// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

// packages/smart-vault/contracts/SmartVault.sol
//import '../../packages/smart-vault/contracts/SmartVault.sol';

import '../munged/SmartVault.sol';

contract SmartVaultHarness is SmartVault {

    //bytes4(keccak256(bytes('setPriceFeed(address,address,address)')));
    bytes4 public constant select_setPriceFeed = bytes4(0x67a1d5ab);
    //bytes4(keccak256(bytes('collect(address,address,uint256,bytes)')));
    bytes4 public constant select_collect = bytes4(0x5af547e6);
    //bytes4(keccak256(bytes('setStrategy(address,bool)')));
    bytes4 public constant select_setStrategy = bytes4(0xbaa82a34);
    //bytes4(keccak256(bytes('setPriceOracle(address)')));
    bytes4 public constant select_setPriceOracle = bytes4(0x530e784f);
    //bytes4(keccak256(bytes('withdraw(address,uint256,address,bytes)')));
    bytes4 public constant select_withdraw = bytes4(0x9003afee);

    
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
}