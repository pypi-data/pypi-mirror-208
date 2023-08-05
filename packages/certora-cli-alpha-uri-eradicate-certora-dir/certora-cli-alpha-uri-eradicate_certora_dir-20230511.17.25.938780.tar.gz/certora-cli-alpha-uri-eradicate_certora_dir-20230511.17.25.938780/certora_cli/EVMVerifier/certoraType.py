from typing import Any, Dict, List, Optional, Callable

from EVMVerifier.certoraNodeFilters import NodeFilters
from abc import ABC, abstractmethod
from enum import Enum
import logging

ast_logger = logging.getLogger("ast")


class Type(ABC):
    def __init__(self, name: str, type_string: str):
        """
        not every instance of a type needs to have a name. TODO
        @param type_string: solidity associates a type_string with every type
        """
        self.name = name
        self.type_string = type_string

    # I'm not messing with __eq__ right now
    def matches(self, other: Any) -> bool:
        if not isinstance(other, Type):
            # don't attempt to compare against unrelated types
            return NotImplemented
        if isinstance(other, UserDefinedType) and isinstance(self, UserDefinedType):
            return self.canonical_name == other.canonical_name
        elif isinstance(other, MappingType) and isinstance(self, MappingType):
            return self.type_string == other.type_string
        elif isinstance(other, ArrayType) and isinstance(self, ArrayType):
            return self.type_string == other.type_string
        else:
            # hope I got all cases, luv2python
            return self.type_string == other.type_string

    @abstractmethod
    def as_dict(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_abi_canonical_string(self, is_library: bool) -> str:
        ...

    @abstractmethod
    def get_source_str(self) -> str:
        ...

    def default_location(self) -> 'TypeLocation':
        return TypeLocation.STACK

    @staticmethod
    def from_primitive_name(name: str) -> 'Type':
        return PrimitiveType(name, name)

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]],
                      lookup_containing_file: Callable[[int], Optional[str]], def_node: Dict[str, Any]) -> 'Type':
        if NodeFilters.is_enum_definition(def_node):
            ret = EnumType.from_def_node(lookup_reference, lookup_containing_file, def_node)  # type: Type
        elif NodeFilters.is_struct_definition(def_node):
            ret = StructType.from_def_node(lookup_reference, lookup_containing_file, def_node)
        elif NodeFilters.is_user_defined_value_type_definition(def_node):
            ret = UserDefinedValueType.from_def_node(lookup_reference, lookup_containing_file, def_node)
        elif NodeFilters.is_contract_definition(def_node):
            ret = ContractType.from_def_node(lookup_reference, lookup_containing_file, def_node)
        else:
            ast_logger.fatal(f"unexpected AST Type Definition Node {def_node}")
        return ret

    @staticmethod
    def from_type_name_node(lookup_reference: Callable[[int], Dict[str, Any]],
                            lookup_containing_file: Callable[[int], Optional[str]],
                            type_name: Dict[str, Any]) -> 'Type':
        node_type = type_name["nodeType"]
        if node_type == "ElementaryTypeName":
            if type_name["name"] in PrimitiveType.allowed_primitive_type_names:
                ret = PrimitiveType(type_name["name"], type_name["typeDescriptions"]["typeString"])  # type: Type
            else:
                ret = Type.get_non_primitive_elementary_type(type_name)
        elif node_type == "FunctionTypeName":
            # TODO what to do with FunctionTypes :[]
            name = type_name["typeDescriptions"]["typeString"]
            ret = FunctionType(name)
        elif node_type == "UserDefinedTypeName":
            ret = UserDefinedType.from_def_node(lookup_reference, lookup_containing_file, lookup_reference(
                type_name["referencedDeclaration"]))
        elif node_type == "Mapping":
            ret = MappingType.from_def_node(lookup_reference, lookup_containing_file, type_name)
        elif node_type == "ArrayTypeName":
            ret = ArrayType.from_def_node(lookup_reference, lookup_containing_file, type_name)
        else:
            ast_logger.fatal(f"unexpected AST Type Name Node: {type_name}")
        return ret

    @staticmethod
    def get_non_primitive_elementary_type(type_name: Dict[str, Any]) -> 'Type':
        name = type_name["name"]
        if name == "bytes":
            ret = PackedBytes()
        elif name == "string":
            return StringType()
        else:
            ast_logger.fatal(f"unexpected AST Type Name Node: {name}")
        return ret


class PrimitiveType(Type):
    allowed_primitive_type_names = {
        "uint", "uint8", "uint16", "uint24", "uint32", "uint40", "uint48", "uint56", "uint64", "uint72", "uint80",
        "uint88", "uint96", "uint104", "uint112", "uint120", "uint128", "uint136", "uint144", "uint152", "uint160",
        "uint168", "uint176", "uint184", "uint192", "uint200", "uint208", "uint216", "uint224", "uint232", "uint240",
        "uint248", "uint256",
        "int", "int8", "int16", "int24", "int32", "int40", "int48", "int56", "int64", "int72", "int80",
        "int88", "int96", "int104", "int112", "int120", "int128", "int136", "int144", "int152", "int160",
        "int168", "int176", "int184", "int192", "int200", "int208", "int216", "int224", "int232", "int240",
        "int248", "int256",
        "bytes1", "bytes2", "bytes3", "bytes4", "bytes5", "bytes6", "bytes7", "bytes8", "bytes9", "bytes10", "bytes11",
        "bytes12", "bytes13", "bytes14", "bytes15", "bytes16", "bytes17", "bytes18", "bytes19", "bytes20", "bytes21",
        "bytes22", "bytes23", "bytes24", "bytes25", "bytes26", "bytes27", "bytes28", "bytes29", "bytes30", "bytes31",
        "bytes32",
        "byte",
        "bool",
        "address",
    }

    # I am not 100% convinced this is the right spot for this canonicalizing (perhaps in kotlin deserialization) but
    # I do like that everything is "cleaned" before the jar gets its hands on this information
    @staticmethod
    def canonical_primitive_name(name: str) -> str:
        if name == "uint":
            return "uint256"
        elif name == "int":
            return "int256"
        else:
            return name

    def __init__(self, name: str, type_string: str):
        if name not in self.allowed_primitive_type_names:
            raise Exception(f'bad primitive name {name}')
        canonical_name = PrimitiveType.canonical_primitive_name(name)
        Type.__init__(self, canonical_name, type_string)

    def as_dict(self) -> Dict[str, Any]:
        return {"primitiveName": self.name,
                "type": "Primitive"}

    def get_abi_canonical_string(self, is_library: bool) -> str:
        return PrimitiveType.canonical_primitive_name(self.name)

    def get_source_str(self) -> str:
        return self.name


class StringType(Type):
    def __init__(self) -> None:
        Type.__init__(self, "string", "string")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "StringType",
        }

    def default_location(self) -> 'TypeLocation':
        return TypeLocation.MEMORY

    def get_abi_canonical_string(self, is_library: bool) -> str:
        return "string"

    def get_source_str(self) -> str:
        return "string"

class PackedBytes(Type):
    def __init__(self) -> None:
        Type.__init__(self, "bytes", "bytes")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "PackedBytes",
        }

    def default_location(self) -> 'TypeLocation':
        return TypeLocation.MEMORY

    def get_abi_canonical_string(self, is_library: bool) -> str:
        return "bytes"

    def get_source_str(self) -> str:
        return "bytes"

class MappingType(Type):
    def __init__(self, type_string: str, domain: Type, codomain: Type, contract_name: str, reference: int):
        Type.__init__(self, f"mapping({domain.name} => {codomain.name})", type_string)
        self.domain = domain
        self.codomain = codomain
        self.contract_name = contract_name
        self.reference = reference

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]],
                      lookup_containing_file: Callable[[int], Optional[str]],
                      def_node: Dict[str, Any]) -> 'MappingType':
        domain = Type.from_type_name_node(lookup_reference, lookup_containing_file,
                                          def_node["keyType"])
        codomain = Type.from_type_name_node(lookup_reference, lookup_containing_file,
                                            def_node["valueType"])
        type_string = def_node["typeDescriptions"]["typeString"]
        return MappingType(
            type_string=type_string,
            domain=domain,
            codomain=codomain,
            contract_name=def_node.get(NodeFilters.CERTORA_CONTRACT_NAME(), None),
            reference=def_node["id"],
        )

    def default_location(self) -> 'TypeLocation':
        return TypeLocation.STORAGE

    def get_abi_canonical_string(self, is_library: bool) -> str:
        return f"mapping({self.domain.get_abi_canonical_string(is_library)} => \
            {self.codomain.get_abi_canonical_string(is_library)})"

    def get_source_str(self) -> str:
        return f"mapping({self.domain.get_source_str()} => {self.codomain.get_source_str()})"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "Mapping",
            "mappingKeyType": self.domain.as_dict(),
            "mappingValueType": self.codomain.as_dict()
        }


class ArrayType(Type):
    def __init__(self, type_string: str, elementType: Type, length: Optional[int], contract_name: Optional[str],
                 reference: int):
        Type.__init__(self, type_string, type_string)
        self.elementType = elementType
        self.length = length  # a length of None indicates a dynamic array
        self.contract_name = contract_name
        self.reference = reference

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]],
                      lookup_containing_file: Callable[[int], Optional[str]],
                      def_node: Dict[str, Any]) -> 'ArrayType':
        type_string = def_node["typeDescriptions"]["typeString"]
        element_type = Type.from_type_name_node(lookup_reference, lookup_containing_file,
                                                def_node["baseType"])
        if "length" in def_node.keys() and def_node["length"] is not None:
            length_object = def_node["length"]
            if "value" in length_object.keys():
                length = int(length_object["value"], 10)  # type: Optional[int]
            else:
                """
                This happens if we have something like:
                uint256 internal constant TREE_DEPTH = 32;

                struct Tree {
                    bytes32[TREE_DEPTH] branch;
                    uint256 count;
                }

                I guess we could resolve TREE_DEPTH, but taking a more straight forward approach now
                """
                length = None
        else:
            length = None
        return ArrayType(
            type_string=type_string,
            elementType=element_type,
            length=length,
            contract_name=def_node.get(NodeFilters.CERTORA_CONTRACT_NAME(), None),
            reference=def_node["id"],
        )

    def as_dict(self) -> Dict[str, Any]:
        if self.is_static_array():
            return {
                "type": "StaticArray",
                "staticArrayBaseType": self.elementType.as_dict(),
                "staticArraySize": f"{self.length}",
            }
        else:
            return {
                "type": "Array",
                "dynamicArrayBaseType": self.elementType.as_dict(),
            }

    def is_static_array(self) -> bool:
        return self.length is not None

    def default_location(self) -> 'TypeLocation':
        return TypeLocation.MEMORY

    def get_abi_canonical_string(self, is_library: bool) -> str:
        return self.elementType.get_abi_canonical_string(is_library) + \
            f"[{self.length if self.is_static_array() else ''}]"

    def get_source_str(self) -> str:
        return self.elementType.get_source_str() + \
            f"[{self.length if self.is_static_array() else ''}]"


class UserDefinedType(Type):
    # TODO: what should we do if file is None? we may want to not let file be optional and error if we can't get it
    def __init__(self, name: str, type_string: str, canonical_name: str, contract_name: str, reference: int,
                 file: Optional[str]):
        Type.__init__(self, name, type_string)
        self.canonical_name = canonical_name
        self.contract_name = contract_name
        self.reference = reference
        self.canonical_id = f"{file}|{canonical_name}"

    @abstractmethod
    def as_dict(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_abi_canonical_string(self, is_library: bool) -> str:
        ...

    @abstractmethod
    def get_source_str(self) -> str:
        ...


class EnumType(UserDefinedType):
    def __init__(self, name: str, type_string: str, canonical_name: str, members: List[str], contract_name: str,
                 reference: int, file: Optional[str]):
        UserDefinedType.__init__(self, name, type_string, canonical_name, contract_name, reference, file)
        self.members = tuple(members)

    @staticmethod
    def get_type_string_from_def_node(def_node: Dict[str, Any]) -> str:
        if "typeDescriptions" in def_node.keys():
            return def_node["typeDescriptions"]["typeString"]  # was'nt included in solidity 4ish
        else:
            canonical_name = def_node["canonicalName"]
            return f"enum {canonical_name}"

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]],
                      lookup_containing_file: Callable[[int], Optional[str]],
                      def_node: Dict[str, Any], _: Optional[str] = None) -> 'EnumType':
        members = map(
            lambda member: member["name"],
            def_node["members"]
        )

        return EnumType(
            name=def_node["name"],
            type_string=EnumType.get_type_string_from_def_node(def_node),
            canonical_name=def_node["canonicalName"],
            members=list(members),
            contract_name=def_node.get(NodeFilters.CERTORA_CONTRACT_NAME(), None),
            reference=def_node["id"],
            file=lookup_containing_file(def_node["id"])
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "UserDefinedEnum",
            "enumName": self.name,
            "enumMembers": [{"name": x} for x in self.members],
            "containingContract": self.contract_name,  # null means it wasn't declared in a contract but at file-level
            "astId": self.reference,
            "canonicalId": self.canonical_id
        }

    def get_abi_canonical_string(self, is_library: bool) -> str:
        if is_library:
            return f"{self.contract_name}.{self.name}"
        return "uint8"

    def get_source_str(self) -> str:
        return self.name  # no clue if this is right


class StructType(UserDefinedType):
    def __init__(self, name: str, type_string: str, canonical_name: str, members: List[Any], contract_name: str,
                 reference: int, file: Optional[str]):
        UserDefinedType.__init__(self, name, type_string, canonical_name, contract_name, reference, file)
        self.members = members

    class StructMember:
        def __init__(self, name: str, type: Type):
            self.name = name
            self.type = type

        @staticmethod
        def from_member_node(lookup_reference: Callable[[int], Dict[str, Any]],
                             lookup_containing_file: Callable[[int], Optional[str]],
                             member_node: Dict[str, Any]) -> 'StructType.StructMember':
            name = member_node["name"]
            type_name = member_node["typeName"]
            type = Type.from_type_name_node(lookup_reference, lookup_containing_file,
                                            type_name)
            assert type is not None
            return StructType.StructMember(name, type)

        def as_dict(self) -> Dict[str, Any]:
            return {
                "name": self.name,
                "type": self.type.as_dict()
            }

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]],
                      lookup_containing_file: Callable[[int], Optional[str]],
                      def_node: Dict[str, Any]) -> 'StructType':
        canonical_name = def_node["canonicalName"]
        return StructType(
            name=def_node["name"],
            type_string=f"struct {canonical_name}",
            canonical_name=canonical_name,
            members=[StructType.StructMember.from_member_node(lookup_reference,
                                                              lookup_containing_file,
                                                              member_node) for member_node in def_node["members"]],
            contract_name=def_node.get(NodeFilters.CERTORA_CONTRACT_NAME(), None),
            reference=def_node["id"],
            file=lookup_containing_file(def_node["id"]),
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "UserDefinedStruct",
            "structName": self.name,
            "structMembers": [x.as_dict() for x in self.members],
            "containingContract": self.contract_name,
            # ^ null means it wasn't declared in a contract but at file-level (is this possible for structs?)
            "astId": self.reference,
            "canonicalId": self.canonical_id,
        }

    def default_location(self) -> 'TypeLocation':
        return TypeLocation.MEMORY

    def get_abi_canonical_string(self, is_library: bool) -> str:
        if is_library:
            return f"{self.contract_name}.{self.name}"
        members = ",".join(m.type.get_abi_canonical_string(False) for m in self.members)
        return f"({members})"

    def get_source_str(self) -> str:
        return f"{self.canonical_name}"  # again, flailing here


# Solidity Name for a Type Alias
class UserDefinedValueType(UserDefinedType):
    def __init__(self, name: str, canonical_name: str, contract_name: str, reference: int,
                 underlying: Type, file: Optional[str]):
        UserDefinedType.__init__(self, name, canonical_name, canonical_name, contract_name, reference, file)
        self.underlying = underlying

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]],
                      lookup_containing_file: Callable[[int], Optional[str]],
                      def_node: Dict[str, Any], _: Optional[str] = None) -> 'UserDefinedValueType':
        underlying_node = def_node["underlyingType"]
        assert underlying_node["nodeType"] == "ElementaryTypeName", \
               f"Unexpected underlying type {underlying_node}"
        assert underlying_node["name"] in PrimitiveType.allowed_primitive_type_names, \
               f"Unexpected underlying type name {underlying_node['name']}"
        return UserDefinedValueType(
            name=def_node["name"],
            canonical_name=def_node["canonicalName"],
            contract_name=def_node.get(NodeFilters.CERTORA_CONTRACT_NAME(), None),
            reference=def_node["id"],
            underlying=PrimitiveType(underlying_node["name"], underlying_node["typeDescriptions"]["typeString"]),
            file=lookup_containing_file(def_node["id"])
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "UserDefinedValueType",
            "valueTypeName": self.name,
            "containingContract": self.contract_name,
            "valueTypeAliasedName": self.underlying.as_dict(),
            "astId": self.reference,
            "canonicalId": self.canonical_id,
        }

    def get_abi_canonical_string(self, is_library: bool) -> str:
        return self.underlying.get_abi_canonical_string(is_library)

    def get_source_str(self) -> str:
        return f"{self.contract_name}.{self.name}"


# unclear if this belongs in certoraBuild or not (it may only bet that CodeContracts come from the scene)
class ContractType(UserDefinedType):
    def __init__(self, name: str, reference: int):
        # TODO: should we allow contract_name for inner/nested contract declarations?
        UserDefinedType.__init__(self, name, f"contract {name}", name, name,  # is name right for typeString?
                                 reference, None)

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]],
                      lookup_containing_file: Callable[[int], Optional[str]],
                      def_node: Dict[str, Any], _: Optional[str] = None) -> 'ContractType':
        name = def_node["name"]
        reference = def_node["id"]
        return ContractType(name, reference)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "Contract",
            "contractName": self.name,
        }

    def get_abi_canonical_string(self, is_library: bool) -> str:
        if is_library:
            return self.name
        return "address"

    def get_source_str(self) -> str:
        return self.name  # yolo


class FunctionType(Type):
    def __init__(self, name: str):
        Type.__init__(self, name, name)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "Function",
            "name": self.name
        }

    def get_abi_canonical_string(self, is_library: bool) -> str:
        return "function"

    def get_source_str(self) -> str:
        return f"function {self.name}"  # this is wrong, fix is function types are ever really supported


class TypeLocation(Enum):
    STACK = "stack"
    MEMORY = "memory"
    CALLDATA = "calldata"
    STORAGE = "storage"

    @property
    def abi_str(self) -> str:
        if self == TypeLocation.STORAGE:
            return f' {self.value}'
        return ""


class TypeInstance:
    def __init__(self, type: Type, location: str = "default"):
        self.type = type
        self.location = TypeLocation(location) if location != "default" else type.default_location()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "typeDesc": self.type.as_dict(),
            "location": self.location.value
        }

    def get_abi_canonical_string(self, is_library: bool) -> str:
        ret = self.type.get_abi_canonical_string(is_library)
        if is_library:
            ret += self.location.abi_str if self.location == TypeLocation.STORAGE else ''
        return ret

    def get_source_str(self) -> str:
        return self.type.get_source_str()

    def get_source_and_location_str(self) -> str:
        return self.get_source_str() + (f" {self.location.value}" if self.location != TypeLocation.STACK else "")

    def matches(self, other: Any) -> bool:
        if not isinstance(other, TypeInstance):
            return False

        if not self.type.matches(other.type):
            return False

        if not self.location == other.location:
            return False

        return True
