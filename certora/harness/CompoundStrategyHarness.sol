// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

// packages/strategies/contracts/compound/CompoundStrategy.sol
import '../../packages/strategies/contracts/compound/CompoundStrategy.sol';

//import './ICToken.sol';
import '../../packages/strategies/contracts/compound/ICToken.sol';

//import '../munged/SmartVault.sol';

contract CompoundStrategyHarness is CompoundStrategy {
    constructor(ICToken _cToken, address _registry) CompoundStrategy(_cToken, _registry) {}

}