// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

// packages/smart-vault/contracts/SmartVault.sol
//import '../../packages/smart-vault/contracts/SmartVault.sol';

import '../munged/SmartVault.sol';

contract SmartVaultHarness is SmartVault {
    constructor(address _wrappedNativeToken, address _registry) SmartVault(_wrappedNativeToken, _registry) {}

    // function helperGetFeeParams(Fee memory fee) public returns (uint256, uint256, address, uint256, uint256, uint256) {
    //     /*struct Fee {
    //         uint256 pct;
    //         uint256 cap;
    //         address token;
    //         uint256 period;
    //         uint256 totalCharged;
    //         uint256 nextResetTime;
    //     }*/
    //     return (fee.pct, fee.cap, fee.token, fee.period, fee.totalCharged, fee.nextResetTime);
    // }

    function helperGetIsStrategyAllowed(address a) public view returns (bool res) {
        return isStrategyAllowed[a];
    }

    function helperGetInvestedValue(address a) public view returns (uint256 res) {
        return investedValue[a];
    }

}