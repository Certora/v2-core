// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

import '../munged/SmartVault.sol';  // CVL1
// import '../../packages/smart-vault/contracts/SmartVault.sol';  // CVL2

import '../../packages/smart-vault/contracts/test/samples/DexMock.sol';

contract SmartVaultHarnessSwap is SmartVault {
    using FixedPoint for uint256;
    using UncheckedMath for uint256;

    DexMock public immutable dex;
    
    constructor(address _wrappedNativeToken, address _registry) SmartVault(_wrappedNativeToken, _registry) 
    {
        dex = new DexMock();
    }

    function swap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        SwapLimit limitType,
        uint256 limitAmount,
        bytes memory data
    ) external auth returns (uint256 amountOut) {
        require(tokenIn != tokenOut, 'SWAP_SAME_TOKEN');
        require(swapConnector != address(0), 'SWAP_CONNECTOR_NOT_SET');

        uint256 minAmountOut;
        if (limitType == SwapLimit.MinAmountOut) {
            minAmountOut = limitAmount;
        } else if (limitType == SwapLimit.Slippage) {
            require(limitAmount <= FixedPoint.ONE, 'SWAP_SLIPPAGE_ABOVE_ONE');
            uint256 price = getPrice(tokenIn, tokenOut);
            // No need for checked math as we are checking it manually beforehand
            // Always round up the expected min amount out. Limit amount is slippage.
            minAmountOut = amountIn.mulUp(price).mulUp(FixedPoint.ONE.uncheckedSub(limitAmount));
        } else {
            revert('SWAP_INVALID_LIMIT_TYPE');
        }

        uint256 preBalanceOut = IERC20(tokenOut).balanceOf(address(this));

        // swapConnector.swap(source, tokenIn, tokenOut, amountIn, minAmountOut, data);
        IERC20(tokenIn).approve(address(dex), amountIn);
        dex.swap(tokenIn, tokenOut, amountIn, minAmountOut, data);

        uint256 postBalanceOut = IERC20(tokenOut).balanceOf(address(this));
        uint256 amountOutBeforeFees = postBalanceOut - preBalanceOut;
        require(amountOutBeforeFees >= minAmountOut, 'SWAP_MIN_AMOUNT');

        uint256 swapFeeAmount = _payFee(tokenOut, amountOutBeforeFees, swapFee);
        amountOut = amountOutBeforeFees - swapFeeAmount;
    }

    function payFee(address token, uint256 amount) external returns (uint256 paidAmount){
        return _payFee(token, amount, swapFee);
    }

    function getSwapFeePct() view external returns (uint256) {
        return swapFee.pct;
    }

    function getSwapFeeCap() view external returns (uint256) {
        return swapFee.cap;
    }

    function getSwapFeeToken() view external returns (address) {
        return swapFee.token;
    }

    function getSwapFeePeriod() view external returns (uint256) {
        return swapFee.period;
    }

    function getSwapFeeTotalCharged() view external returns (uint256) {
        return swapFee.totalCharged;
    }

    function getSwapFeeNextResetTime() view external returns (uint256) {
        return swapFee.nextResetTime;
    }
}