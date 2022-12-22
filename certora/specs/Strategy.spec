/*
    This is a specification file for smart contract
    verification with the Certora prover.

    For more information,
    visit: https://www.certora.com/

    This file is run with scripts/...
*/



////////////////////////////////////////
// ERC20 methods
import "./erc20.spec"
/**************************************************
 *                LINKED CONTRACTS                *
 **************************************************/
// Declaration of contracts used in the spec

// using WrappedNativeTokenMock as WRToken
// using SmartVaultHarnessSwap as SmartVault
using PriceOracleHarness as Oracle
// using DummyERC20FeeCollectorMock as FeeCollector
// using DummyERC20A as ERC20A
// using DummyERC20B as ERC20B
// using DexMock as Dex
using AaveV2Token as AToken
using TokenMock as Token

/**************************************************
 *              METHODS DECLARATIONS              *
 **************************************************/
methods {

    ////////////////////////////////////////
	// ERC20 methods
    WRToken.balanceOf(address) returns(uint256) envfree
    mint(address, uint256) => DISPATCHER(true)
    burn(address, uint256) => DISPATCHER(true)

    ////////////////////////////////////////
    // SwapConnectorMock methods
    // packages/smart-vault/contracts/test/core/SwapConnectorMock.sol
    swap(uint8, address, address, uint256, uint256, bytes) returns (uint256) => DISPATCHER(true)

    ////////////////////////////////////////
    // DexMock methods (called by SwapConnectorMock)
    // packages/smart-vault/contracts/test/samples/DexMock.sol
    swap(address, address, uint256, uint256, bytes) returns (uint256) => DISPATCHER(true)
    // swap(address tokenIn, address tokenOut, uint256 amountIn, uint256, bytes memory)
    //     returns (uint256 amountOut)

    implementationOf(address) returns (address) => DISPATCHER(true)
    implementationData(address) returns (bool, bool, bytes32) => DISPATCHER(true)
    ANY_ADDRESS() returns (address) envfree
    isStrategyAllowed(address) returns (bool) envfree
    investedValue(address) returns (uint256) envfree
    isAuthorized(address, bytes4) returns (bool) envfree
    getPriceFeed(address, address) returns (address) envfree
    getPrice(address, address) returns (uint256) envfree
    setSwapFee(uint256, uint256, address, uint256)

    // Price Oracle & helpers
    Oracle._getFeedData(address) returns (uint256, uint256) envfree
    Oracle.getFeedDecimals(address) returns (uint256) envfree
    Oracle.getERC20Decimals(address) returns (uint256) envfree
    Oracle.pow10(uint256) returns (uint256) envfree
    Oracle.balanceOfToken(address, address) returns(uint256) envfree
    Oracle.uint32ToBytes4(uint32) returns (bytes4) envfree
    Oracle.uint32Sol(uint256) returns (uint32) envfree
    Oracle.getERC20Allowance(address, address, address) returns (uint256) envfree
    Oracle.mulDownFP(uint256, uint256) returns (uint256) envfree
    Oracle.pivot() returns(address) envfree
}

rule sanity(env e, method f) 
    filtered { f -> f.selector == join(address, address[], uint256[], uint256, bytes).selector 
                    || f.selector == exit(address, address[], uint256[], uint256, bytes).selector 
                    || f.selector == claim(address, bytes).selector 
    } 
{
    calldataarg args;
    f(e, args);
    assert false;
}


// Disclaimer: this verification is done based on AAVE's Strategy implementation with harnesses
// since array as a return value is not supported in CVL


/**************************************************
 *                  JOIN INTEGRITY                *
 **************************************************/


// STATUS - in progress
// TODO: rule description
rule joinIntergrity_investedValue(env e, method f) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;

    require amountsIn[0] != 0;  // need this to avoid if branch in internal join. There is a bug with wrong array initialization in CVL
    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

    address tokenOut;
    uint256 amountOut;

    uint256 investedValueBefore = investedValue(strategy); 

    tokenOut, amountOut = joinHarness(e, strategy, tokensIn, amountsIn, slippage, data);

    uint256 investedValueAfter = investedValue(strategy);

    assert investedValueAfter - investedValueBefore == amountOut, "Remember, with great power comes great responsibility.";
}


rule joinIntergrity_aTokenBalance(env e, method f) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;

    require amountsIn[0] != 0;  // need this to avoid if branch in internal join. There is a bug with wrong array initialization in CVL
    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

    address tokenOut;
    uint256 amountOut;

    uint256 aTokenBalanceBefore = AToken.balanceOf(e, currentContract);

    tokenOut, amountOut = joinHarness(e, strategy, tokensIn, amountsIn, slippage, data);

    uint256 aTokenBalanceAfter = AToken.balanceOf(e, currentContract);

    assert aTokenBalanceAfter - aTokenBalanceBefore == amountOut, "Remember, with great power comes great responsibility.";
}


rule joinIntergrity_tokenBalance(env e, method f) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;

    require amountsIn[0] != 0;  // need this to avoid if branch in internal join. There is a bug with wrong array initialization in CVL
    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

    address tokenOut;
    uint256 amountOut;

    uint256 tokenBalanceCCBefore = Token.balanceOf(e, currentContract);
    uint256 tokenBalanceATokenBefore = Token.balanceOf(e, aToken(e));
    uint256 aTokenBalanceBefore = AToken.balanceOf(e, currentContract);

    tokenOut, amountOut = joinHarness(e, strategy, tokensIn, amountsIn, slippage, data);

    require amountOut != 0; 

    uint256 tokenBalanceCCAfter = Token.balanceOf(e, currentContract);
    uint256 tokenBalanceATokenAfter = Token.balanceOf(e, aToken(e));
    uint256 aTokenBalanceAfter = AToken.balanceOf(e, currentContract);

    uint256 amountInInternal = amountInInternal(e);
    uint256 amountsInExternal = amountsInExternal(e);
    uint256 amountsInHigh = amountsInHigh(e);

    assert tokenBalanceCCBefore - tokenBalanceCCAfter == amountOut, "Remember, with great power comes great responsibility.";
    assert tokenBalanceATokenAfter - tokenBalanceATokenBefore == amountOut, "Remember, with great power comes great responsibility.";
    assert amountsIn[0] == amountOut, "Remember, with great power comes great responsibility.";
}


// 2 small deposit shouldn't bring more proit for user (useless with ratio 1:1 but might be good for other strategies)



/**************************************************
 *                 CLAIM INTEGRITY                *
 **************************************************/


// STATUS - in progress
// TODO: rule description
// rule claimIntergrity_investedValue(env e, method f) {
//     address strategy;
//     bytes data;

//     require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

//     address tokenOut;
//     uint256 amountOut;

//     uint256 investedValueBefore = investedValue(strategy); 

//     tokenOut, amountOut = claimHarness(e, strategy, data);

//     uint256 investedValueAfter = investedValue(strategy);

//     assert investedValueAfter - investedValueBefore == amountOut, "Remember, with great power comes great responsibility.";
// }