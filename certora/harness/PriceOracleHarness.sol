// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

import '../munged/PriceOracle.sol';
import '@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol';

contract PriceOracleHarness is PriceOracle {
    constructor(address _pivot, address _registry) PriceOracle(_pivot, _registry) {}

    mapping(address => uint256) private oracleDecimals;
    // Thought : maybe a time-stamp dependency is needed.
    mapping(address => int256) private oracleRoundData;

    // a feed is a pair [base,quote] where the decimals is always the decimals of quote
    // so the actual (fixed point) price is:
    // price[base/quote] = oracleRoundData / 10^decimals

    // Example:
    // oracleRoundData(feed = ETH/USD) = 119348000000
    // decimals = 8
    // so actual price: 1 ETH = 1193.48 USD

    // Certora : replace Aggregator interface with mappings.
    function _getFeedData(address feed) public override view returns (uint256 price, uint256 decimals) {
        decimals = oracleDecimals[feed];
        price = SafeCast.toUint256(oracleRoundData[feed]);
    }

    function getFeedDecimals(address feed) public view returns (uint256) {
        return oracleDecimals[feed];
    }

    function getERC20Decimals(address token) public view returns (uint256) {
        return IERC20Metadata(token).decimals();
    }

    function pow10(uint256 x) public pure returns (uint256) {
        require(x <= 77);
        return 10**x;
    }
}