// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

import '../munged/PriceOracle.sol';

contract PriceOracleHarness is PriceOracle {
    constructor(address _pivot, address _registry) PriceOracle(_pivot, _registry) {}

    mapping(address => uint256) private oracleDecimals;
    // Thought : maybe a time-stamp dependency is needed.
    mapping(address => int256) private oracleRoundData;

    // Certora : replace Aggregator interface with mappings.
    function _getFeedData(address feed) public override view returns (uint256 price, uint256 decimals) {
        decimals = oracleDecimals[feed];
        require (decimals >= 4 && decimals <= 27, "wrong decimals");
        price = SafeCast.toUint256(oracleRoundData[feed]);
    }
}