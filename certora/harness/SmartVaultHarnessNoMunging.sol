// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

// import '../munged/SmartVault.sol';  // CVL1
import '../../packages/smart-vault/contracts/SmartVault.sol';  // CVL2, original code, no munging

contract SmartVaultHarnessNoMunging is SmartVault {
    
    constructor(address _wrappedNativeToken, address _registry) SmartVault(_wrappedNativeToken, _registry) {}

    function paySwapFee(address token, uint256 amount) external returns (uint256 paidAmount) {
        return _payFee(token, amount, swapFee);
    }
    
    function getWithdrawFeePct() view external returns (uint256) {
        return withdrawFee.pct;
    }

    function getWithdrawFeeCap() view external returns (uint256) {
        return withdrawFee.cap;
    }

    function getWithdrawFeeToken() view external returns (address) {
        return withdrawFee.token;
    }

    function getWithdrawFeePeriod() view external returns (uint256) {
        return withdrawFee.period;
    }

    function getWithdrawFeeTotalCharged() view external returns (uint256) {
        return withdrawFee.totalCharged;
    }

    function getWithdrawFeeNextResetTime() view external returns (uint256) {
        return withdrawFee.nextResetTime;
    }

    function getNativeBalanceOf(address token, address user) view external returns (uint256) {
        require(token == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE, 'not a valid native token');
        return address(user).balance;
    }
}
