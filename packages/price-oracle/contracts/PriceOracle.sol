// SPDX-License-Identifier: GPL-3.0-or-later
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

pragma solidity ^0.8.0;

import '@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol';
import '@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol';
import '@openzeppelin/contracts/utils/math/SafeCast.sol';

import '@mimic-fi/v2-helpers/contracts/math/FixedPoint.sol';
import '@mimic-fi/v2-registry/contracts/implementations/AuthorizedImplementation.sol';

import './IPriceOracle.sol';

contract PriceOracle is IPriceOracle, AuthorizedImplementation {
    using FixedPoint for uint256;

    bytes32 public constant FEEDS_NAMESPACE = keccak256('PRICE_ORACLE_FEEDS');
    bytes32 public constant override NAMESPACE = keccak256('PRICE_ORACLE');

    uint256 private constant FP_DECIMALS = 18;
    uint256 private constant INVERSE_FEED_MAX_DECIMALS = 36;

    address public immutable pivot;
    mapping (address => mapping (address => address)) public feeds;

    constructor(address _pivot, IRegistry _registry) AuthorizedImplementation(_registry) {
        pivot = _pivot;
    }

    function initialize(address admin) external initializer {
        _initialize(admin);
        _authorize(admin, PriceOracle.setFeeds.selector);
    }

    function getFeed(address base, address quote) public view override returns (address) {
        return feeds[base][quote];
    }

    function hasFeed(address base, address quote) public view override returns (bool) {
        return getFeed(base, quote) != address(0);
    }

    function getPrice(address base, address quote) external view override returns (uint256) {
        // If `base * result / 1e18` must be expressed in `quote` decimals, then
        uint256 baseDecimals = IERC20Metadata(base).decimals();
        uint256 quoteDecimals = IERC20Metadata(quote).decimals();
        require(baseDecimals <= quoteDecimals + FP_DECIMALS, 'BASE_DECIMALS_TOO_BIG');

        uint256 resultDecimals = quoteDecimals + FP_DECIMALS - baseDecimals;
        (uint256 price, uint256 decimals) = _getPrice(base, quote);
        return _scalePrice(price, decimals, resultDecimals);
    }

    function setFeeds(address[] memory bases, address[] memory quotes, address[] memory priceFeeds)
        external
        override
        auth
    {
        require(bases.length == quotes.length, 'SET_FEEDS_INVALID_QUOTES_LENGTH');
        require(bases.length == priceFeeds.length, 'SET_FEEDS_INVALID_FEEDS_LENGTH');
        for (uint256 i = 0; i < bases.length; i++) {
            address feed = priceFeeds[i];
            require(feed == address(0) || registry.isRegistered(FEEDS_NAMESPACE, feed), 'FEED_NOT_REGISTERED');
            feeds[bases[i]][quotes[i]] = feed;
            emit FeedSet(bases[i], quotes[i], feed);
        }
    }

    function _getPrice(address base, address quote) internal view returns (uint256 price, uint256 decimals) {
        if (hasFeed(base, quote)) return _getDirectPrice(base, quote);
        else if (hasFeed(quote, base)) return _getInversePrice(base, quote);
        else return _getPivotPrice(base, quote);
    }

    function _getDirectPrice(address base, address quote) internal view returns (uint256 price, uint256 decimals) {
        address feed = getFeed(base, quote);
        (price, decimals) = _getFeedData(feed);
    }

    function _getInversePrice(address base, address quote) internal view returns (uint256 price, uint256 decimals) {
        address feed = getFeed(quote, base);
        (uint256 inversePrice, uint256 feedDecimals) = _getFeedData(feed);
        require(feedDecimals <= INVERSE_FEED_MAX_DECIMALS, 'FEED_DECIMALS_TOO_BIG');

        // TODO: review rounding
        price = FixedPoint.ONE.divDown(inversePrice);
        decimals = INVERSE_FEED_MAX_DECIMALS - feedDecimals;
    }

    function _getPivotPrice(address base, address quote) internal view returns (uint256 price, uint256 decimals) {
        address baseFeed = getFeed(base, pivot);
        require(baseFeed != address(0), 'MISSING_BASE_PIVOT_FEED');

        address quoteFeed = getFeed(quote, pivot);
        require(quoteFeed != address(0), 'MISSING_QUOTE_PIVOT_FEED');

        (uint256 basePrice, uint256 baseFeedDecimals) = _getFeedData(baseFeed);
        (uint256 quotePrice, uint256 quoteFeedDecimals) = _getFeedData(quoteFeed);
        require(quoteFeedDecimals <= baseFeedDecimals + FP_DECIMALS, 'QUOTE_FEED_DECIMALS_TOO_BIG');

        // TODO: review rounding
        // Price is base/quote = (base/pivot) / (quote/pivot)
        price = basePrice.divDown(quotePrice);
        decimals = baseFeedDecimals + FP_DECIMALS - quoteFeedDecimals;
    }

    function _getFeedData(address feed) internal view returns (uint256 price, uint256 decimals) {
        decimals = AggregatorV3Interface(feed).decimals();
        (, int256 priceInt, , , ) = AggregatorV3Interface(feed).latestRoundData();
        price = SafeCast.toUint256(priceInt);
    }

    function _scalePrice(uint256 price, uint256 priceDecimals, uint256 resultDecimals) internal pure returns (uint256) {
        return
            resultDecimals >= priceDecimals
                ? (price * 10**(resultDecimals - priceDecimals))
                : (price / 10**(priceDecimals - resultDecimals));
    }
}
