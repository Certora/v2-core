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
//using WrappedNativeTokenMock as wrappedToken
using StrategyMock as strategyMock

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
    swap(address, address, uint256, uint256, bytes) => DISPATCHER(true)

    ////////////////////////////////////////
    // node_modules/@openzeppelin/contracts/utils/Address.sol
    //sendValue(address, uint256) => DISPATCHER(true) // not working well!
    // !@#@!@#@ still getting call resolutions for swap(), exit(), withdraw()
    sendValue(address, uint256) => HAVOC_ECF


    ////////////////////////////////////////
    // node_modules/@mimic-fi/v2-strategies/contracts/IStrategy.sol
    // packages/strategies/contracts/IStrategy.sol
    // using the mock at:
    // packages/smart-vault/contracts/test/core/StrategyMock.sol
    token() => DISPATCHER(true)
    // valueRate() returns (uint256) => DISPATCHER(true)
    lastValue(address) returns (uint256) => DISPATCHER(true)
    claim(bytes) returns (address[], uint256[]) => DISPATCHER(true)
    join(uint256, uint256, bytes) returns (uint256) => DISPATCHER(true)
    exit(uint256, uint256, bytes) returns (uint256, uint256) => DISPATCHER(true)
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
rule sanity(method f){
    env e;
    calldataarg args;
    f(e,args);
    //join(e,args);
    assert false;
}
