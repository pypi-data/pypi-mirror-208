from eulith_web3.binding_generator import ContractBindingGenerator

if __name__ == '__main__':
    g = ContractBindingGenerator(['../../../contracts/src/main/sol/gnosis/Safe.sol'],
                                 remappings={'@openzeppelin': '../../../node_modules/@openzeppelin'},
                                 allow_paths=['../../../contracts/src/main/sol/gnosis'])
    g.generate('hello')
