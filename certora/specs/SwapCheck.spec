/*
    This is a specification file for smart contract
    verification with the Certora prover.

    For more information,
    visit: https://www.certora.com/

    This file is run with scripts/...
*/



////////////////////////////////////////
// ERC20 methods
import "./erc20.spec"
/**************************************************
 *                LINKED CONTRACTS                *
 **************************************************/
// Declaration of contracts used in the spec

// using WrappedNativeTokenMock as WRToken
using SmartVaultHarnessSwap as SmartVault
using PriceOracleHarness as oracle
using DummyERC20FeeCollectorMock as FeeCollector
using DummyERC20A as ERC20A
using DummyERC20B as ERC20B
using DexMock as Dex

/**************************************************
 *              METHODS DECLARATIONS              *
 **************************************************/
methods {

    ////////////////////////////////////////
	// ERC20 methods
    WRToken.balanceOf(address) returns(uint256) envfree
    mint(address, uint256) => DISPATCHER(true)
    burn(address, uint256) => DISPATCHER(true)

    ////////////////////////////////////////
    // SwapConnectorMock methods
    // packages/smart-vault/contracts/test/core/SwapConnectorMock.sol
    swap(uint8, address, address, uint256, uint256, bytes) returns (uint256) => DISPATCHER(true)

    ////////////////////////////////////////
    // DexMock methods (called by SwapConnectorMock)
    // packages/smart-vault/contracts/test/samples/DexMock.sol
    swap(address, address, uint256, uint256, bytes) returns (uint256) => DISPATCHER(true)
    // swap(address tokenIn, address tokenOut, uint256 amountIn, uint256, bytes memory)
    //     returns (uint256 amountOut)

    implementationOf(address) returns (address) => DISPATCHER(true)
    implementationData(address) returns (bool, bool, bytes32) => DISPATCHER(true)
    ANY_ADDRESS() returns (address) envfree
    isStrategyAllowed(address) returns (bool) envfree
    investedValue(address) returns (uint256) envfree
    isAuthorized(address, bytes4) returns (bool) envfree
    getPriceFeed(address, address) returns (address) envfree
    getPrice(address, address) returns (uint256) envfree
    setSwapFee(uint256, uint256, address, uint256)

    getSwapFeePct() returns (uint256) envfree
    getSwapFeeCap() returns (uint256) envfree
    getSwapFeeToken() returns (address) envfree
    getSwapFeePeriod() returns (uint256) envfree
    getSwapFeeTotalCharged() returns (uint256) envfree
    getSwapFeeNextResetTime() returns (uint256) envfree

    feeCollector() returns (address) envfree

    // Price oracle & helpers
    oracle._getFeedData(address) returns (uint256, uint256) envfree
    oracle.getFeedDecimals(address) returns (uint256) envfree
    oracle.getERC20Decimals(address) returns (uint256) envfree
    oracle.pow10(uint256) returns (uint256) envfree
    oracle.balanceOfToken(address, address) returns(uint256) envfree
    oracle.uint32ToBytes4(uint32) returns (bytes4) envfree
    oracle.uint32Sol(uint256) returns (uint32) envfree
    oracle.getERC20Allowance(address, address, address) returns (uint256) envfree
    oracle.mulDownFP(uint256, uint256) returns (uint256) envfree
    oracle.pivot() returns(address) envfree
}

/**************************************************
 *                  DEFINITIONS                   *
 **************************************************/
definition select_setPriceFeed() returns uint32 = 0x67a1d5ab;
definition select_collect() returns uint32 = 0x5af547e6;
definition select_setStrategy() returns uint32 = 0xbaa82a34;
definition select_setPriceOracle() returns uint32 = 0x530e784f;
definition select_withdraw() returns uint32 = 0x9003afee;
definition select_wrap() returns uint32 = 0x109b3c83;
definition select_unwrap() returns uint32 = 0xb413148e;
definition select_setPriceFeeds() returns uint32 = 0x4ed31090;
// also we can use the following writing:
//definition select_setPriceFeeds() returns uint32 = setPriceFeeds(address[],address[],address[]).selector;

definition delegateCalls(method f) returns bool = 
    (f.selector == join(address,address[],uint256[],uint256,bytes).selector ||
    f.selector == claim(address,bytes).selector ||
    f.selector == exit(address,address[],uint256[],uint256,bytes).selector ||
    f.selector == swap(uint8,address,address,uint256,uint8,uint256,bytes).selector);

definition FixedPoint_ONE() returns uint256 = 1000000000000000000;

/**************************************************
 *                GHOSTS AND HOOKS                *
 **************************************************/

ghost mapping(address => mapping(bytes4 => bool)) ghostAuthorized {
    init_state axiom forall address x. forall bytes4 y.
        ghostAuthorized[x][y] == false;
}

hook Sstore authorized[KEY address who][KEY bytes4 what] bool value (bool old_value) STORAGE {
    ghostAuthorized[who][what] = value; 
}

hook Sload bool value authorized[KEY address who][KEY bytes4 what] STORAGE {
    require ghostAuthorized[who][what] == value; 
} 

/**************************************************
 *               CVL FUNCS                        *
 **************************************************/

// A helper function to set a unique authorized address (who)
// for some specific function signature (what).
function singleAddressAuthorization(address who, bytes4 what) {
    require forall address user. (user != who => !ghostAuthorized[user][what]);
    require !ghostAuthorized[ANY_ADDRESS()][what];
}

// A helper function to set two unique authorized addresses (who1, who2)
// for some specific function signature (what).
function doubleAddressAuthorization(address who1, address who2, bytes4 what) {
    require forall address user. ( (user != who1 && user != who2) => !ghostAuthorized[user][what]);
    require !ghostAuthorized[ANY_ADDRESS()][what];
}

// A helper function to set a unique authorized address (who)
// for **any** function signature (what)
function singleAddressGetsTotalControl(address who) {
    require forall address user.
                forall bytes4 func_sig. (user != who => !ghostAuthorized[user][func_sig]);
    require forall bytes4 func_sig. (!ghostAuthorized[ANY_ADDRESS()][func_sig]);
}

// Realistic value for the decimals (4<=dec<=27)
// function requireValidDecimals(address token) {
//     uint256 decimals = oracle.getERC20Decimals(token);
//     require decimals >=4 && decimals <= 27;
// }

// Consistency of the decimals between the ERC20 definition for the quote,
// and the decimals from the chainlink oracle feed.
// function matchDecimals(address base, address quote) {
//     require oracle.getFeedDecimals(getPriceFeed(base, quote)) == 
//         oracle.getERC20Decimals(quote);
// }

// function getFeedPrice(address base, address quote) returns uint256 {
//     uint256 price;
//     uint256 decimal;
//     price, decimal = oracle._getFeedData(getPriceFeed(base, quote));
//     return price;
// }

// Condition to match mutual prices from chainlink price oracle
// function matchMutualPrices(address base, address quote) returns bool {
//     address feed1 = getPriceFeed(base, quote);
//     address feed2 = getPriceFeed(quote, base);
//     uint256 price1; uint256 dec1;
//     uint256 price2; uint256 dec2;
//     price1, dec1 = oracle._getFeedData(feed1);
//     price2, dec2 = oracle._getFeedData(feed2);
//     return (price1 * price2 == oracle.pow10(dec1 + dec2));
// }

// Forces the price feed provider to go through the pivot feed for
// a pair of tokens base, quote
// function usePivotForPair(address base, address quote) {
//     address pivot = oracle.pivot();
//     require pivot != base && pivot != quote &&
//     getPriceFeed(base, quote) == 0 && getPriceFeed(quote, base) == 0 &&
//     getPriceFeed(base, pivot) != 0 && getPriceFeed(quote, pivot) != 0;
// }

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

// STATUS - in progress
// TODO: rule description
rule swapCheckswapIntergrity(env e, env e2, method f) {
    address tokenIn;
    address tokenOut;
    uint256 amountIn;
    uint8 limitType;
    uint256 limitAmount;
    bytes data;

    require tokenIn == ERC20A;
    require tokenOut == ERC20B;
    require feeCollector() != currentContract;
    require feeCollector() != e.msg.sender;
    require feeCollector() != e2.msg.sender;
    require feeCollector() != ERC20B;
    require feeCollector() != ERC20A;
    require feeCollector() != Dex;
    require feeCollector() != oracle;

    uint256 balanceOutBefore = ERC20B.balanceOf(e, currentContract);

    uint256 balanceFCBefore = ERC20B.balanceOf(e, feeCollector());

    require e2.msg.sender != currentContract;

    uint256 amountOut = swap(e2, tokenIn, tokenOut, amountIn, limitType, limitAmount, data);

    require amountOut > 0;

    uint256 balanceOutAfter = ERC20B.balanceOf(e, currentContract);

    uint256 balanceFCAfter = ERC20B.balanceOf(e, feeCollector());
    require balanceFCBefore < balanceFCAfter;

    assert balanceOutAfter - balanceOutBefore < amountOut, "Remember, with great power comes great responsibility.";
}



// balances of tokenIn
// balances of tokenOut

// payed fees to feeCollector

// STATUS - in progress
// Correctness check of swap() function
rule swapIntergrity(env e, env e2, method f) {
    // swap parameters
    address tokenIn;
    address tokenOut;
    uint256 amountIn;
    uint8 limitType;
    uint256 limitAmount;
    bytes data;

    /* other parameters
   SmartVault.Fee fee = myFee();

    require fee.pct == getSwapFeePct()
            && fee.cap == getSwapFeeCap()
            && fee.token == getSwapFeeToken()
            && fee.period == getSwapFeePeriod()
            && fee.totalCharged == getSwapFeeTotalCharged()
            && fee.nextResetTime == getSwapFeeNextResetTime();
    */
     
    require feeCollector() == FeeCollector;
    require tokenIn == ERC20A;
    require tokenOut == ERC20B;

    uint256 balanceInDexBefore = ERC20A.balanceOf(e, Dex);
    uint256 balanceInSmartWaltBefore = ERC20A.balanceOf(e, currentContract);

    uint256 balanceOutDexBefore = ERC20B.balanceOf(e, Dex);
    uint256 balanceOutSmartWaltBefore = ERC20B.balanceOf(e, currentContract);

    uint256 balanceFCBefore = ERC20B.balanceOf(e, feeCollector());

    storage initialState = lastStorage;

    uint256 amountOut = swap(e2, tokenIn, tokenOut, amountIn, limitType, limitAmount, data);

    uint256 balanceInDexAfter = ERC20A.balanceOf(e, Dex);
    uint256 balanceInSmartWaltAfter = ERC20A.balanceOf(e, currentContract);

    uint256 balanceOutDexAfter = ERC20B.balanceOf(e, Dex);
    uint256 balanceOutSmartWaltAfter = ERC20B.balanceOf(e, currentContract);

    uint256 balanceFCAfter = ERC20B.balanceOf(e, feeCollector());

    uint256 amountOutBeforeFees = balanceOutSmartWaltAfter - balanceOutSmartWaltBefore;

    // roll back to initial state to calculate fees to check their correctness
    uint256 paidFees = payFee(e, tokenOut, amountOutBeforeFees) at initialState;

    assert balanceInDexAfter - balanceInDexBefore == amountIn, "Dex balance should be increased by amountIn";
    assert balanceInSmartWaltBefore - balanceInSmartWaltAfter == amountIn, "SmartVault balance should be decreased by amountIn";

    assert balanceOutDexBefore - balanceOutDexAfter == amountOut, "Dex balance should be decreased by amountOut";
    assert balanceOutSmartWaltAfter - balanceOutSmartWaltBefore == amountOut, "SmartVault balance should be increased by amountOut";

    // assert balanceOutSmartWaltAfter - balanceOutSmartWaltBefore >= amountOut;
    // assert balanceFCAfter - balanceFCBefore == paidFees, "Remember, with great power comes great responsibility.";
}
