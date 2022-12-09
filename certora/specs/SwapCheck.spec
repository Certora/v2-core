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
using SmartVaultHarnessSwap as SmartVault
using PriceOracleHarness as oracle
using DummyERC20FeeCollectorMock as FeeCollector
using DummyERC20A as ERC20A
using DummyERC20B as ERC20B
using DexMock as Dex

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

    getSwapFeePct() returns (uint256) envfree
    getSwapFeeCap() returns (uint256) envfree
    getSwapFeeToken() returns (address) envfree
    getSwapFeePeriod() returns (uint256) envfree
    getSwapFeeTotalCharged() returns (uint256) envfree
    getSwapFeeNextResetTime() returns (uint256) envfree

    feeCollector() returns (address) envfree

    // Price oracle & helpers
    oracle._getFeedData(address) returns (uint256, uint256) envfree
    oracle.getFeedDecimals(address) returns (uint256) envfree
    oracle.getERC20Decimals(address) returns (uint256) envfree
    oracle.pow10(uint256) returns (uint256) envfree
    oracle.balanceOfToken(address, address) returns(uint256) envfree
    oracle.uint32ToBytes4(uint32) returns (bytes4) envfree
    oracle.uint32Sol(uint256) returns (uint32) envfree
    oracle.getERC20Allowance(address, address, address) returns (uint256) envfree
    oracle.mulDownFP(uint256, uint256) returns (uint256) envfree
    oracle.pivot() returns(address) envfree
}

/**************************************************
 *                 SPECIFICATION                  *
 **************************************************/


// STATUS - verified
// Correctness check of swap() function
rule swapIntergrity(env e, env e2, method f) {
    // swap parameters
    address tokenIn;
    address tokenOut;
    uint256 amountIn;
    uint8 limitType;
    uint256 limitAmount;
    bytes data;

    /* other parameters
   SmartVault.Fee fee = myFee();

    require fee.pct == getSwapFeePct()
            && fee.cap == getSwapFeeCap()
            && fee.token == getSwapFeeToken()
            && fee.period == getSwapFeePeriod()
            && fee.totalCharged == getSwapFeeTotalCharged()
            && fee.nextResetTime == getSwapFeeNextResetTime();
    */
     
    require feeCollector() == FeeCollector;
    require tokenIn == ERC20A;
    require tokenOut == ERC20B;

    require e2.block.timestamp == e.block.timestamp;

    uint256 balanceOutDexBefore = ERC20B.balanceOf(e, Dex);
    uint256 balanceOutSmartWaltBefore = ERC20B.balanceOf(e, currentContract);

    uint256 balanceFCBefore = ERC20B.balanceOf(e, feeCollector());

    storage initialState = lastStorage;

    uint256 amountOut = swap(e2, tokenIn, tokenOut, amountIn, limitType, limitAmount, data);

    uint256 balanceOutDexAfter = ERC20B.balanceOf(e, Dex);
    uint256 balanceOutSmartWaltAfter = ERC20B.balanceOf(e, currentContract);

    uint256 balanceFCAfter = ERC20B.balanceOf(e, feeCollector());

    uint256 amountOutBeforeFees = balanceOutSmartWaltAfter - balanceOutSmartWaltBefore;
    uint256 paidFees = balanceFCAfter - balanceFCBefore;
    uint256 feesAndSwapAmount = paidFees + amountOutBeforeFees;

    // roll back to initial state to calculate fees to check their correctness
    uint256 payFeeResults = payFee(e, tokenOut, feesAndSwapAmount) at initialState;

    assert payFeeResults == paidFees;

    assert balanceFCAfter - balanceFCBefore == paidFees, "Remember, with great power comes great responsibility.";

    assert balanceOutDexBefore - balanceOutDexAfter == feesAndSwapAmount, "Dex balance should be decreased by amountOut";

    assert amountOut == balanceOutDexBefore - balanceOutDexAfter - paidFees, "AmountOut should be equal to amountOutBeforeFees + paidFees";
}


// STATUS - verified
// Correctness of balance updates in tokenIn by swap()
rule swapIntergrityTokenIn(env e, env e2, method f) {
    // swap parameters
    address tokenIn;
    address tokenOut;
    uint256 amountIn;
    uint8 limitType;
    uint256 limitAmount;
    bytes data;

    // other parameters
    SmartVault.Fee fee;

    require fee.pct == getSwapFeePct()
            && fee.cap == getSwapFeeCap()
            && fee.token == getSwapFeeToken()
            && fee.period == getSwapFeePeriod()
            && fee.totalCharged == getSwapFeeTotalCharged()
            && fee.nextResetTime == getSwapFeeNextResetTime();

    require tokenIn == ERC20A;
    require tokenOut == ERC20B;

    uint256 balanceInDexBefore = ERC20A.balanceOf(e, Dex);
    uint256 balanceInSmartWaltBefore = ERC20A.balanceOf(e, currentContract);

    uint256 amountOut = swap(e2, tokenIn, tokenOut, amountIn, limitType, limitAmount, data);

    uint256 balanceInDexAfter = ERC20A.balanceOf(e, Dex);
    uint256 balanceInSmartWaltAfter = ERC20A.balanceOf(e, currentContract);

    assert balanceInDexAfter - balanceInDexBefore == amountIn, "Dex balance should be increased by amountIn";
    assert balanceInSmartWaltBefore - balanceInSmartWaltAfter == amountIn, "SmartVault balance should be decreased by amountIn";
}


// STATUS - verified
// any other address except swap actors won't be affected by swap()
rule swapIntergrityOthersUntouchable(env e, env e2, method f) {
    // swap parameters
    address tokenIn;
    address tokenOut;
    uint256 amountIn;
    uint8 limitType;
    uint256 limitAmount;
    bytes data;

    address randAddress;

    require randAddress != currentContract
            && randAddress != Dex
            && randAddress != feeCollector();

    require tokenIn == ERC20A;
    require tokenOut == ERC20B;

    uint256 balanceInAddrBefore = ERC20A.balanceOf(e, randAddress);
    uint256 balanceOutAddrBefore = ERC20B.balanceOf(e, randAddress);

    uint256 amountOut = swap(e2, tokenIn, tokenOut, amountIn, limitType, limitAmount, data);

    uint256 balanceInAddrAfter = ERC20A.balanceOf(e, randAddress);
    uint256 balanceOutAddrAfter = ERC20B.balanceOf(e, randAddress);

    assert balanceInAddrBefore == balanceInAddrAfter, "Random address balance should not be changed (tokenIn)";
    assert balanceOutAddrBefore == balanceOutAddrAfter, "Random address balance should not be changed (tokenOut)";
}
