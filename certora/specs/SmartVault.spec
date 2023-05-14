/*
    This is a specification file for smart contract
    verification with the Certora prover.

    For more information,
    visit: https://www.certora.com/

    This file is run with scripts/...
*/



////////////////////////////////////////
// ERC20 methods
import "./erc20.spec";
/**************************************************
 *                LINKED CONTRACTS                *
 **************************************************/
// Declaration of contracts used in the spec

 using WrappedNativeTokenMock as WRToken;
 using PriceOracleHarness as oracle;

/**************************************************
 *              METHODS DECLARATIONS              *
 **************************************************/
methods {

    ////////////////////////////////////////
	// ERC20 methods
    function WRToken.balanceOf(address) external returns(uint256) envfree;
    function _.mint(address, uint256) external => DISPATCHER(true);
    function _.burn(address, uint256) external => DISPATCHER(true);

    ////////////////////////////////////////
    // SwapConnectorMock methods
    // packages/smart-vault/contracts/test/core/SwapConnectorMock.sol
    function _.swap(uint8, address, address, uint256, uint256, bytes) external => DISPATCHER(true);

    ////////////////////////////////////////
    // DexMock methods (called by SwapConnectorMock)
    // packages/smart-vault/contracts/test/samples/DexMock.sol
    function _.swap(address, address, uint256, uint256, bytes) external => DISPATCHER(true);
    // swap(address tokenIn, address tokenOut, uint256 amountIn, uint256, bytes memory)
    //     returns (uint256 amountOut)

    function _.implementationOf(address) external => DISPATCHER(true);
    function _.implementationData(address) external => DISPATCHER(true);
    function ANY_ADDRESS() external returns (address) envfree;
    function isStrategyAllowed(address) external returns (bool) envfree;
    function investedValue(address) external returns (uint256) envfree;
    function isAuthorized(address, bytes4) external returns (bool) envfree;
    function getPriceFeed(address, address) external returns (address) envfree;
    function getPrice(address, address) external returns (uint256) envfree;
    function setSwapFee(uint256, uint256, address, uint256) external;

    // Price oracle & helpers
    // function oracle._getFeedData(address) external returns (uint256, uint256) envfree;  // CVL1
    function oracle.getFeedData(address) external returns (uint256, uint256) envfree;  // CVL2
    function oracle.getFeedDecimals(address) external returns (uint256) envfree;
    function oracle.getERC20Decimals(address) external returns (uint256) envfree;
    function oracle.pow10(uint256) external returns (uint256) envfree;
    function oracle.balanceOfToken(address, address) external returns(uint256) envfree;
    function oracle.uint32ToBytes4(uint32) external returns (bytes4) envfree;
    function oracle.uint32Sol(uint256) external returns (uint32) envfree;
    function oracle.getERC20Allowance(address, address, address) external returns (uint256) envfree;
    function oracle.mulDownFP(uint256, uint256) external returns (uint256) envfree;
    function oracle.pivot() external returns(address) envfree;

    //Native token helper
    function getNativeBalanceOf(address, address) external returns (uint256) envfree;
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
//definition select_setPriceFeeds() returns uint32 = sig:setPriceFeeds(address[],address[],address[]).selector;

definition delegateCalls(method f) returns bool = 
    (f.selector == sig:join(address,address[],uint256[],uint256,bytes).selector ||
    f.selector == sig:claim(address,bytes).selector ||
    f.selector == sig:exit(address,address[],uint256[],uint256,bytes).selector ||
    f.selector == sig:swap(uint8,address,address,uint256,SmartVaultHarness.SwapLimit,uint256,bytes).selector);

definition FixedPoint_ONE() returns uint256 = 1000000000000000000;

/**************************************************
 *                GHOSTS AND HOOKS                *
 **************************************************/

ghost mapping(address => mapping(bytes4 => bool)) ghostAuthorized {
    init_state axiom forall address x. forall bytes4 y.
        ghostAuthorized[x][y] == false;
}

hook Sstore authorized[KEY address who][KEY bytes4 what] bool value (bool old_value) STORAGE {
    // bytes4 what_prime = what & 0xffffffff;
    // ghostAuthorized[who][what_prime] = value;
    ghostAuthorized[who][what] = value;
}

hook Sload bool value authorized[KEY address who][KEY bytes4 what] STORAGE {
    // bytes4 what_prime = what & 0xffffffff;
    // require ghostAuthorized[who][what_prime] == value; 
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
    // require forall address user.
    //             forall bytes4 func_sig. (user != who => !ghostAuthorized[user][func_sig & 0xffffffff]);
    // require forall bytes4 func_sig. (!ghostAuthorized[ANY_ADDRESS()][func_sig & 0xffffffff]);
    require forall address user.
                forall bytes4 func_sig. (user != who => !ghostAuthorized[user][func_sig]);
    require forall bytes4 func_sig. (!ghostAuthorized[ANY_ADDRESS()][func_sig]);
}

// Realistic value for the decimals (4<=dec<=27)
function requireValidDecimals(address token) {
    uint256 decimals = oracle.getERC20Decimals(token);
    require decimals >= 4 && decimals <= 27;
}

// Consistency of the decimals between the ERC20 definition for the quote,
// and the decimals from the chainlink oracle feed.
function matchDecimals(address base, address quote) {
    require oracle.getFeedDecimals(getPriceFeed(base, quote)) == 
        oracle.getERC20Decimals(quote);
}

function getFeedPrice(address base, address quote) returns uint256 {
    uint256 price;
    uint256 decimal;
    // price, decimal = oracle._getFeedData(getPriceFeed(base, quote));  // CVL1
    price, decimal = oracle.getFeedData(getPriceFeed(base, quote));  // CVL2
    return price;
}

// Condition to match mutual prices from chainlink price oracle
function matchMutualPrices(address base, address quote) returns bool {
    address feed1 = getPriceFeed(base, quote);
    address feed2 = getPriceFeed(quote, base);
    uint256 price1; uint256 dec1;
    uint256 price2; uint256 dec2;
    // price1, dec1 = oracle._getFeedData(feed1);  // CVL1
    // price2, dec2 = oracle._getFeedData(feed2);  // CVL1
    price1, dec1 = oracle.getFeedData(feed1);  // CVL2
    price2, dec2 = oracle.getFeedData(feed2);  // CVL2
    return (require_uint256(price1 * price2) == oracle.pow10(require_uint256(dec1 + dec2)));
}

// Forces the price feed provider to go through the pivot feed for
// a pair of tokens base, quote
function usePivotForPair(address base, address quote) {
    address pivot = oracle.pivot();
    require pivot != base && pivot != quote &&
    getPriceFeed(base, quote) == 0 && getPriceFeed(quote, base) == 0 &&
    getPriceFeed(base, pivot) != 0 && getPriceFeed(quote, pivot) != 0;
}

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

rule collectTransferIntegrity(address token, address from, uint256 amount) {
    env e;
    bytes data;
    address anyToken;
    address anyUser;
    require anyToken != token;
    require anyUser != currentContract && anyUser != from;

    uint256 fromBalance1 = oracle.balanceOfToken(token, from);
    uint256 vaultBalance1 = oracle.balanceOfToken(token, currentContract);
    uint256 fromBalanceAny1 = oracle.balanceOfToken(anyToken, from);
    uint256 vaultBalanceAny1 = oracle.balanceOfToken(anyToken, currentContract);
    uint256 anyUserBalance1 = oracle.balanceOfToken(token, anyUser);

        collect(e, token, from, amount, data);

    uint256 fromBalance2 = oracle.balanceOfToken(token, from);
    uint256 vaultBalance2 = oracle.balanceOfToken(token, currentContract);
    uint256 fromBalanceAny2 = oracle.balanceOfToken(anyToken, from);
    uint256 vaultBalanceAny2 = oracle.balanceOfToken(anyToken, currentContract);
    uint256 anyUserBalance2 = oracle.balanceOfToken(token, anyUser);

    // One needs to take fees into account
    if(from == currentContract) {
        assert fromBalance1 == fromBalance2;
    }
    else {
        assert to_mathint(fromBalance2) == (fromBalance1 - amount);
        assert to_mathint(vaultBalance2) == (vaultBalance1 + amount);
    }

    assert fromBalanceAny1 == fromBalanceAny2;
    assert vaultBalanceAny1 == vaultBalanceAny2;
    assert anyUserBalance1 == anyUserBalance2;
}

rule withdrawTransferIntegrity(address token, address to, uint256 amount) {
    env e;
    bytes data;
    address anyToken;
    address anyUser;
    require anyToken != token;
    require anyUser != currentContract && anyUser != to;
    require token != 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE; // not a native token
    uint256 withdrawFeePct = getWithdrawFeePct(e);
    require withdrawFeePct == 0;  // simplification - no fees

    uint256 toBalance1 = oracle.balanceOfToken(token, to);
    uint256 vaultBalance1 = oracle.balanceOfToken(token, currentContract);
    uint256 toBalanceAny1 = oracle.balanceOfToken(anyToken, to);
    uint256 vaultBalanceAny1 = oracle.balanceOfToken(anyToken, currentContract);
    uint256 anyUserBalance1 = oracle.balanceOfToken(token, anyUser);

        withdraw(e, token, amount, to, data);

    uint256 toBalance2 = oracle.balanceOfToken(token, to);
    uint256 vaultBalance2 = oracle.balanceOfToken(token, currentContract);
    uint256 toBalanceAny2 = oracle.balanceOfToken(anyToken, to);
    uint256 vaultBalanceAny2 = oracle.balanceOfToken(anyToken, currentContract);
    uint256 anyUserBalance2 = oracle.balanceOfToken(token, anyUser);

    if(to == currentContract) {
        assert toBalance2 == toBalance1;
    }
    else {
        assert to_mathint(toBalance2) == (toBalance1 + amount);
        assert to_mathint(vaultBalance2) == (vaultBalance1 - amount);
    }
    
    assert toBalanceAny1 == toBalanceAny2;
    assert vaultBalanceAny1 == vaultBalanceAny2;
    assert anyUserBalance1 == anyUserBalance2;
}

rule withdrawTransferIntegrityOfNativeToken(address nativeToken, address to, uint256 amount) {
    env e;
    bytes data;
    address anyToken;
    address anyUser;
    require anyToken != nativeToken;
    require anyUser != currentContract && anyUser != to;
    require nativeToken == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE; // explicitly a native token
    uint256 withdrawFeePct = getWithdrawFeePct(e);
    require withdrawFeePct == 0;  // simplification - no fees

    uint256 toBalance1 = getNativeBalanceOf(nativeToken, to);
    uint256 vaultBalance1 = getNativeBalanceOf(nativeToken, currentContract);
    uint256 toBalanceAny1 = oracle.balanceOfToken(anyToken, to);
    uint256 vaultBalanceAny1 = oracle.balanceOfToken(anyToken, currentContract);
    uint256 anyUserBalance1 = getNativeBalanceOf(nativeToken, anyUser);

        withdraw(e, nativeToken, amount, to, data);

    uint256 toBalance2 = getNativeBalanceOf(nativeToken, to);
    uint256 vaultBalance2 = getNativeBalanceOf(nativeToken, currentContract);
    uint256 toBalanceAny2 = oracle.balanceOfToken(anyToken, to);
    uint256 vaultBalanceAny2 = oracle.balanceOfToken(anyToken, currentContract);
    uint256 anyUserBalance2 = getNativeBalanceOf(nativeToken, anyUser);

    if(to == currentContract) {
        assert toBalance2 == toBalance1;
    }
    else {
        assert to_mathint(toBalance2) == (toBalance1 + amount);
        assert to_mathint(vaultBalance2) == (vaultBalance1 - amount);
    }
    
    if(anyToken == WRToken && to == WRToken) {
        assert vaultBalanceAny2 - vaultBalanceAny1 == to_mathint(amount);
    }
    else {
        assert vaultBalanceAny1 == vaultBalanceAny2;
    }

    assert toBalanceAny1 == toBalanceAny2;
    assert anyUserBalance1 == anyUserBalance2;
}


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

rule sanity(method f) {
    env e;
    calldataarg args;
    f(e, args);
    assert false;
}

rule sanityFiltered(method f)
filtered {f -> f.selector == sig:claim(address,bytes).selector || 
              f.selector == sig:bridge(uint8,uint256,address,uint256,SmartVaultHarness.BridgeLimit,uint256,bytes).selector || 
              f.selector == sig:join(address,address[],uint256[],uint256,bytes).selector ||
              f.selector == sig:exit(address,address[],uint256[],uint256,bytes).selector ||
              f.selector == sig:swap(uint8,address,address,uint256,SmartVaultHarness.SwapLimit,uint256,bytes).selector ||
              f.selector == sig:wrap(uint256,bytes).selector}
{
    env e;
    calldataarg args;
    f(e, args);
    assert false;
}

 rule exitSanity() {
    env e;
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;
    require amountsIn[0] > 0;
    require tokensIn.length == 1;
    require amountsIn.length == 1;
    require data.length == 64;
    exit(e, strategy, tokensIn, amountsIn, slippage, data);
    assert false;
}

// Currently there is an inconsistency problem so this rule is violated.
// A well-functioning ghost should yield a correct rule.
rule ghostAuthorizationConsistency() {
    bytes4 what;
    address who;
    bool auth = isAuthorized(who, what);
    assert auth == (ghostAuthorized[who][what] || ghostAuthorized[ANY_ADDRESS()][what]);
}


rule onlyAuthUserCanCallFunctions(method f) 
filtered {f -> !f.isView && !f.isFallback &&
                f.selector != sig:paySwapFee(address,uint256).selector &&
                f.selector != sig:initialize(address).selector &&
                f.selector != sig:setPriceFeeds(address[],address[],address[]).selector} {
    // this rule checks that only authorized user can run all the methods in the contract without reverting
    // all the other users when trying to execute any method should revert
    // therefore the rule should only fail on
    // * paySwapFee(address,uint256) - our own method added to the harness
    // * initialize(address) - this method should be run only once
    // * setPriceFeeds(address[],address[],address[]) - doesn't revert if the loop isn't executed
    // regarding setPriceFeeds() we manually checked that it also requires authorization
    env e1;
    env e2;
    calldataarg args;

    // setup - only e1.msg.sender is authorized to run any function:
    singleAddressGetsTotalControl(e1.msg.sender);
    //singleAddressAuthorization(e1.msg.sender, oracle.uint32ToBytes4(select_setPriceFeeds()));

    // another user (e2.msg.sender) tries to call any function
    require e1.msg.sender != e2.msg.sender;
    f@withrevert(e2,args);
    //setPriceFeeds@withrevert(e2,args);
    bool reverted = lastReverted; // true if f(e2,args) reverted

    assert reverted; // this means that always the call reverted    
}

rule uniqueAddressChangesPriceFeed(method f) {
    env e;
    calldataarg args;
    address priceFeedAuthorized;
    address base;
    address quote;
    address feed0 = getPriceFeed(base, quote);

    // Set a single authorized address to set price feed.
    singleAddressAuthorization(priceFeedAuthorized, oracle.uint32ToBytes4(select_setPriceFeed()));
    require ghostAuthorized[priceFeedAuthorized][oracle.uint32ToBytes4(select_setPriceFeed())];
    require priceFeedAuthorized != e.msg.sender;
    f(e, args);

    address feed1 = getPriceFeed(base, quote);

    assert feed0 == feed1;
}

rule uniquenessOfAuthorization(method f, method g) 
filtered{f -> (!f.isView && f.selector != sig:authorize(address,bytes4).selector)
,g -> !g.isView} {
//filtered{f -> f.selector == sig:setPriceFeed(address, address, address).selector,
//g -> g.selector == sig:setSwapFee(uint256, uint256, address, uint256).selector}{
    env ef;
    env eg;
    calldataarg args_f;
    calldataarg args_g;
    // Unique address authorization for the called methods.
    singleAddressAuthorization(ef.msg.sender, oracle.uint32ToBytes4(f.selector));
    singleAddressAuthorization(eg.msg.sender, oracle.uint32ToBytes4(g.selector));
    bool authorized_G = ghostAuthorized[eg.msg.sender][oracle.uint32ToBytes4(g.selector)];

    // Call f, g
    f(ef, args_f);
    g@withrevert(eg, args_g);

    assert !authorized_G => lastReverted;
}


/**************************************************
 *           Wrapped token METHOD INTEGRITY       *
 **************************************************/

rule wrapUnwrapIntegrity(uint256 amount, address user) {
    env e1;
    env e2;
    bytes data;
    uint256 balance1 = WRToken.balanceOf(user);
        uint256 wrappedAmount = wrap(e1, amount, data);
        uint256 unWrappedAmount = unwrap(e2, wrappedAmount, data);
    uint256 balance2 = WRToken.balanceOf(user);

    assert amount == unWrappedAmount;
    assert balance1 == balance2;
}

rule unwrapWrapIntegrity(uint256 amount, address user) {
    env e1;
    env e2;
    bytes data;
    
    uint256 balance1 = WRToken.balanceOf(user);
        uint256 unWrappedAmount = unwrap(e1, amount, data);
        uint256 wrappedAmount = wrap(e2, unWrappedAmount, data);
    uint256 balance2 = WRToken.balanceOf(user);
    
    assert amount == wrappedAmount;
    assert balance1 == balance2;
}

rule unwrapCannotRevertAfterWrap(uint256 amount) {
    env e;
    bytes data;
    uint256 amountToUnwrap;
    require amountToUnwrap > 0;
    require isAuthorized(e.msg.sender, oracle.uint32ToBytes4(select_unwrap()));
    uint256 wrappedAmount = wrap(e, amount, data);
    unwrap@withrevert(e, amountToUnwrap, data);
    
    assert amountToUnwrap <= wrappedAmount => !lastReverted;
}

rule wrapCannotRevertAfterUnwrap(uint256 amount) {
    env e;
    bytes data;
    uint256 amountToWrap;
    require amountToWrap > 0;
    require isAuthorized(e.msg.sender, oracle.uint32ToBytes4(select_wrap()));
    uint256 unwrappedAmount = unwrap(e, amount, data);
    wrap@withrevert(e, amountToWrap, data);
    
    assert amountToWrap <= unwrappedAmount => !lastReverted;
}


/**************************************************
 *           Price Oracle Integrity     *
 **************************************************/
rule getPriceMutuallyRevert(address base, address quote) {
    
    getPrice@withrevert(base, quote);
    bool revert1 = lastReverted;
    getPrice@withrevert(quote, base);
    bool revert2 = lastReverted;
    
    assert revert1 <=> revert2;
}

// This is not necessarily true!
// There could be a mismatch between the prices of two tokens and the inverse.

// In addition, the invariant is violated for every function which activates a
// delegatecall since it can potentially change the price feeds addresses and
// therefore the oracle prices for any pair.
invariant tokensPriceReciprocity(address base, address quote)
     matchMutualPrices(base, quote);

rule feedDecimalsCannotChange(method f, address feed) 
filtered{f -> !f.isView && f.selector != sig:setPriceFeed(address,address,address).selector} 
{
    env e;
    calldataarg args;
    uint256 decBefore = oracle.getFeedDecimals(feed); 
        f(e, args);
    uint256 decAfter = oracle.getFeedDecimals(feed); 

    assert decBefore == decAfter;
}


rule getPriceReciprocity(address base, address quote) {
    requireInvariant tokensPriceReciprocity(base, quote);
    matchDecimals(base, quote);
    matchDecimals(quote, base);
    // Just making things simpler...
    requireValidDecimals(quote);
    requireValidDecimals(base);
    
    assert oracle.mulDownFP(getPrice(quote, base), getPrice(base, quote)) == FixedPoint_ONE();
}

// The price of two tokens is zero iff the reciprocal price is also zero.
// (More precisely they can't be zero together, unless something is not defined
// in the chain-link oracle)
rule pricesEqualZeroMutually(address base, address quote) {
    requireInvariant tokensPriceReciprocity(base, quote);
    matchDecimals(base, quote);
    matchDecimals(quote, base);

    // Additional assumptions for a more realistic scope
    require getFeedPrice(base, quote) >= 100000;
    require getFeedPrice(quote, base) >= 100000;
    requireValidDecimals(quote);
    requireValidDecimals(base);

    assert getPrice(base, quote) == 0 <=> getPrice(quote, base) == 0;

    // this checks that returned price cannot be zero
    assert getPrice(base, quote) != 0;  
}

// Fails
rule pivotUnitPrice(address base, address quote) {
    usePivotForPair(base, quote);
    address pivot = oracle.pivot();

    // View prices from feed
    uint256 priceBase = getFeedPrice(base, pivot);
    uint256 priceQuote = getFeedPrice(quote, pivot);

    //requireValidDecimals(pivot);
    matchDecimals(base, pivot);
    matchDecimals(quote, pivot);
    
    assert 
    (getPrice(base, pivot) == FixedPoint_ONE() &&
    getPrice(quote, pivot) == FixedPoint_ONE()) =>
    getPrice(base, quote) == FixedPoint_ONE();
}

// Relaxed version (1%) of pivotUnitPrice rule
// Also fails.
rule pivotUnitPriceRelaxed(address base, address quote) {
    usePivotForPair(base, quote);
    address pivot = oracle.pivot();

    // View prices from feed
    uint256 priceBase = getFeedPrice(base, pivot);
    uint256 priceQuote = getFeedPrice(quote, pivot);
    uint256 pairPrice = getPrice(base, quote);

    //requireValidDecimals(pivot);
    matchDecimals(base, pivot);
    matchDecimals(quote, pivot);
    
    assert 
    (getPrice(base, pivot) == FixedPoint_ONE() &&
    getPrice(quote, pivot) == FixedPoint_ONE()) 
    =>
    (to_mathint(pairPrice) >= (FixedPoint_ONE()*99 ) / 100 &&
     to_mathint(pairPrice) <= (FixedPoint_ONE()*101) / 100);
}

// Tests the prover's modeling of pow10(x) = 10**x
rule pow10Integrity(uint256 x, uint256 y) {
    uint256 z = require_uint256(x+y);
    assert to_mathint(oracle.pow10(z)) == oracle.pow10(x)*oracle.pow10(y);
    assert oracle.pow10(1) == 10;
    assert oracle.pow10(2) == 100;
}

// Integrity of exit()
// investedValue[strategy] = 0 <= strategyToken.balanceOf(SmartVault) = 0
// if investedValue[strategy] != 0 => strategy.exit() should not revert
//invariant integrityOfExit() {
//
//}

// rule ifInvestedValueNotZeroCanAlwaysExit
// 1) strategyA.exit(args1) not reverting
// 2) return to initial storage
// 3) swap(tokenA)
// 4) strategyA.exit(args1) should not revert

