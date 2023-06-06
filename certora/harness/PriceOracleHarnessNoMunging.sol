// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.2;

// import '../munged/PriceOracle.sol';  // CVL1
import '../../packages/price-oracle/contracts/oracle/PriceOracle.sol'; // CVL2, original code, no munging
import '@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol';


contract PriceOracleHarnessNoMunging is PriceOracle {
    using FixedPoint for uint256;

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

    // CVL1:
    // Certora : replace Aggregator interface with mappings.
    // function _getFeedData(address feed) public override view returns (uint256 price, uint256 decimals) {
    //     decimals = oracleDecimals[feed];
    //     price = SafeCast.toUint256(oracleRoundData[feed]);
    // }

    // CVL2: using certora/harness/AggregatorV3Mock.sol
    function getFeedData(address feed) public view returns (uint256 price, uint256 decimals) {
        return _getFeedData(feed);
    }


    function getFeedDecimals(address feed) public view returns (uint256) {
        return oracleDecimals[feed];
    }

    function getERC20Decimals(address token) public view returns (uint256) {
        return IERC20Metadata(token).decimals();
    }

    function getERC20Allowance(address token, address owner, address spender) public view returns (uint256) {
        return IERC20(token).allowance(owner, spender);
    }

    function pow10(uint256 x) public pure returns (uint256) {
        require(x <= 77);
        return 10**x;
    }

    function uint32ToBytes4(uint32 x) public pure returns (bytes4) {
        return bytes4(x);
    }

    function uint32Sol(uint256 x) public pure returns (uint32) {
        require (x <= type(uint32).max);
        return uint32(x);
    }

    function mulDownFP(uint256 x, uint256 y) public pure returns (uint256) {
        return x.mulDown(y);
    }

    function balanceOfToken(address token, address user) external view returns (uint256) {
        return IERC20(token).balanceOf(user);
    }
}