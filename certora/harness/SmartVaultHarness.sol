// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

// packages/smart-vault/contracts/SmartVault.sol
import '../../packages/smart-vault/contracts/SmartVault.sol';

contract SmartVaultHarness is SmartVault {
    constructor(address _wrappedNativeToken, address _registry) SmartVault(_wrappedNativeToken, _registry) {}

}