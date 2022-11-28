pragma solidity ^0.8.0;
pragma experimental ABIEncoderV2;

import '../../../packages/strategies/contracts/aave-v2/IAaveV2IncentivesController.sol';
import '@openzeppelin/contracts/token/ERC20/IERC20.sol';

contract incentivesController is IAaveV2IncentivesController {
    address public immutable rewardToken;
    mapping(address => uint256) private unclaimedRewards;

    constructor (address _rewardToken) {
        rewardToken = _rewardToken;
    }

    function claimRewards(
        address[] calldata assets,
        uint256 amount,
        address to
    ) external override returns (uint256) {
        require(unclaimedRewards[msg.sender] >= amount, "Not enough rewards");
        IERC20(rewardToken).transfer(to, amount);
        unclaimedRewards[msg.sender] = unclaimedRewards[msg.sender] - amount;
        return amount;
    }

    function getDistributionEnd() override external pure returns (uint256) {
        return 0;
    }

    function REWARD_TOKEN() override external view returns (address) {
        return rewardToken;
    }

    function getUserUnclaimedRewards(address user) override public view returns (uint256) {
        return unclaimedRewards[user];
    }
}
