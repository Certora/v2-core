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


// external join

// STATUS - in progress
// TODO: rule description
rule joinIntergrity_investedValue(env e, method f) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;

    address tokenOut;
    uint256 amountOut;

    uint256 investedValueBefore = investedValue(strategy); 

    tokenOut, amountOut = joinHarness(e, strategy, tokensIn, amountsIn, slippage, data);

    uint256 investedValueAfter = investedValue(strategy);

    assert investedValueAfter - investedValueBefore == amountOut, "Remember, with great power comes great responsibility.";
}