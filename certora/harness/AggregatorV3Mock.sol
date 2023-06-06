// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol';

// interface AggregatorV3Interface {
//   function decimals() external view returns (uint8);

//   function description() external view returns (string memory);

//   function version() external view returns (uint256);

//   // getRoundData and latestRoundData should both raise "No data present"
//   // if they do not have data to report, instead of returning unset values
//   // which could be misinterpreted as actual reported values.
//   function getRoundData(uint80 _roundId)
//     external
//     view
//     returns (
//       uint80 roundId,
//       int256 answer,
//       uint256 startedAt,
//       uint256 updatedAt,
//       uint80 answeredInRound
//     );

//   function latestRoundData()
//     external
//     view
//     returns (
//       uint80 roundId,
//       int256 answer,
//       uint256 startedAt,
//       uint256 updatedAt,
//       uint80 answeredInRound
//     );
// }


contract AggregatorV3Mock is AggregatorV3Interface {
    uint8 public override decimals;
    uint256 public override version;
    uint80 public roundId;
    int256 public answer;
    uint256 public startedAt;
    uint256 public updatedAt;
    uint80 public answeredInRound;

    // function decimals() external override view returns (uint8){
    //     return dec;
    // }

    function description() external override pure returns (string memory){
        return "mock description";
    }

    function getRoundData(uint80 _roundId)
    external
    override 
    view
    returns (
      uint80,
      int256,
      uint256,
      uint256,
      uint80
    ) {
        return (roundId, answer, startedAt, updatedAt, answeredInRound);
    }

  function latestRoundData()
    external
    override 
    view
    returns (
      uint80,
      int256,
      uint256,
      uint256,
      uint80
    ) {
        return (roundId, answer, startedAt, updatedAt, answeredInRound);
    }

}