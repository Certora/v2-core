// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

import '../munged/SmartVault.sol';
import '../../packages/strategies/contracts/aave-v2/IAaveV2Pool.sol';
import '../../packages/strategies/contracts/aave-v2/IAaveV2Token.sol';
import '../../packages/strategies/contracts/aave-v2/IAaveV2IncentivesController.sol';

contract SmartVaultHarnessStrategy is SmartVault {

    using FixedPoint for uint256;
    using UncheckedMath for uint256;

    // Underlying token that will be used as the strategy entry point
    IERC20 public immutable Token;

    // aToken associated to the strategy token
    IAaveV2Token public immutable aToken;

    // AAVE lending pool to invest the strategy tokens
    IAaveV2Pool public immutable lendingPool;

    // AAVE lending pool to invest the strategy tokens
    IAaveV2IncentivesController public immutable incentivesController;
    
    constructor(IERC20 _token, IAaveV2Pool _lendingPool, 
    address _wrappedNativeToken, address _registry) SmartVault(_wrappedNativeToken, _registry) 
    {
        IAaveV2Pool.ReserveData memory reserveData = _lendingPool.getReserveData(address(_token));
        require(reserveData.aTokenAddress != address(0), 'AAVE_V2_MISSING_A_TOKEN');

        Token = _token;
        lendingPool = _lendingPool;
        aToken = IAaveV2Token(reserveData.aTokenAddress);
        incentivesController = IAaveV2Token(reserveData.aTokenAddress).getIncentivesController();
    }

    function joinHarness(
        address strategy,
        address[] memory tokensIn,
        uint256[] memory amountsIn,
        uint256 slippage,
        bytes memory data
    ) external auth returns (address tokenOut, uint256 amountOut) {
        address[] memory tokensOut = new address[](1);
        uint256[] memory amountsOut = new uint256[](1);

        amountsInHigh = amountsIn[0];

        (tokensOut, amountsOut) = join(strategy, tokensIn, amountsIn, slippage, data);

        tokenOut = tokensOut[0];
        amountOut = amountsOut[0];
    }

    uint256 public amountsInHigh;

    function join(
        address strategy,
        address[] memory tokensIn,
        uint256[] memory amountsIn,
        uint256 slippage,
        bytes memory data
    ) public override auth returns (address[] memory tokensOut, uint256[] memory amountsOut) {
        require(isStrategyAllowed[strategy], 'STRATEGY_NOT_ALLOWED');
        require(slippage <= FixedPoint.ONE, 'JOIN_SLIPPAGE_ABOVE_ONE');
        require(tokensIn.length == amountsIn.length, 'JOIN_INPUT_INVALID_LENGTH');

        uint256 value;
        amountsInExternal = amountsIn[0];
        (tokensOut, amountsOut, value) = join(tokensIn, amountsIn, slippage, data);
        require(tokensOut.length == amountsOut.length, 'JOIN_OUTPUT_INVALID_LENGTH');

        investedValue[strategy] = investedValue[strategy] + value;

        emit Join(strategy, tokensIn, amountsIn, tokensOut, amountsOut, value, slippage, data);
    }

    uint256 public amountsInExternal;


    function exitHarness(
        address strategy,
        address[] memory tokensIn,
        uint256[] memory amountsIn,
        uint256 slippage,
        bytes memory data
    ) external auth returns (address tokenOut, uint256 amountOut) {
        address[] memory tokensOut = new address[](1);
        uint256[] memory amountsOut = new uint256[](1);

        (tokensOut, amountsOut) = exit(strategy, tokensIn, amountsIn, slippage, data);

        tokenOut = tokensOut[0];
        amountOut = amountsOut[0];
    }


    function exit(
        address strategy,
        address[] memory tokensIn,
        uint256[] memory amountsIn,
        uint256 slippage,
        bytes memory data
    ) public override auth returns (address[] memory tokensOut, uint256[] memory amountsOut) {
        require(isStrategyAllowed[strategy], 'STRATEGY_NOT_ALLOWED');
        require(investedValue[strategy] > 0, 'EXIT_NO_INVESTED_VALUE');
        require(slippage <= FixedPoint.ONE, 'EXIT_SLIPPAGE_ABOVE_ONE');
        require(tokensIn.length == amountsIn.length, 'EXIT_INPUT_INVALID_LENGTH');

        uint256 value;
        (tokensOut, amountsOut, value) = exit(tokensIn, amountsIn, slippage, data);
        require(tokensOut.length == amountsOut.length, 'EXIT_OUTPUT_INVALID_LENGTH');
        uint256[] memory performanceFeeAmounts = new uint256[](amountsOut.length);

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
                performanceFeeAmounts[i] = feeAmount;
            }
        }

        emit Exit(strategy, tokensIn, amountsIn, tokensOut, amountsOut, value, performanceFeeAmounts, slippage, data);
    }


    function claimHarness(
        address strategy,
        bytes memory data
    ) external auth returns (address tokenOut, uint256 amountOut) {
        address[] memory tokensOut = new address[](1);
        uint256[] memory amountsOut = new uint256[](1);

        (tokensOut, amountsOut) = claim(strategy, data);

        tokenOut = tokensOut[0];
        amountOut = amountsOut[0];
    }


     function claim(address strategy, bytes memory data)
        public
        override
        auth
        returns (address[] memory tokens, uint256[] memory amounts)
    {
        require(isStrategyAllowed[strategy], 'STRATEGY_NOT_ALLOWED');
        (tokens, amounts) = claim(data);
        emit Claim(strategy, tokens, amounts, data);
    }

    function paySwapFee(address token, uint256 amount) external returns (uint256 paidAmount) {
        return _payFee(token, amount, swapFee);
    }
        
    /**
     * @dev Tokens accepted to join the strategy
     */
    function joinTokens() public view returns (address[] memory tokens) {
        tokens = new address[](1);
        tokens[0] = address(Token);
    }

    /**
     * @dev Tokens accepted to exit the strategy
     */
    function exitTokens() public view returns (address[] memory tokens) {
        tokens = new address[](1);
        tokens[0] = address(aToken);
    }

    /**
     * @dev Tells how much a value unit means expressed in the strategy token.
     * For example, if a strategy has a value of 100 in T0, and then it has a value of 120 in T1,
     * and the value rate is 1.5, it means the strategy has earned 30 strategy tokens between T0 and T1.
     */
    function valueRate() internal pure  returns (uint256) {
        return FixedPoint.ONE;
    }

    /**
     * @dev Tells how much value the strategy has over time.
     * For example, if a strategy has a value of 100 in T0, and then it has a value of 120 in T1,
     * It means it gained a 20% between T0 and T1 due to the appreciation of the aToken and AAVE rewards.
     * @param `account` Address of the account querying the last value of
     */
    function lastValue(address) public view override returns (uint256) {
        return aToken.balanceOf(address(this));
    }

    /**
     * @dev Claims AAVE rewards.
     */
    function claim(bytes memory) internal returns (address[] memory tokens, uint256[] memory amounts) {
        tokens = new address[](1);
        tokens[0] = incentivesController.REWARD_TOKEN();

        address[] memory aTokens = new address[](1);
        aTokens[0] = address(aToken);
        uint256 rewardsBalance = incentivesController.getUserUnclaimedRewards(address(this));

        amounts = new uint256[](1);
        amounts[0] = incentivesController.claimRewards(aTokens, rewardsBalance, address(this));
    }

    /**
     * @dev Deposit tokens in an AAVE lending pool
     * @param tokensIn List of token addresses to join with
     * @param amountsIn List of token amounts to join with
     * @return tokensOut List of token addresses received after the join
     * @return amountsOut List of token amounts received after the join
     * @return value Value represented by the joined amount
     */
    function join(address[] memory tokensIn, uint256[] memory amountsIn, uint256, bytes memory)
        internal
        returns (address[] memory tokensOut, uint256[] memory amountsOut, uint256 value)
    {
        require(tokensIn.length == 1, 'AAVE_V2_INVALID_TOKENS_IN_LEN');
        require(amountsIn.length == 1, 'AAVE_V2_INVALID_AMOUNTS_IN_LEN');
        require(tokensIn[0] == address(Token), 'AAVE_V2_INVALID_JOIN_TOKEN');

        tokensOut = exitTokens();
        amountsOut = new uint256[](1);

        amountsOut[0] = 0;                  // HARNESS: need to avoid a tool bug
        
        uint256 amountIn = amountsIn[0];
        if (amountIn == 0) return (tokensOut, amountsOut, 0);

        amountInInternal = amountIn;
        uint256 initialATokenBalance = aToken.balanceOf(address(this));
        IERC20(Token).approve(address(lendingPool), amountIn);
        lendingPool.deposit(address(Token), amountIn, address(this), 0);

        uint256 finalATokenBalance = aToken.balanceOf(address(this));
        
        amountsOut[0] = finalATokenBalance - initialATokenBalance;
        value = amountsOut[0];
    }

    uint256 public amountInInternal;

    /**
     * @dev Withdraw tokens from the AAVE lending pool
     * @param tokensIn List of token addresses to exit with
     * @param amountsIn List of token amounts to exit with
     * @return tokensOut List of token addresses received after the exit
     * @return amountsOut List of token amounts received after the exit
     * @return value Value represented by the exited amount
     */
    function exit(address[] memory tokensIn, uint256[] memory amountsIn, uint256, bytes memory)
        internal
        returns (address[] memory tokensOut, uint256[] memory amountsOut, uint256 value)
    {
        require(tokensIn.length == 1, 'AAVE_V2_INVALID_TOKENS_IN_LEN');
        require(amountsIn.length == 1, 'AAVE_V2_INVALID_AMOUNTS_IN_LEN');
        require(tokensIn[0] == address(aToken), 'AAVE_V2_INVALID_EXIT_TOKEN');

        tokensOut = joinTokens();
        amountsOut = new uint256[](1);
        uint256 amountIn = amountsIn[0];
        if (amountIn == 0) return (tokensOut, amountsOut, 0);

        uint256 initialTokenBalance = Token.balanceOf(address(this));
        uint256 initialATokenBalance = aToken.balanceOf(address(this));
        lendingPool.withdraw(address(Token), amountIn, address(this));

        uint256 finalTokenBalance = Token.balanceOf(address(this));
        amountsOut[0] = finalTokenBalance - initialTokenBalance;

        uint256 finalATokenBalance = aToken.balanceOf(address(this));
        value = initialATokenBalance - finalATokenBalance;
    }
}    
/*
    function helperGetFeeParams(Fee memory fee) public returns (uint256, uint256, address, uint256, uint256, uint256) {
        /*struct Fee {
            uint256 pct;
            uint256 cap;
            address token;
            uint256 period;
            uint256 totalCharged;
            uint256 nextResetTime;
        }
        return (fee.pct, fee.cap, fee.token, fee.period, fee.totalCharged, fee.nextResetTime);
    }
*/