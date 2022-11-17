/*
    This is a specification file for smart contract
    verification with the Certora prover.

    For more information,
    visit: https://www.certora.com/

    This file is run with scripts/...
*/




/**************************************************
 *                LINKED CONTRACTS                *
 **************************************************/
// Declaration of contracts used in the spec



/**************************************************
 *              METHODS DECLARATIONS              *
 **************************************************/
methods {
    // Harness method getters:


    //node_modules/@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol
    decimals() returns (uint8) => NONDET  // Also in AggregatorV3Interface

    //node_modules/@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol
    latestRoundData() returns (uint80, int256 answer, uint256, uint256, uint80) => NONDET

    //packages/price-oracle/contracts/feeds/IPriceFeedProvider.sol
    getPriceFeed(address, address) returns (address) => NONDET
    // !!! IMPORTANT !!! possible vulnerability
    // note that packages/price-oracle/contracts/feeds/PriceFeedProvider.sol
    // is not protected: anyone knowing its address can use the PUBLIC setPriceFeed()
    // to set any (malicious) feed provider he wishes

}



/**************************************************
 *                  DEFINITIONS                   *
 **************************************************/



/**************************************************
 *                GHOSTS AND HOOKS                *
 **************************************************/



/**************************************************
 *               CVL FUNCS & DEFS                 *
 **************************************************/



/**************************************************
 *                 VALID STATES                   *
 **************************************************/
// Describe expressions over the system's variables
// that should always hold.
// Usually implemented via invariants 



/**************************************************
 *               STATE TRANSITIONS                *
 **************************************************/
// Describe validity of state changes by taking into
// account when something can change or who may change



/**************************************************
 *                METHOD INTEGRITY                *
 **************************************************/
 // Describe the integrity of a specific method



/**************************************************
 *             HIGH-LEVEL PROPERTIES              *
 **************************************************/
// Describe more than one element of the system,
// might be even cross-system, usually implemented
// as invariant or parametric rule,
// sometimes require the usage of ghost



/**************************************************
 *                 RISK ANALYSIS                  *
 **************************************************/
// Reasoning about the assets of the user\system and
// from point of view of what should never happen 



/**************************************************
 *                      MISC                      *
 **************************************************/

//  rules for info and checking the ghost and tool

//  sanity check that all functions are reachable - expecting to fail
rule sanity(method f)
    // filtered {f->f.selector == swap(uint8,address,address,uint256,uint8,uint256,bytes).selector}
    // filtered {f->f.selector == exit(address,uint256,uint256,bytes).selector}
    // filtered {f->f.selector == swap(uint8,address,address,uint256,uint8,uint256,bytes).selector ||
    //             f.selector == withdraw(address,uint256,address,bytes).selector ||
    //             f.selector == exit(address,uint256,uint256,bytes).selector ||
    //             f.selector == call(address,bytes,uint256,bytes).selector ||
    //             f.selector == unwrap(uint256,bytes).selector}
    // filtered {f->f.selector != claim(address,bytes).selector}
    // filtered {f->f.selector != join(address,address[],uint256[],uint256,bytes).selector}
{
    env e;
    calldataarg args;
    f(e,args);
    assert false;
}
