/*
    This is a specification file for smart contract
    verification with the Certora prover.

    For more information,
    visit: https://www.certora.com/

    This file is run with scripts/...
*/




/**************************************************
 *                LINKED CONTRACTS                *
 **************************************************/
// Declaration of contracts used in the spec

// using DummyERC20Impl as dummyERC20Token
// using DummyERC20A as tokenA
// using DummyERC20B as tokenB
// using WrappedNativeTokenMock as wrappedToken
// using StrategyMock as strategyMock

/**************************************************
 *              METHODS DECLARATIONS              *
 **************************************************/
methods {
    // Harness method getters:

    ////////////////////////////////////////
	// ERC20 methods
	transferFrom(address, address, uint256) => DISPATCHER(true)
	transfer(address, uint256) => DISPATCHER(true)
    balanceOf(address) => DISPATCHER(true)
    approve(address, uint256) => DISPATCHER(true)

    // packages/smart-vault/contracts/test/samples/TokenMock.sol
    mint(address, uint256) => DISPATCHER(true)
    burn(address, uint256) => DISPATCHER(true)

	// //
    // tokenA.balanceOf(address) envfree
	// tokenB.balanceOf(address) envfree
	// dummyERC20Token.balanceOf(address) envfree
	// //
    // tokenA.totalSupply() envfree
	// tokenB.totalSupply() envfree
	// dummyERC20Token.totalSupply() envfree

    ////////////////////////////////////////
    // SwapConnectorMock methods
    // packages/smart-vault/contracts/test/core/SwapConnectorMock.sol
    swap(uint8, address, address, uint256, uint256, bytes) returns (uint256) => DISPATCHER(true)
    // swap(
    //     ISwapConnector.Source, /* source */ //enum --> uint8
    //     address tokenIn,
    //     address tokenOut,
    //     uint256 amountIn,
    //     uint256 minAmountOut,
    //     bytes memory data
    // ) external override returns (uint256 amountOut) => DISPATCHER(true)

    ////////////////////////////////////////
    // DexMock methods (called by SwapConnectorMock)
    // packages/smart-vault/contracts/test/samples/DexMock.sol
    swap(address, address, uint256, uint256, bytes) returns (uint256) => DISPATCHER(true)
    // swap(address tokenIn, address tokenOut, uint256 amountIn, uint256, bytes memory)
    //     returns (uint256 amountOut)

    ////////////////////////////////////////
    // node_modules/@openzeppelin/contracts/utils/Address.sol
    // sendValue(address, uint256) => DISPATCHER(true) // not working well, probably because is internal!
    // getting call resolutions for swap(), exit(), withdraw()
    // sendValue(address, uint256) => HAVOC_ECF
    // RESOLVED using --settings -optimisticFallback=true \
    
    ////////////////////////////////////////
    // SmartVault.sol = the main contract
    // call(address, bytes, uint256, bytes) returns (bytes) => HAVOC_ECF
    // ------------- WARNING! -------------
    // call is considered a reserved keyword in CVL, meanwhile HOTFIX by Alex works partially:
    // --staging alex/remove-call-cvl-keyword \
    // --disableLocalTypeChecking
    // we are getting the default: havoc all contracts except SmartVaultHarness


    ////////////////////////////////////////
    // node_modules/@mimic-fi/v2-strategies/contracts/IStrategy.sol
    // packages/strategies/contracts/IStrategy.sol
    // both files above were identical
    // the interface is implemented by mock at:
    // packages/smart-vault/contracts/test/core/StrategyMock.sol
    // token() => DISPATCHER(true)
    // valueRate() returns (uint256) => DISPATCHER(true)
    lastValue(address) returns (uint256) => NONDET
    // lastValue(address) returns (uint256) => DISPATCHER(true) // causes error in rule sanity -> exit()
    // claim(bytes) returns (address[], uint256[]) => DISPATCHER(true) // works, but too slow
    claim(bytes) returns (address[], uint256[]) => NONDET
    // join(uint256, uint256, bytes) returns (uint256) => DISPATCHER(true) // old version
    // join(address[],uint256[],uint256,bytes) returns (address[], uint256[], uint256) => DISPATCHER(true) // causes error in rule sanity -> exit()
    join(address[],uint256[],uint256,bytes) returns (address[], uint256[], uint256) => NONDET 
    // exit(uint256, uint256, bytes) returns (uint256, uint256) => DISPATCHER(true) // old version
    exit(address[],uint256[],uint256,bytes) returns (address[], uint256[], uint256) => NONDET

    // the StrategyMock dispatchers caused the tool to TIMEOUT because of
    // incorrect calling in the SmartVault.sol
    // fixed the original code by changing "strategy." to "IStrategy(strategy)."


    ////////////////////////////////////////
    // packages/registry/contracts/registry/IRegistry.sol
    // using the implementation at:
    // packages/registry/contracts/registry/Registry.sol
    implementationOf(address) returns (address) => DISPATCHER(true)
    implementationData(address) returns (bool, bool, bytes32) => DISPATCHER(true)
    

}



/**************************************************
 *                  DEFINITIONS                   *
 **************************************************/



/**************************************************
 *                GHOSTS AND HOOKS                *
 **************************************************/




/**************************************************
 *               CVL FUNCS & DEFS                 *
 **************************************************/



/**************************************************
 *                 VALID STATES                   *
 **************************************************/
// Describe expressions over the system's variables
// that should always hold.
// Usually implemented via invariants 



/**************************************************
 *               STATE TRANSITIONS                *
 **************************************************/
// Describe validity of state changes by taking into
// account when something can change or who may change



/**************************************************
 *                METHOD INTEGRITY                *
 **************************************************/
 // Describe the integrity of a specific method



/**************************************************
 *             HIGH-LEVEL PROPERTIES              *
 **************************************************/
// Describe more than one element of the system,
// might be even cross-system, usually implemented
// as invariant or parametric rule,
// sometimes require the usage of ghost



/**************************************************
 *                 RISK ANALYSIS                  *
 **************************************************/
// Reasoning about the assets of the user\system and
// from point of view of what should never happen 



/**************************************************
 *                      MISC                      *
 **************************************************/

//  rules for info and checking the ghost and tool
//  expecting to fail
rule sanity(method f)
    // filtered {f->f.selector == swap(uint8,address,address,uint256,uint8,uint256,bytes).selector}
    // filtered {f->f.selector == exit(address,uint256,uint256,bytes).selector}
    // filtered {f->f.selector == swap(uint8,address,address,uint256,uint8,uint256,bytes).selector ||
    //             f.selector == withdraw(address,uint256,address,bytes).selector ||
    //             f.selector == exit(address,uint256,uint256,bytes).selector ||
    //             f.selector == call(address,bytes,uint256,bytes).selector ||
    //             f.selector == unwrap(uint256,bytes).selector}
    // filtered {f->f.selector != claim(address,bytes).selector}
    // filtered {f->f.selector != join(address,address[],uint256[],uint256,bytes).selector}
{
    env e;
    calldataarg args;
    f(e,args);
    //join(e,args);
    //swap(e,args);
    assert false;
}
