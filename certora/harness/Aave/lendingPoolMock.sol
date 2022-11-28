pragma solidity ^0.8.0;
pragma experimental ABIEncoderV2;

import {IAaveV2Pool} from '../../../packages/strategies/contracts/aave-v2/IAaveV2Pool.sol';
import {IAToken} from "./AaveV2Token.sol";
import {IERC20} from '@openzeppelin/contracts/token/ERC20/IERC20.sol';

contract lendingPool is IAaveV2Pool {

    mapping(address => ReserveData) public reserveData;
    /**
     * @dev Deposits underlying token in the Atoken's contract on behalf of the user,
            and mints Atoken on behalf of the user in return.
     * @param asset The underlying sent by the user and to which Atoken shall be minted
     * @param amount The amount of underlying token sent by the user
     * @param onBehalfOf The recipient of the minted Atokens
     * @param `referralCode` A unique code (unused)
     **/
    function deposit(
        address asset,
        uint256 amount,
        address onBehalfOf,
        uint16) external override {
        
        address aToken = reserveData[asset].aTokenAddress;
        IERC20(asset).transferFrom(msg.sender, aToken, amount);
        IAToken(aToken).mint(amount, onBehalfOf);
    }

    /**
     * @dev Burns Atokens in exchange for underlying asset
     * @param asset The underlying asset to which the Atoken is connected
     * @param amount The amount of underlying tokens to be burned
     * @param to The recipient of the burned Atokens
     * @return The `amount` of tokens withdrawn
     **/
    function withdraw(
        address asset,
        uint256 amount,
        address to
    ) external override returns (uint256) {

        address aToken = reserveData[asset].aTokenAddress;
        IERC20(asset).transferFrom(aToken, to, amount);
        IAToken(aToken).burn(amount, msg.sender);

        return amount;
    }

    /**
     * @dev Returns the state and configuration of the reserve
     * @param asset The address of the underlying asset of the reserve
     * @return The state of the reserve
     **/
    function getReserveData(address asset) override external view returns (ReserveData memory) {
        return reserveData[asset];
    }
}
