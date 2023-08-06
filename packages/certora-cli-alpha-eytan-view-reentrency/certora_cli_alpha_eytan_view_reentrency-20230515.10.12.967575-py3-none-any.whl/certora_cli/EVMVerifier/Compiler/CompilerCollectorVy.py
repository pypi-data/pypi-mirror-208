import itertools
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
import json
import logging
import re
import subprocess
from Crypto.Hash import keccak
from abc import ABC, abstractmethod

from EVMVerifier.Compiler.CompilerCollector import CompilerCollector, CompilerLang, CompilerLangFunc
from Shared.certoraUtils import Singleton
from Shared.certoraUtils import print_failed_to_run

import EVMVerifier.certoraType as CT

ast_logger = logging.getLogger("ast")


class CompilerLangVy(CompilerLang, metaclass=Singleton):
    """
    [CompilerLang] for Vyper.
    """
    _compiler_name: str = "vyper"

    @property
    def name(self) -> str:
        return "Vyper"

    @property
    def compiler_name(self) -> str:
        return self._compiler_name

    @staticmethod
    def normalize_func_hash(func_hash: str) -> str:
        try:
            return hex(int(func_hash, 16))
        except ValueError:
            raise Exception(f'{func_hash} is not convertible to hexadecimal')

    @staticmethod
    def normalize_file_compiler_path_name(file_abs_path: str) -> str:
        if not file_abs_path.startswith('/'):
            return '/' + file_abs_path
        return file_abs_path

    @staticmethod
    def normalize_deployed_bytecode(deployed_bytecode: str) -> str:
        assert deployed_bytecode.startswith("0x"), f'expected {deployed_bytecode} to have hexadecimal prefix'
        return deployed_bytecode[2:]

    @staticmethod
    def get_contract_def_node_ref(contract_file_ast: Dict[int, Any], contract_file: str, contract_name: str) -> \
            int:
        # in vyper, "ContractDefinition" is "Module"
        denormalized_contract_file = contract_file[1:] if contract_file.startswith('/') else contract_file
        contract_def_refs = list(filter(
            lambda node_id: contract_file_ast[node_id].get("ast_type") == "Module" and
            (contract_file_ast[node_id].get("name") == contract_file, contract_file_ast) or
            contract_file_ast[node_id].get("name") == denormalized_contract_file, contract_file_ast))
        assert len(contract_def_refs) != 0, \
            f'Failed to find a "Module" ast node id for the file {contract_file}'
        assert len(contract_def_refs) == 1, f'Found multiple "Module" ast node ids for the same file' \
            f'{contract_file}: {contract_def_refs}'
        return contract_def_refs[0]

    @staticmethod
    def compilation_output_path(sdc_name: str, config_path: Path) -> Path:
        return config_path / f"{sdc_name}"

    # Todo - add this for Vyper too and make it a CompilerLang class method one day
    @staticmethod
    def compilation_error_path(sdc_name: str, config_path: Path) -> Path:
        return config_path / f"{sdc_name}.standard.json.stderr"

    @staticmethod
    def all_compilation_artifacts(sdc_name: str, config_path: Path) -> Set[Path]:
        """
        Returns the set of paths for all files generated after compilation.
        """
        return {CompilerLangVy.compilation_output_path(sdc_name, config_path),
                CompilerLangVy.compilation_error_path(sdc_name, config_path)}

    class VyperType(ABC):
        uniqueId: int = 0

        @classmethod
        def get_unique_id(cls) -> int:
            r = cls.uniqueId
            cls.uniqueId += 1
            return r

        @abstractmethod
        def size_in_bytes(self) -> int:
            pass

        @abstractmethod
        def generate_types_field(self) -> Dict[str, Any]:
            pass

        @abstractmethod
        def get_canonical_vyper_name(self) -> str:
            pass

        @abstractmethod
        def get_used_types(self) -> List[Any]:
            pass

        def resolve_forward_declared_types(self, resolution_dict: Dict[str, Any]) -> Any:
            return self

        @abstractmethod
        def get_certora_type(self, contract_name: str, ref: int) -> CT.Type:
            pass

        @abstractmethod
        def get_storage_type_descriptor(self) -> Dict[str, Any]:
            pass

    class VyperTypeNameReference(VyperType):
        def __init__(self, name: str):
            self.name = name

        def size_in_bytes(self) -> int:
            raise NotImplementedError

        def generate_types_field(self) -> Dict[str, Any]:
            raise NotImplementedError

        def get_canonical_vyper_name(self) -> str:
            return self.name

        def get_used_types(self) -> List[Any]:
            raise NotImplementedError

        def resolve_forward_declared_types(self, resolution_dict: Dict[str, Any]) -> Any:
            if self.name in resolution_dict:
                return resolution_dict[self.name]
            return self

        def get_certora_type(self, contract_name: str, ref: int) -> CT.Type:
            assert False, "can't generate_ct_type for a forward name reference"

        def get_storage_type_descriptor(self) -> Dict[str, Any]:
            assert False, "can't get_storage_type_descriptor for a forward name reference"

    class VyperTypeStaticArray(VyperType):
        def __init__(self, element_type: Any, max_num_elements: int):
            self.element_type = element_type
            self.max_num_elements = max_num_elements

        def size_in_bytes(self) -> int:
            return self.element_type.size_in_bytes() * self.max_num_elements

        def generate_types_field(self) -> Dict[str, Any]:
            return {
                'label': self.get_canonical_vyper_name(),
                'encoding': 'inplace',
                'base': self.element_type.get_canonical_vyper_name(),
                'numberOfBytes': str(self.size_in_bytes())
            }

        def get_canonical_vyper_name(self) -> str:
            return f'{self.element_type.get_canonical_vyper_name()}[{self.max_num_elements}]'

        def resolve_forward_declared_types(self, resolution_dict: Dict[str, Any]) -> Any:
            self.element_type = self.element_type.resolve_forward_declared_types(resolution_dict)
            return self

        def get_used_types(self) -> List[Any]:
            return [self] + [self.element_type]

        def get_certora_type(self, contract_name: str, ref: int) -> CT.Type:
            return CT.ArrayType(self.element_type.get_canonical_vyper_name(),
                                self.element_type.get_certora_type(contract_name, ref),
                                self.max_num_elements,
                                contract_name, ref)

        def get_storage_type_descriptor(self) -> Dict[str, Any]:
            return {
                "type": "StaticArray",
                "staticArrayBaseType": self.element_type.get_storage_type_descriptor(),
                "staticArraySize": f"{self.max_num_elements}",
            }

    class VyperTypeStruct(VyperType):
        def __init__(self, name: str, members: List[Tuple[str, Any]]):
            self.name = name
            self.members = members

        def size_in_bytes(self) -> int:
            return sum([f[1].size_in_bytes() for f in self.members])

        def generate_types_field(self) -> Dict[str, Any]:
            bytes_so_far_rounded_up = 0
            slots = {}
            for n, t in self.members:
                slots.update({n: bytes_so_far_rounded_up // 32})
                bytes_so_far_rounded_up += (t.size_in_bytes() + 31) & ~31
            members_field = [
                {
                    'label': n,
                    'slot': str(slots[n]),
                    'offset': 0,
                    'type': t.get_canonical_vyper_name()
                }
                for (n, t) in self.members]
            return {
                'label': self.get_canonical_vyper_name(),
                'encoding': 'inplace',
                'members': members_field,
                'numberOfBytes': str(self.size_in_bytes())
            }

        def get_canonical_vyper_name(self) -> str:
            return self.name

        def resolve_forward_declared_types(self, resolution_dict: Dict[str, Any]) -> Any:
            self.members = [(f[0], f[1].resolve_forward_declared_types(resolution_dict)) for f in self.members]
            return self

        def get_used_types(self) -> List[Any]:
            return [self] + list(itertools.chain.from_iterable([t.get_used_types() for _, t in self.members]))

        def get_certora_type(self, contract_name: str, ref: int) -> CT.Type:
            members = \
                [CT.StructType.StructMember(x[0], x[1].get_certora_type(contract_name, ref)) for x in self.members]
            return CT.StructType(self.name, "struct " + self.name, self.name, members, contract_name, ref, None)

        def get_storage_type_descriptor(self) -> Dict[str, Any]:
            return {
                "type": "UserDefinedStruct",
                "structName": self.name,
                "structMembers": [{"name": x[0], "type": x[1].get_storage_type_descriptor()} for x in self.members],
                "containingContract": None,
                "astId": 0,
                "canonicalId": str(0)
            }

    class VyperTypeDynArray(VyperTypeStruct):
        def __init__(self, element_type: Any, max_num_elements: int):
            self.count_type = CompilerLangVy.VyperTypeBoundedInteger(
                CompilerLangVy.primitive_types['uint256'], 1, max_num_elements)
            self.array_type = CompilerLangVy.VyperTypeStaticArray(element_type, int(max_num_elements))
            name = f'DynArray[{element_type.get_canonical_vyper_name()}, {max_num_elements}]'
            super().__init__(name, [('count', self.count_type), ('data', self.array_type)])

    class VyperTypeString(VyperTypeDynArray):
        def __init__(self, max_num_elements: int):
            super().__init__(CompilerLangVy.primitive_types['byte'], max_num_elements)

        def get_canonical_vyper_name(self) -> str:
            return 'String[' + str(self.array_type.max_num_elements) + ']'

    class VyperTypeHashMap(VyperType):
        def __init__(self, key_type: Any, value_type: Any):
            self.key_type = key_type
            self.value_type = value_type

        def size_in_bytes(self) -> int:
            return 32

        def generate_types_field(self) -> Dict[str, Any]:
            return {
                'label': self.get_canonical_vyper_name(),
                'encoding': 'mapping',
                'key': self.key_type.get_canonical_vyper_name(),
                'value': self.value_type.get_canonical_vyper_name(),
                'numberOfBytes': '32'
            }

        def get_canonical_vyper_name(self) -> str:
            return 'HashMap[' + self.key_type.get_canonical_vyper_name() + ', ' + \
                self.value_type.get_canonical_vyper_name() + ']'

        def resolve_forward_declared_types(self, resolution_dict: Dict[str, Any]) -> Any:
            self.key_type = self.key_type.resolve_forward_declared_types(resolution_dict)
            self.value_type = self.value_type.resolve_forward_declared_types(resolution_dict)
            return self

        def get_used_types(self) -> List[Any]:
            return [self] + [self.key_type] + [self.value_type]

        def get_certora_type(self, contract_name: str, ref: int) -> CT.Type:
            in_type = self.key_type.get_certora_type(contract_name, ref)
            out_type = self.value_type.get_certora_type(contract_name, ref)
            return CT.MappingType(out_type.type_string, in_type, out_type, contract_name, ref)

        def get_storage_type_descriptor(self) -> Dict[str, Any]:
            return {
                "type": "Mapping",
                "mappingKeyType": self.key_type.get_storage_type_descriptor(),
                "mappingValueType": self.value_type.get_storage_type_descriptor()
            }

    class VyperTypePrimitive(VyperType):
        def __init__(self, name: str, size: int):
            self.name = name
            self.size = size

        def size_in_bytes(self) -> int:
            return self.size

        def generate_types_field(self) -> Dict[str, Any]:
            return {
                'label': self.get_canonical_vyper_name(),
                'encoding': 'inplace',
                'numberOfBytes': str(self.size_in_bytes())
            }

        def get_canonical_vyper_name(self) -> str:
            return self.name

        def get_used_types(self) -> List[Any]:
            return [self]

        def get_certora_type(self, contract_name: str, ref: int) -> CT.Type:
            if self.name not in CT.PrimitiveType.allowed_primitive_type_names:
                return CT.PrimitiveType('uint256', 'uint256')
            else:
                return CT.PrimitiveType(self.name, self.name)

        def get_storage_type_descriptor(self) -> Dict[str, Any]:
            return {"primitiveName": self.get_canonical_vyper_name(),
                    "type": "Primitive"}

    class VyperTypePrimitiveAlias(VyperTypePrimitive):
        def __init__(self, basetype: Any, name: str):
            super().__init__(name, basetype.size)
            self.basetype = basetype

        def get_storage_type_descriptor(self) -> Dict[str, Any]:
            return {
                "type": "UserDefinedValueType",
                "valueTypeName": self.name,
                "containingContract": None,
                "valueTypeAliasedName": self.basetype.get_storage_type_descriptor(),
                "astId": 0,
                "canonicalId": str(0)
            }

    class VyperTypeBoundedInteger(VyperTypePrimitiveAlias):
        def __init__(self, basetype: Any, lower_bound: int, upper_bound: int):
            super().__init__(basetype, f'{basetype.get_canonical_vyper_name()}_bounded_{lower_bound}_{upper_bound}')
            self.lower_bound = lower_bound
            self.upper_bound = upper_bound

        def generate_types_field(self) -> Dict[str, Any]:
            return {
                'label': self.get_canonical_vyper_name(),
                'encoding': 'inplace',
                'numberOfBytes': str(self.size_in_bytes()),
                'lowerBound': str(self.lower_bound),
                'upperBound': str(self.upper_bound)
            }

    primitive_types = {
        'address': VyperTypePrimitive('address', 32),
        'bool': VyperTypePrimitive('bool', 1),
        'byte': VyperTypePrimitive('byte', 1),
        'decimal': VyperTypePrimitive('decimal', 32),
        'int8': VyperTypePrimitive('int8', 1),
        'int16': VyperTypePrimitive('int16', 2),
        'int32': VyperTypePrimitive('int32', 4),
        'int64': VyperTypePrimitive('int64', 8),
        'int128': VyperTypePrimitive('int128', 16),
        'int256': VyperTypePrimitive('int256', 32),
        'uint8': VyperTypePrimitive('uint8', 1),
        'uint16': VyperTypePrimitive('uint16', 2),
        'uint32': VyperTypePrimitive('uint32', 4),
        'uint64': VyperTypePrimitive('uint64', 8),
        'uint128': VyperTypePrimitive('uint128', 16),
        'uint256': VyperTypePrimitive('uint256', 32),
        'nonreentrant lock': VyperTypePrimitive('nonreentrant lock', 32),
        'ERC20': VyperTypePrimitive('ERC20', 32),
        'ERC721': VyperTypePrimitive('ERC721', 32),
        'bytes4': VyperTypePrimitive('bytes4', 32 + 4),
        'bytes8': VyperTypePrimitive('bytes8', 32 + 8),
        'bytes16': VyperTypePrimitive('bytes16', 32 + 16),
        'bytes32': VyperTypePrimitive('bytes32', 32 + 32)
    }

    @staticmethod
    def extract_type_from_subscript_node(ast_subscript_node: Dict[str, Any],
                                         named_constants: Dict[str, int]) -> VyperType:
        value_id = ast_subscript_node['value']['id']
        if value_id == 'String':
            max_bytes = ast_subscript_node['slice']['value']['value']
            return CompilerLangVy.VyperTypeString(max_bytes)
        elif value_id == 'DynArray':
            elem_type = CompilerLangVy.extract_type_from_type_annotation_node(
                ast_subscript_node['slice']['value']['elements'][0], named_constants)
            max_elements = ast_subscript_node['slice']['value']['elements'][1]['value']
            if max_elements in named_constants:
                return CompilerLangVy.VyperTypeDynArray(elem_type, named_constants[max_elements])
            else:
                return CompilerLangVy.VyperTypeDynArray(elem_type, max_elements)
        elif value_id == 'HashMap':
            elements_node = ast_subscript_node['slice']['value']['elements']
            key_type = CompilerLangVy.extract_type_from_type_annotation_node(elements_node[0], named_constants)
            value_type = CompilerLangVy.extract_type_from_type_annotation_node(elements_node[1], named_constants)
            return CompilerLangVy.VyperTypeHashMap(key_type, value_type)
        else:  # StaticArray
            key_type = CompilerLangVy.primitive_types[value_id] if value_id in CompilerLangVy.primitive_types \
                else CompilerLangVy.extract_type_from_type_annotation_node(value_id, named_constants)
            max_elements_node = ast_subscript_node['slice']['value']
            if 'id' in max_elements_node and max_elements_node['id'] in named_constants:
                return CompilerLangVy.VyperTypeStaticArray(key_type, named_constants[max_elements_node['id']])
            else:
                return CompilerLangVy.VyperTypeStaticArray(key_type, max_elements_node['value'])

    @staticmethod
    def extract_type_from_type_annotation_node(ast_type_annotation: Dict[str, Any],
                                               named_constants: Dict[str, int]) -> VyperType:
        if ast_type_annotation['ast_type'] == 'Subscript':
            return CompilerLangVy.extract_type_from_subscript_node(ast_type_annotation, named_constants)
        elif ast_type_annotation['id'] in CompilerLangVy.primitive_types:
            return CompilerLangVy.primitive_types[ast_type_annotation['id']]
        elif 'value' in ast_type_annotation:
            value_id = ast_type_annotation['value']['id']
            return CompilerLangVy.VyperTypeNameReference(value_id)
        else:
            return CompilerLangVy.VyperTypeNameReference(ast_type_annotation['id'])

    @staticmethod
    def extract_type_from_variable_decl(ast_vardecl_node: Dict[str, Any],
                                        named_constants: Dict[str, int]) -> VyperType:
        return CompilerLangVy.extract_type_from_type_annotation_node(ast_vardecl_node['annotation'], named_constants)

    @staticmethod
    def extract_type_from_struct_def(ast_structdef_node: Dict[str, Any],
                                     named_constants: Dict[str, int]) -> VyperType:
        fields = [(n['target']['id'], CompilerLangVy.extract_type_from_type_annotation_node(n['annotation'],
                                                                                            named_constants))
                  for n in ast_structdef_node['body']]
        return CompilerLangVy.VyperTypeStruct(ast_structdef_node['name'], fields)

    @staticmethod
    def resolve_extracted_types(extracted_types: List[VyperType]) -> List[VyperType]:
        real_types = [t for t in extracted_types if not isinstance(t, CompilerLangVy.VyperTypeNameReference)]
        name_resolution_dict = {t.get_canonical_vyper_name(): t for t in real_types}
        return [t.resolve_forward_declared_types(name_resolution_dict) for t in real_types]

    @staticmethod
    def extract_ast_types_and_public_vardecls(ast_body_nodes: Dict[int, Dict[str, Any]]) -> \
            Tuple[List[VyperType], Dict[str, VyperType]]:
        def resolve_vardecl_types(
                vardecls: Dict[str, CompilerLangVy.VyperType],
                resolved_types: List[CompilerLangVy.VyperType]) -> Dict[str, CompilerLangVy.VyperType]:
            name_resolution_dict = {t.get_canonical_vyper_name(): t for t in resolved_types}
            return {x: vardecls[x].resolve_forward_declared_types(name_resolution_dict) for x in vardecls}

        result_types = []
        public_vardecls = {}
        named_constants: Dict[str, int] = {}
        for ast_node in ast_body_nodes.values():
            if ast_node['ast_type'] == 'VariableDecl':
                decltype = CompilerLangVy.extract_type_from_variable_decl(ast_node, named_constants)
                result_types.append(decltype)
                if ast_node['is_public']:
                    public_vardecls[ast_node['target']['id']] = decltype
                if ast_node['is_constant'] and (ast_node['value'] is not None) and \
                        (ast_node['value']['ast_type'] == 'Int'):
                    named_constants.update({ast_node['target']['id']: int(ast_node['value']['value'])})
            elif ast_node['ast_type'] == 'StructDef':
                result_types.append(CompilerLangVy.extract_type_from_struct_def(ast_node, named_constants))
            elif ast_node['ast_type'] == 'Import':
                result_types.append(CompilerLangVy.VyperTypePrimitiveAlias(CompilerLangVy.primitive_types['address'],
                                                                           ast_node['name']))
        resolved_result_types = CompilerLangVy.resolve_extracted_types(result_types)

        return resolved_result_types, resolve_vardecl_types(public_vardecls, resolved_result_types)

    @staticmethod
    def collect_storage_layout_info(file_abs_path: str,
                                    config_path: Path,
                                    compiler_cmd: str,
                                    data: Dict[str, Any]) -> Dict[str, Any]:
        storage_layout_output_file_name = f'{config_path}.storage.layout'
        storage_layout_stdout_name = storage_layout_output_file_name + '.stdout'
        storage_layout_stderr_name = storage_layout_output_file_name + '.stderr'
        args = [compiler_cmd, '-f', 'layout', '-o', storage_layout_output_file_name, file_abs_path]
        with Path(storage_layout_stdout_name).open('w+') as stdout:
            with Path(storage_layout_stderr_name).open('w+') as stderr:
                try:
                    subprocess.run(args, stdout=stdout, stderr=stderr)
                    with Path(storage_layout_output_file_name).open('r') as output_file:
                        storage_layout_dict = json.load(output_file)
                except Exception as e:
                    print(f'Error: {e}')
                    print_failed_to_run(compiler_cmd)
                    raise
        ast_output_file_name = f'{config_path}.ast'
        ast_stdout_name = storage_layout_output_file_name + '.stdout'
        ast_stderr_name = storage_layout_output_file_name + '.stderr'
        args = [compiler_cmd, '-f', 'ast', '-o', ast_output_file_name, file_abs_path]
        with Path(ast_stdout_name).open('w+') as stdout:
            with Path(ast_stderr_name).open('w+') as stderr:
                try:
                    subprocess.run(args, stdout=stdout, stderr=stderr)
                    with Path(ast_output_file_name).open('r') as output_file:
                        ast_dict = json.load(output_file)
                except Exception as e:
                    print(f'Error: {e}')
                    print_failed_to_run(compiler_cmd)
                    raise

        extracted_types, _ = CompilerLangVy.extract_ast_types_and_public_vardecls(
            {x['node_id']: x for x in ast_dict['ast']['body']}
        )
        all_used_types = list(itertools.chain.from_iterable([e.get_used_types() for e in extracted_types])) + \
            list(CompilerLangVy.primitive_types.values())
        type_descriptors_by_name = {i.get_canonical_vyper_name(): i.get_storage_type_descriptor()
                                    for i in all_used_types}
        types_field = {i.get_canonical_vyper_name(): i.generate_types_field() for i in all_used_types}
        storage_field = [{
            'label': v,
            'slot': str(storage_layout_dict['storage_layout'][v]['slot']),
            'offset': 0,
            'type': storage_layout_dict['storage_layout'][v]['type'],
            'descriptor': type_descriptors_by_name[storage_layout_dict['storage_layout'][v]['type']]
        } for v in storage_layout_dict['storage_layout'].keys()]

        contract_name = list(data['contracts'][file_abs_path].keys())[0]
        data['contracts'][file_abs_path][contract_name]['storageLayout'] = {
            'storage': storage_field,
            'types': types_field,
            'storageHashArgsReversed': True
        }
        data['contracts'][file_abs_path][contract_name]['storageHashArgsReversed'] = True
        return data

    @staticmethod
    def get_supports_imports() -> bool:
        return False

    @staticmethod
    def collect_source_type_descriptions_and_funcs(asts: Dict[str, Dict[str, Dict[int, Any]]],
                                                   data: Dict[str, Any],
                                                   contract_file: str,
                                                   contract_name: str,
                                                   build_arg_contract_file: str) -> \
            Tuple[List[CT.Type], List[CompilerLangFunc]]:
        parsed_types = {}  # type: Dict[str, CT.Type]

        def get_abi_type_by_name(type_name: str) -> CT.Type:
            if type_name == "bytes":
                return CT.PackedBytes()
            elif type_name == "string":
                return CT.StringType()
            elif type_name in CT.PrimitiveType.allowed_primitive_type_names:
                return CT.PrimitiveType(type_name, type_name)
            elif type_name in parsed_types:
                return parsed_types[type_name]
            else:
                ast_logger.fatal(f"unexpected AST Type Name Node: {type_name}")
                assert False, "get_type_by_name failed to resolve type name"

        def collect_funcs(getter_vars: Dict[str, CT.MappingType]) -> List[CompilerLangFunc]:
            def collect_array_type_from_abi_rec(type_str: str, dims: List[int]) -> str:
                outer_dim = re.findall(r"\[\d*]$", type_str)
                if outer_dim:
                    type_rstrip_dim = re.sub(r"\[\d*]$", '', type_str)
                    if len(outer_dim[0]) == 2:
                        dims.append(-1)  # dynamic array
                    else:
                        assert len(outer_dim[0]) > 2, f"Expected to find a fixed-size array, but found {type_str}"
                        dims.append(int(re.findall(r"\d+", outer_dim[0])[0]))
                    return collect_array_type_from_abi_rec(type_rstrip_dim, dims)
                return type_str

            # Returns (list of array dimensions' lengths, the base type of the array)
            def collect_array_type_from_abi(type_str: str) -> Tuple[List[int], str]:
                dims = []  # type: List[int]
                base_type = collect_array_type_from_abi_rec(type_str, dims)
                return dims, base_type

            def cons_array_type(base_ct_type: CT.Type, dims: List[int]) -> CT.Type:
                if dims:
                    tn = base_ct_type.name + ''.join(['[' + str(x) + ']' for x in dims])
                    return CT.ArrayType(
                        type_string=tn,
                        elementType=cons_array_type(base_ct_type, dims[1:]),
                        length=dims[0],
                        contract_name=contract_name,
                        reference=0)  # We have no useful reference number because this is used to extract from abi_data
                else:
                    return base_ct_type

            # Gets the CT.TypeInstance of a function parameter (either input or output) from the ABI
            def get_solidity_type_from_abi(abi_param_entry: Dict[str, Any]) -> CT.TypeInstance:
                assert "type" in abi_param_entry, f"Invalid ABI function parameter entry: {abi_param_entry}"
                array_dims, base_type = collect_array_type_from_abi(abi_param_entry["type"])

                internal_type_exists = "internalType" in abi_param_entry
                if internal_type_exists:
                    array_dims_internal, internal_base_type = collect_array_type_from_abi(
                        abi_param_entry["internalType"])
                    assert array_dims_internal == array_dims
                    user_defined_type = CT.TypeInstance(get_abi_type_by_name(internal_base_type))
                else:
                    base_ct_type = get_abi_type_by_name(base_type)
                    user_defined_type = CT.TypeInstance(cons_array_type(base_ct_type, array_dims))

                return user_defined_type

            def compute_signature(name: str, args: List[CT.TypeInstance], signature_getter: Any) -> str:
                return name + "(" + ",".join([signature_getter(x) for x in args]) + ")"

            def get_function_selector(f_entry: Dict[str, Any], f_name: str,
                                      input_types: List[CT.TypeInstance], is_lib: bool) -> str:
                if "functionSelector" in f_entry:
                    return f_entry["functionSelector"]

                f_base = compute_signature(f_name, input_types, lambda x: x.get_abi_canonical_string(is_lib))

                assert f_base in data["evm"]["methodIdentifiers"], \
                    f"Was about to compute the sighash of {f_name} based on the signature {f_base}.\n" \
                    f"Expected this signature to appear in \"methodIdentifiers\"."

                f_hash = keccak.new(digest_bits=256)
                f_hash.update(str.encode(f_base))

                result = f_hash.hexdigest()[0:8]
                expected_result = data["evm"]["methodIdentifiers"][f_base]

                assert expected_result == CompilerLangVy.normalize_func_hash(result), \
                    f"Computed the sighash {result} of {f_name} " \
                    f"based on a (presumably) correct signature ({f_base}), " \
                    f"but got an incorrect result. Expected result: {expected_result}"

                return result

            def flatten_getter_domain(in_type: CT.Type) -> List[CT.Type]:
                if isinstance(in_type, CT.MappingType):
                    return [in_type.domain] + flatten_getter_domain(in_type.codomain)
                else:
                    return []

            funcs = list()
            base_contract_files = [(contract_file, contract_name, False)]  # type: List[Tuple[str, str, bool]]
            ast_logger.debug(
                f"build arg contract file {build_arg_contract_file} and base contract files {base_contract_files}")
            c_is_lib = False
            for c_file, c_name, c_is_lib in base_contract_files:
                for abi_data in data["abi"]:
                    if abi_data["type"] == "function":
                        name = abi_data["name"]
                        if name in getter_vars:
                            solidity_type_args = [CT.TypeInstance(x) for x in flatten_getter_domain(getter_vars[name])]
                            solidity_type_outs = [CT.TypeInstance(getter_vars[name].codomain)]
                        else:
                            params = [p for p in abi_data["inputs"]]
                            out_params = [p for p in abi_data["outputs"]]
                            solidity_type_args = [get_solidity_type_from_abi(p) for p in params]
                            solidity_type_outs = [get_solidity_type_from_abi(p) for p in out_params]

                        func_selector = get_function_selector({}, name, solidity_type_args, True)
                        state_mutability = abi_data["stateMutability"]

                        funcs.append(
                            CompilerLangFunc(
                                name=name,
                                fullargs=solidity_type_args,
                                paramnames=[],
                                returns=solidity_type_outs,
                                sighash=func_selector,
                                notpayable=state_mutability in ["nonpayable", "view", "pure"],
                                fromlib=True,
                                isconstructor=False,
                                statemutability=state_mutability,
                                implemented=True,
                                overrides=False,
                                # according to Solidity docs, getter functions have external visibility
                                visibility="external",
                                ast_id=None
                            )
                        )

            # TODO: merge this and the implementation from certoraBuild
            def verify_collected_all_abi_funcs(
                abi_funcs: List[Dict[str, Any]], collected_funcs: List[CompilerLangFunc], is_lib: bool
            ) -> None:
                for fabi in abi_funcs:
                    # check that we collected at least one function with the same name as the ABI function
                    fs = [f for f in collected_funcs if f.name == fabi["name"]]
                    assert fs, f"{fabi['name']} is in the ABI but wasn't collected"

                    # check that at least one of the functions has the correct number of arguments
                    fs = [f for f in fs if len(f.fullArgs) == len(fabi["inputs"])]
                    assert fs, \
                        f"no collected func with name {fabi['name']} has the same \
                                amount of arguments as the ABI function of that name"

                    def compareTypes(ct_type: CT.Type, i: Dict[str, Any]) -> bool:
                        # check that there is exactly one collected function with the same argument types
                        # as the ABI function
                        def get_type(i: Dict[str, Any]) -> bool:
                            return i["internalType"] if "internalType" in i else i["type"]

                        solc_type = get_type(i)
                        ret = ct_type.type_string == solc_type
                        if not ret:
                            # The representation in the abi changed at some point, so hack up something that will pass
                            # for both older and newer solc versions
                            if isinstance(ct_type, CT.ContractType):
                                ret = solc_type == "address"
                            elif isinstance(ct_type, CT.StructType):
                                ret = solc_type == "tuple"
                        return ret

                    fs = [f for f in fs if all(compareTypes(a.type, i)
                                               for a, i in zip(f.fullArgs, fabi["inputs"]))]
                    assert fs, \
                        f"no collected func with name {fabi['name']} has the same \
                                types of arguments as the ABI function of that name"

                    if len(fs) > 1:
                        assert is_lib, "Collected too many functions with the same ABI specification (non-library)"
                        # if a function is in a library and its first argument is of storage, then it’s not ABI.
                        fs = [f for f in fs if f.fullArgs[0].location != CT.TypeLocation.STORAGE]
                        assert len(fs) == 1, "Collected too many (library) functions with the same ABI specification"

                    # At this point we are certain we have just one candidate. Let's do some sanity checks also
                    # on the return values
                    f = fs[0]
                    assert len(f.returns) == len(fabi["outputs"]), \
                        f"function collected for {fabi['name']} has the wrong number of return values"
                    assert all(compareTypes(a.type, i) for a, i in zip(f.returns, fabi["outputs"])), \
                        f"function collected for {fabi['name']} has the wrong types of return values"

            verify_collected_all_abi_funcs(
                [f for f in data["abi"] if f["type"] == "function"],
                [f for f in funcs if f.visibility in ("external", "public") and f.name != "constructor"],
                c_is_lib
            )

            return funcs

        vyper_types, public_vardecls = \
            CompilerLangVy.extract_ast_types_and_public_vardecls(asts[build_arg_contract_file][contract_file])
        ct_types = [x.get_certora_type(contract_name, 0) for x in vyper_types]
        getter_vars_list = [(v, public_vardecls[v].get_certora_type(contract_name, 0))
                            for v in public_vardecls if isinstance(public_vardecls[v], CompilerLangVy.VyperTypeHashMap)]
        getter_vars = {k: v for (k, v) in getter_vars_list if isinstance(v, CT.MappingType)}
        parsed_types = {x.name: x for x in ct_types}
        return list(parsed_types.values()), collect_funcs(getter_vars)


class CompilerCollectorVy(CompilerCollector):

    @property
    def compiler_name(self) -> str:
        return self.smart_contract_lang.compiler_name

    @property
    def smart_contract_lang(self) -> CompilerLangVy:
        return CompilerLangVy()

    @property
    def compiler_version(self) -> str:
        return "vyper"  # TODO implement to return a valid version
