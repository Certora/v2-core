// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

import '../munged/SmartVault.sol';

contract SmartVaultHarness is SmartVault {

    using FixedPoint for uint256;
    using UncheckedMath for uint256;

    // Aave strategy
    IStrategy public immutable aaveStrategy;
    
    constructor(address _wrappedNativeToken, address _registry,
        address _aaveStategy) SmartVault(_wrappedNativeToken,_registry) {
            aaveStrategy = IStrategy(_aaveStategy);
    }
    
    function join(
        address,
        address[] memory tokensIn,
        uint256[] memory amountsIn,
        uint256 slippage,
        bytes memory data
    ) override external auth returns (address[] memory tokensOut, uint256[] memory amountsOut) 
    {
        address strategy = address(aaveStrategy);
        require(isStrategyAllowed[strategy], 'STRATEGY_NOT_ALLOWED');
        require(slippage <= FixedPoint.ONE, 'JOIN_SLIPPAGE_ABOVE_ONE');
        require(tokensIn.length == amountsIn.length, 'JOIN_INPUT_INVALID_LENGTH');

        uint256 value;
        // Strategy Lib
        //(tokensOut, amountsOut, value) = strategy.join(tokensIn, amountsIn, slippage, data);
        bytes memory joinData = abi.encodeWithSelector(IStrategy.join.selector, tokensIn, amountsIn, slippage, data);
        
        (bool success, bytes memory returndata) = address(aaveStrategy).delegatecall(joinData);
        Address.verifyCallResult(success, returndata, 'JOIN_CALL_REVERTED');
        (tokensOut, amountsOut, value) =  abi.decode(returndata, (address[], uint256[], uint256));
        
        require(tokensOut.length == amountsOut.length, 'JOIN_OUTPUT_INVALID_LENGTH');

        investedValue[strategy] = investedValue[strategy] + value;
        emit Join(strategy, tokensIn, amountsIn, tokensOut, amountsOut, value, slippage, data);
    }

    function exit(
        address,
        address[] memory tokensIn,
        uint256[] memory amountsIn,
        uint256 slippage,
        bytes memory data
    ) override external auth returns (address[] memory tokensOut, uint256[] memory amountsOut)
    {
        address strategy = address(aaveStrategy);
        require(isStrategyAllowed[strategy], 'STRATEGY_NOT_ALLOWED');
        require(investedValue[strategy] > 0, 'EXIT_NO_INVESTED_VALUE');
        require(slippage <= FixedPoint.ONE, 'EXIT_SLIPPAGE_ABOVE_ONE');
        require(tokensIn.length == amountsIn.length, 'EXIT_INPUT_INVALID_LENGTH');

        uint256 value;
        // Strategy Lib
        //(tokensOut, amountsOut, value) = strategy.exit(tokensIn, amountsIn, slippage, data);
        bytes memory exitData = abi.encodeWithSelector(IStrategy.exit.selector, tokensIn, amountsIn, slippage, data);

        // solhint-disable-next-line avoid-low-level-calls
        (bool success, bytes memory returndata) = address(aaveStrategy).delegatecall(exitData);
        Address.verifyCallResult(success, returndata, 'EXIT_CALL_REVERTED');
        (tokensOut, amountsOut, value) = abi.decode(returndata, (address[], uint256[], uint256));

        require(tokensOut.length == amountsOut.length, 'EXIT_OUTPUT_INVALID_LENGTH');
        //uint256[] memory performanceFeeAmounts = new uint256[](amountsOut.length);

        // It can rely on the last updated value since we have just exited, no need to compute current value
        uint256 valueBeforeExit = lastValue(strategy) + value;
        if (valueBeforeExit <= investedValue[strategy]) {
            // There were losses, invested value is simply reduced using the exited ratio compared to the value
            // before exit. Invested value is round up to avoid interpreting losses due to rounding errors
            investedValue[strategy] -= investedValue[strategy].mulUp(value).divUp(valueBeforeExit);
        } else {
            // If value gains are greater than the exit value, it means only gains are being withdrawn. In that case
            // the taxable amount is the entire exited amount, otherwise it should be the equivalent gains ratio of it.
            uint256 valueGains = valueBeforeExit.uncheckedSub(investedValue[strategy]);
            bool onlyGains = valueGains >= value;

            // If the exit value is greater than the value gains, the invested value should be reduced by the portion
            // of the invested value being exited. Otherwise, it's still the same, only gains are being withdrawn.
            // No need for checked math as we are checking it manually beforehand
            uint256 decrement = onlyGains ? 0 : value.uncheckedSub(valueGains);
            investedValue[strategy] = investedValue[strategy] - decrement;

            // Compute performance fees per token out
            for (uint256 i = 0; i < tokensOut.length; i = i.uncheckedAdd(1)) {
                address token = tokensOut[i];
                uint256 amount = amountsOut[i];
                uint256 taxableAmount = onlyGains ? amount : ((amount * valueGains) / value);
                uint256 feeAmount = _payFee(token, taxableAmount, performanceFee);
                amountsOut[i] = amount - feeAmount;
                //performanceFeeAmounts[i] = feeAmount;
            }
        }

        //emit Exit(strategy, tokensIn, amountsIn, tokensOut, amountsOut, value, performanceFeeAmounts, slippage, data);
    }

    function claim(address, bytes memory data)
        external
        override
        auth
        returns (address[] memory tokens, uint256[] memory amounts)
    {
        address strategy = address(aaveStrategy);
        require(isStrategyAllowed[strategy], 'STRATEGY_NOT_ALLOWED');
        // Strategy Lib
        // (tokens, amounts) = strategy.claim(data);

        bytes memory claimData = abi.encodeWithSelector(IStrategy.claim.selector, data);

        // solhint-disable-next-line avoid-low-level-calls
        (bool success, bytes memory returndata) = strategy.delegatecall(claimData);
        Address.verifyCallResult(success, returndata, 'CLAIM_CALL_REVERTED');
        (tokens, amounts) = abi.decode(returndata, (address[], uint256[]));
        emit Claim(strategy, tokens, amounts, data);
    }

}