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
using SmartVaultHarness as smartVaultContract

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

//  sanity check that all functions are reachable - expecting to fail
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
    assert false;
}


rule whoChangedWithdrawFeeSettings(method f)
{
    env e;
    calldataarg args;

    // withdrawFee parameters before
    uint256 pct0; uint256 cap0; address token0; uint256 period0; uint256 totalCharged0; uint256 nextResetTime0;
    require (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == smartVaultContract.withdrawFee(e);
    
    // call any function to try and modify withdrawFee
    f(e,args);

    // withdrawFee parameters after
    uint256 pct1; uint256 cap1; address token1; uint256 period1; uint256 totalCharged1; uint256 nextResetTime1;
    require (pct1, cap1, token1, period1, totalCharged1, nextResetTime1) == smartVaultContract.withdrawFee(e);

    assert (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == (pct1, cap1, token1, period1, totalCharged1, nextResetTime1);
}


rule whoChangedPerformanceFeeSettings(method f)
{
    env e;
    calldataarg args;

    // performanceFee parameters before
    uint256 pct0; uint256 cap0; address token0; uint256 period0; uint256 totalCharged0; uint256 nextResetTime0;
    require (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == smartVaultContract.performanceFee(e);
    
    // call any function to try and modify performanceFee
    f(e,args);

    // performanceFee parameters after
    uint256 pct1; uint256 cap1; address token1; uint256 period1; uint256 totalCharged1; uint256 nextResetTime1;
    require (pct1, cap1, token1, period1, totalCharged1, nextResetTime1) == smartVaultContract.performanceFee(e);

    assert (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == (pct1, cap1, token1, period1, totalCharged1, nextResetTime1);
}


rule whoChangedSwapFeeSettings(method f)
{
    env e;
    calldataarg args;

    // swapFee parameters before
    uint256 pct0; uint256 cap0; address token0; uint256 period0; uint256 totalCharged0; uint256 nextResetTime0;
    require (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == smartVaultContract.swapFee(e);
    
    // call any function to try and modify swapFee
    f(e,args);

    // swapFee parameters after
    uint256 pct1; uint256 cap1; address token1; uint256 period1; uint256 totalCharged1; uint256 nextResetTime1;
    require (pct1, cap1, token1, period1, totalCharged1, nextResetTime1) == smartVaultContract.swapFee(e);

    assert (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == (pct1, cap1, token1, period1, totalCharged1, nextResetTime1);
}


rule whoChangedThePriceOracle(method f)
{
    env e;
    calldataarg args;

    // priceOracle address before
    address priceOracle0;
    require priceOracle0 == smartVaultContract.priceOracle(e);
    
    // call any function to try and modify priceOracle
    f(e,args);

    // priceOracle address after
    address priceOracle1;
    require priceOracle1 == smartVaultContract.priceOracle(e);

    assert priceOracle0 == priceOracle1;
}


rule whoChangedTheSwapConnector(method f)
{
    env e;
    calldataarg args;

    // swapConnector address before
    address swapConnector0;
    require swapConnector0 == smartVaultContract.swapConnector(e);
    
    // call any function to try and modify swapConnector
    f(e,args);

    // swapConnector address after
    address swapConnector1;
    require swapConnector1 == smartVaultContract.swapConnector(e);

    assert swapConnector0 == swapConnector1;
}


rule whoChangedTheFeeCollector(method f)
{
    env e;
    calldataarg args;

    // feeCollector address before
    address feeCollector0;
    require feeCollector0 == smartVaultContract.feeCollector(e);
    
    // call any function to try and modify feeCollector
    f(e,args);

    // feeCollector address after
    address feeCollector1;
    require feeCollector1 == smartVaultContract.feeCollector(e);

    assert feeCollector0 == feeCollector1;
}


rule whoChangedStrategyPermissions(method f)
{
    env e;
    calldataarg args;

    // isStrategyAllowed[address strategy0] should not change
    address strategy0;
    bool strategy0bool;
    require strategy0bool == smartVaultContract.helperGetIsStrategyAllowed(e, strategy0);
    
    // call any function to try and modify feeCollector
    f(e,args);

    address strategy1;
    bool strategy1bool;
    require strategy1bool == smartVaultContract.helperGetIsStrategyAllowed(e, strategy1);

    assert (strategy0 == strategy1) => (strategy0bool == strategy1bool);
}