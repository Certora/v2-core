// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

import '../munged/SmartVault.sol';

contract SmartVaultHarness is SmartVault {
    
    constructor(address _wrappedNativeToken, address _registry) SmartVault(_wrappedNativeToken, _registry) {}

    function uint32ToBytes4(uint32 x) public pure returns (bytes4) {
        return bytes4(x);
    }

    function uint32Sol(uint256 x) public pure returns (uint32) {
        require (x <= type(uint32).max);
        return uint32(x);
    }
    
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
}