import os
import re
from typing import List, Dict, Optional

from solcx import compile_files


class ContractBindingGenerator:
    """
    Class for generating Python bindings for a Solidity contract.

    :ivar remappings: Remappings for imported files.
    :vartype remappings: Dict
    :ivar sources: A list of Solidity contract source files.
    :vartype sources: List[str]
    :ivar allow_paths: An optional list of allowed file paths.
    :vartype allow_paths: Optional[List[str]]
    :ivar template: the string representation of the python file as it's being generated
    :vartype template: str

    :raises ContractAddressNotSet: raised if you try to take an action on-chain without instantiating with a contract address
    """

    def __init__(self, sources: List[str], remappings: Dict, allow_paths: Optional[List[str]] = None):
        """
        :param sources: a list of strings for the .sol sources you intend to compile and generate bindings for
        :type sources: List[str]
        :param remappings: see https://docs.soliditylang.org/en/v0.8.18/using-the-compiler.html#base-path-and-import-remapping
        :type remappings: Dict
        :param allow_paths: see https://docs.soliditylang.org/en/v0.8.18/using-the-compiler.html#base-path-and-import-remapping
        :type allow_paths: Optional[List[str]]
        """

        self.structs = {}
        self.remappings = remappings
        self.sources = sources
        self.allow_paths = allow_paths
        self.template = """from typing import Optional, Union, List, TypedDict
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams
"""

    @staticmethod
    def sol_type_to_py_type(t):
        sol_type_to_py_type = {
            'uint256': 'int',
            'uint128': 'int',
            'uint64': 'int',
            'uint32': 'int',
            'uint16': 'int',
            'uint8': 'int',
            'int256': 'int',
            'int128': 'int',
            'int64': 'int',
            'int32': 'int',
            'int16': 'int',
            'int8': 'int',
            'address': 'str',
            'bool': 'bool',
            'bytes32': 'bytes',
            'bytes1': 'bytes',
            'bytes': 'bytes',
            'tuple': 'tuple',
            'string': 'str'
        }

        if 'struct' in t:
            base_type = ContractBindingGenerator.internal_type_name_to_struct_name(t)
        else:
            base_type = sol_type_to_py_type.get(t.split('[')[0], None)

        if '[' in t:
            return f'List[{base_type}]'
        else:
            return base_type

    @staticmethod
    def camel_to_snake(camel):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', camel).lower()

    @staticmethod
    def internal_type_name_to_struct_name(type_name):
        tokens = type_name.split(' ')
        type_name = tokens[-1]
        return type_name.split('.')[-1].strip('[]')

    @staticmethod
    def outputs_to_return_type(outputs):
        if len(outputs) == 1:
            o = outputs[0]
            return ContractBindingGenerator.sol_type_to_py_type(o.get('type', None))
        elif len(outputs) > 1:
            types = []
            for o in outputs:
                types.append(ContractBindingGenerator.sol_type_to_py_type(o.get('type', None)))

            tuple_str = ', '.join(types)
            return f'({tuple_str})'
        else:
            return None

    @staticmethod
    def get_struct_formatting_code():
        return """
def serialize_struct(d) -> tuple:
    if isinstance(d, dict):
        return tuple(serialize_struct(v) for v in d.values())
    elif isinstance(d, (list, tuple)):
        return tuple(serialize_struct(x) for x in d)
    else:
        return d
"""

    @staticmethod
    def parse_structs(json_data):
        classes = []
        if isinstance(json_data, dict):
            class_name_tokens = json_data.get("internalType").split(' ')
            if len(class_name_tokens) > 1:
                class_name = class_name_tokens[1]
            else:
                class_name = class_name_tokens[0]
            members = []
            for component in json_data.get("components", []):
                member_name = component.get("name")
                member_type = component.get("type")
                member_internal_type = component.get("internalType")
                if member_internal_type.startswith("struct"):
                    member_type = member_internal_type.split(" ")[1]
                    classes.extend(ContractBindingGenerator.parse_structs(component))
                members.append({"name": member_name, "type": member_type})
            classes.append({"struct_name": class_name, "members": members})
        return classes

    def inputs_to_argument_string(self, inputs):
        args = ['self']
        pass_into_method = []
        for i, ip in enumerate(inputs):
            internal_type = ip.get('internalType', None)
            is_struct = False
            if 'struct' in internal_type:
                is_struct = True
                struct_definitions = ContractBindingGenerator.parse_structs(ip)
                for sd in struct_definitions:
                    self.structs.update({sd.get('struct_name'): sd.get('members')})

            write_type = ContractBindingGenerator.sol_type_to_py_type(internal_type)

            n = ip.get('name', None)
            if not n:
                n = f'a{i}'
            elif n == 'from':
                n = '_from'

            args.append(f"{ContractBindingGenerator.camel_to_snake(n)}: {write_type}")
            if is_struct:
                pass_into_method.append(f'serialize_struct({ContractBindingGenerator.camel_to_snake(n)})')
            else:
                pass_into_method.append(ContractBindingGenerator.camel_to_snake(n))

        return ", ".join(pass_into_method), ", ".join(args)

    def generate(self, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output = compile_files(self.sources, output_values=["abi", "bin-runtime", "bin"],
                               import_remappings=self.remappings, allow_paths=self.allow_paths)

        for key, val in output.items():
            contract_name = key.split(':')[1]
            file_name = f"{re.sub(r'(?<!^)(?=[A-Z])', '_', contract_name).lower()}.py"
            path = os.path.join(output_dir, file_name)
            abi = val.get('abi')
            has_constructor = 'constructor' in [elem.get('type') for elem in abi]
            byte_code = val.get('bin')
            code = ''

            code += f"""
\nclass {contract_name}:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = {abi}
        self.bytecode = '{byte_code}'
        self.w3 = web3
            """

            if not has_constructor:
                code += """
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        """

            seen_methods = set()

            for elem in abi:
                ty = elem.get('type')
                inputs = elem.get('inputs', [])
                pass_into_method, statement_args = self.inputs_to_argument_string(inputs)

                if ty == 'constructor':
                    code += f"""
    def deploy({statement_args}):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor({pass_into_method}).transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        """
                elif ty == 'function':
                    func_name = elem.get('name')

                    # we can take the first instance of the method because this is the instance that was
                    # defined in the top level contract
                    if func_name in seen_methods:
                        continue

                    seen_methods.add(func_name)

                    state_mutability = elem.get('stateMutability')
                    outputs = elem.get('outputs', [])
                    return_type = ContractBindingGenerator.outputs_to_return_type(outputs)
                    return_type_string = ' -> TxParams'
                    return_stmt = f"return c.functions.{func_name}({pass_into_method})"
                    if state_mutability != 'view':
                        statement_args += ', override_tx_parameters: Optional[TxParams] = None'
                        return_stmt = f'{return_stmt}.build_transaction(override_tx_parameters)'
                    elif state_mutability == 'view' and return_type:
                        return_type_string = f' -> {return_type}'
                        return_stmt = f"return c.functions.{func_name}({pass_into_method}).call()"
                    else:
                        return_stmt = f'{return_stmt}.build_transaction()'

                    code += f"""\n    def {ContractBindingGenerator.camel_to_snake(func_name)}({statement_args}){return_type_string}:"""
                    code += """\n        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    """
                    code += f"""\n        {return_stmt}\n"""

            with open(path, 'w+') as file:
                file.write(self.template)

                for k, _ in self.structs.items():
                    write_name = ContractBindingGenerator.internal_type_name_to_struct_name(k)
                    file.write(f"from {ContractBindingGenerator.camel_to_snake(write_name)} import {write_name}\n")

                if len(self.structs) > 0:
                    file.write('\n')
                    file.write(ContractBindingGenerator.get_struct_formatting_code())

                file.write("""
\nclass ContractAddressNotSet(Exception):
    pass\n""")

                file.write(code)

            for k, v in self.structs.items():
                struct_names = set(self.structs.keys())
                write_name = ContractBindingGenerator.internal_type_name_to_struct_name(k)

                struct_filename = f'{ContractBindingGenerator.camel_to_snake(write_name)}.py'
                struct_path = os.path.join(output_dir, struct_filename)

                with open(struct_path, 'w+') as struct_file:
                    import_string = 'from typing import List, TypedDict'
                    members_string = ''
                    class_string = f"""
class {write_name}(TypedDict):"""
                    for iv in v:
                        write_type = ContractBindingGenerator.sol_type_to_py_type(iv.get('type'))
                        if not write_type:
                            write_type = iv.get('type')

                        if write_type in struct_names:
                            import_string += f'\nfrom {ContractBindingGenerator.camel_to_snake(write_type)} import {write_type}'
                        write_name = ContractBindingGenerator.camel_to_snake(iv.get('name'))
                        members_string += f"""\n    {write_name}: {write_type}"""

                    struct_file.write(import_string)
                    struct_file.write('\n\n')
                    struct_file.write(class_string)
                    struct_file.write(members_string)
                    struct_file.write('\n')
