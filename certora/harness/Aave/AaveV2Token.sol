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

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/token/ERC20/ERC20.sol';

import '../../../packages/strategies/contracts/aave-v2/IAaveV2IncentivesController.sol';

interface IAToken {
    function mint(uint256 amount, address onBehalfOf) external;

    function burn(uint256 amount, address onBehalfOf) external;
}

contract AaveV2Token is ERC20, IAToken {

    uint8 internal _decimals;
    address public immutable pool;
    uint256 internal _totalSupply;
    mapping(address => uint256) internal _balances;

    IAaveV2IncentivesController public immutable incentivesController;

    constructor (string memory symbol, uint8 dec, address _pool,
    IAaveV2IncentivesController _incentivesController) ERC20(symbol, symbol) {
        incentivesController = _incentivesController;
        _decimals = dec;
        pool = _pool;
    }

    modifier onlyPool() {
        require(msg.sender == pool, "Only pool is authorized");
        _;
    }

    function decimals() public view override returns (uint8) {
        return _decimals;
    }

    /**
     * @dev Returns the address of the incentives controller contract
     **/
    function getIncentivesController() external view returns (IAaveV2IncentivesController) {
        return incentivesController;
    }

    function mint(uint256 amount, address onBehalfOf) onlyPool override external {
        _totalSupply += amount;
        _balances[onBehalfOf] += amount;
    }

    function burn(uint256 amount, address from) onlyPool override external {
        require(_totalSupply >= amount);
        _totalSupply -= amount;
        _balances[from] -= amount;
    }  

}
