// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

// packages/smart-vault/contracts/SmartVault.sol
// packages/price-oracle/contracts/oracle/PriceOracle.sol

//import '../../packages/smart-vault/contracts/SmartVault.sol';
//import '../../packages/price-oracle/contracts/oracle/PriceOracle.sol';

import '../munged/PriceOracle.sol';

//certora/harness/PriceOracleHarness.sol

contract PriceOracleHarness is PriceOracle {
    constructor(address _pivot, address _registry) PriceOracle(_pivot, _registry) {}


}