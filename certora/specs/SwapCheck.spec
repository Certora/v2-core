/*
    This is a specification file for smart contract
    verification with the Certora prover.

    For more information,
    visit: https://www.certora.com/

    This file is run with scripts/...
*/



////////////////////////////////////////
// ERC20 methods
import "./erc20.spec";
/**************************************************
 *                LINKED CONTRACTS                *
 **************************************************/
// Declaration of contracts used in the spec

// using WrappedNativeTokenMock as WRToken
using SmartVaultHarnessSwap as SmartVault;
using PriceOracleHarness as oracle;
using DummyERC20FeeCollectorMock as FeeCollector;
using DummyERC20A as ERC20A;
using DummyERC20B as ERC20B;
using DexMock as Dex;

/**************************************************
 *              METHODS DECLARATIONS              *
 **************************************************/
methods {

    ////////////////////////////////////////
	// ERC20 methods
    // function WRToken.balanceOf(address) external returns(uint256) envfree;
    function _.mint(address, uint256) external => DISPATCHER(true);
    function _.burn(address, uint256) external => DISPATCHER(true);

    ////////////////////////////////////////
    // SwapConnectorMock methods
    // packages/smart-vault/contracts/test/core/SwapConnectorMock.sol
    function _.swap(uint8, address, address, uint256, uint256, bytes) external => DISPATCHER(true);

    ////////////////////////////////////////
    // DexMock methods (called by SwapConnectorMock)
    // packages/smart-vault/contracts/test/samples/DexMock.sol
    function _.swap(address, address, uint256, uint256, bytes) external => DISPATCHER(true);
    // swap(address tokenIn, address tokenOut, uint256 amountIn, uint256, bytes memory)
    //     returns (uint256 amountOut)

    function _.implementationOf(address) external => DISPATCHER(true);
    function _.implementationData(address) external => DISPATCHER(true);
    function ANY_ADDRESS() external returns (address) envfree;
    function isStrategyAllowed(address) external returns (bool) envfree;
    function investedValue(address) external returns (uint256) envfree;
    function isAuthorized(address, bytes4) external returns (bool) envfree;
    function getPriceFeed(address, address) external returns (address) envfree;
    function getPrice(address, address) external returns (uint256) envfree;
    function setSwapFee(uint256, uint256, address, uint256) external;

    function getSwapFeePct() external returns (uint256) envfree;
    function getSwapFeeCap() external returns (uint256) envfree;
    function getSwapFeeToken() external returns (address) envfree;
    function getSwapFeePeriod() external returns (uint256) envfree;
    function getSwapFeeTotalCharged() external returns (uint256) envfree;
    function getSwapFeeNextResetTime() external returns (uint256) envfree;

    function feeCollector() external returns (address) envfree;

    // Price oracle & helpers
    function oracle._getFeedData(address) external returns (uint256, uint256) envfree;
    function oracle.getFeedDecimals(address) external returns (uint256) envfree;
    function oracle.getERC20Decimals(address) external returns (uint256) envfree;
    function oracle.pow10(uint256) external returns (uint256) envfree;
    function oracle.balanceOfToken(address, address) external returns(uint256) envfree;
    function oracle.uint32ToBytes4(uint32) external returns (bytes4) envfree;
    function oracle.uint32Sol(uint256) external returns (uint32) envfree;
    function oracle.getERC20Allowance(address, address, address) external returns (uint256) envfree;
    function oracle.mulDownFP(uint256, uint256) external returns (uint256) envfree;
    function oracle.pivot() external returns(address) envfree;
}

/**************************************************
 *                 SPECIFICATION                  *
 **************************************************/


// STATUS - verified
// Addresses' balances involved in swap should be updated correctly regarding DeX's token, paidFees and amountOut
rule swapIntergrity(env e, env e2, method f) {
    // swap parameters
    address tokenIn;
    address tokenOut;
    uint256 amountIn;
    SmartVaultHarnessSwap.SwapLimit limitType;
    uint256 limitAmount;
    bytes data;
     
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

    uint256 amountOutBeforeFees = require_uint256(balanceOutSmartWaltAfter - balanceOutSmartWaltBefore);
    uint256 paidFees = require_uint256(balanceFCAfter - balanceFCBefore);
    uint256 feesAndSwapAmount = require_uint256(paidFees + amountOutBeforeFees);

    // roll back to initial state to calculate fees to check their correctness
    uint256 payFeeResults = payFee(e, tokenOut, feesAndSwapAmount) at initialState;

    assert payFeeResults == paidFees;
    assert balanceFCAfter - balanceFCBefore == to_mathint(paidFees), "Remember, with great power comes great responsibility.";
    assert balanceOutDexBefore - balanceOutDexAfter == to_mathint(feesAndSwapAmount), "Dex balance should be decreased by amountOut";
    assert to_mathint(amountOut) == balanceOutDexBefore - balanceOutDexAfter - paidFees, "AmountOut should be equal to amountOutBeforeFees + paidFees";
}


// STATUS - verified
// Correctness of balance updates in tokenIn by swap()
rule swapIntergrityTokenIn(env e, env e2, method f) {
    // swap parameters
    address tokenIn;
    address tokenOut;
    uint256 amountIn;
    SmartVaultHarnessSwap.SwapLimit limitType;
    uint256 limitAmount;
    bytes data;

    require tokenIn == ERC20A;
    require tokenOut == ERC20B;

    uint256 balanceInDexBefore = ERC20A.balanceOf(e, Dex);
    uint256 balanceInSmartWaltBefore = ERC20A.balanceOf(e, currentContract);

    uint256 amountOut = swap(e2, tokenIn, tokenOut, amountIn, limitType, limitAmount, data);

    uint256 balanceInDexAfter = ERC20A.balanceOf(e, Dex);
    uint256 balanceInSmartWaltAfter = ERC20A.balanceOf(e, currentContract);

    assert balanceInDexAfter - balanceInDexBefore == to_mathint(amountIn), "Dex balance should be increased by amountIn";
    assert balanceInSmartWaltBefore - balanceInSmartWaltAfter == to_mathint(amountIn), "SmartVault balance should be decreased by amountIn";
}


// STATUS - verified
// any other address except swap actors shouldn't be affected by swap()
rule swapIntergrityOthersUntouchable(env e, env e2, method f) {
    // swap parameters
    address tokenIn;
    address tokenOut;
    uint256 amountIn;
    SmartVaultHarnessSwap.SwapLimit limitType;
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


// STATUS - verified
// During swap(), no additional tokens should be gain regarding tokenIn
rule swapConsistencyTokenIn(env e, env e2, method f) {
    address tokenIn;
    address tokenOut;
    uint256 amountIn;
    SmartVaultHarnessSwap.SwapLimit limitType;
    uint256 limitAmount;
    bytes data;

    require tokenIn == ERC20A;
    require tokenOut == ERC20B;
    require feeCollector() != Dex && feeCollector() != currentContract;

    uint256 balanceInDexBefore = ERC20A.balanceOf(e, Dex);
    uint256 balanceInSmartWaltBefore = ERC20A.balanceOf(e, currentContract);
    uint256 balanceFCBefore = ERC20A.balanceOf(e, feeCollector());

    uint256 amountOut = swap(e2, tokenIn, tokenOut, amountIn, limitType, limitAmount, data);

    uint256 balanceInDexAfter = ERC20A.balanceOf(e, Dex);
    uint256 balanceInSmartWaltAfter = ERC20A.balanceOf(e, currentContract);
    uint256 balanceFCAfter = ERC20A.balanceOf(e, feeCollector());

    assert balanceInDexBefore + balanceInSmartWaltBefore + balanceFCBefore == balanceInDexAfter + balanceInSmartWaltAfter + balanceFCAfter;
}


// STATUS - verified
// During swap(), no additional tokens should be gain regarding tokenOut
rule swapConsistencyTokenOut(env e, env e2, method f) {
    address tokenIn;
    address tokenOut;
    uint256 amountIn;
    SmartVaultHarnessSwap.SwapLimit limitType;
    uint256 limitAmount;
    bytes data;

    require tokenIn == ERC20A;
    require tokenOut == ERC20B;
    require feeCollector() != Dex && feeCollector() != currentContract;

    uint256 balanceInDexBefore = ERC20B.balanceOf(e, Dex);
    uint256 balanceInSmartWaltBefore = ERC20B.balanceOf(e, currentContract);
    uint256 balanceFCBefore = ERC20B.balanceOf(e, feeCollector());

    uint256 amountOut = swap(e2, tokenIn, tokenOut, amountIn, limitType, limitAmount, data);

    uint256 balanceInDexAfter = ERC20B.balanceOf(e, Dex);
    uint256 balanceInSmartWaltAfter = ERC20B.balanceOf(e, currentContract);
    uint256 balanceFCAfter = ERC20B.balanceOf(e, feeCollector());

    assert balanceInDexBefore + balanceInSmartWaltBefore + balanceFCBefore == balanceInDexAfter + balanceInSmartWaltAfter + balanceFCAfter;
}
