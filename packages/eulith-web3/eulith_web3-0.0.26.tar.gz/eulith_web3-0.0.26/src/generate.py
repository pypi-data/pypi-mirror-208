from eulith_web3.binding_generator import ContractBindingGenerator

if __name__ == '__main__':
    g = ContractBindingGenerator(['../../../contracts/src/main/sol/gmx/IOrderBook.sol'],
                                 remappings={'@openzeppelin': '../../../node_modules/@openzeppelin'},
                                 allow_paths=['../../../contracts/src/main/sol/gmx'])
    g.generate('hello')
