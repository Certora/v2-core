/*
    This is a specification file for smart contract
    verification with the Certora prover.

    For more information,
    visit: https://www.certora.com/

    This file is run with scripts/...
*/

/**************************************************
 *      Top Level Properties / Rule Ideas         *
 **************************************************/

// 1.   Only specific allowed users can execute specific methods in the contract

// 2.   Users allowed to execute only method A,
//      should not be able to execute method that is not A

// 3.   Owner of the SmartVault, should not lose access to it (no one can block the owner)

// 4.   Only contracts set in the Registry should be accessible by the SmartVault

// 5.   If a contract is available in the Registry,
//      the owner of SmartVault should be able to use it (same as 4)

// 6.   User that is not authorized to change the Registry should not be able to do so

// 7.   If any of the linked contracts (PriceOracle, Registry, SwapConnector, Strategy...)
//      is not available, this should not block SmartVault from executing methods that
//      don't use the contracts.
//      For example: If SwapConnector is not available, this can (and probably will)
//                   prevent using swap(), but it should not prevent calling withdraw()

// 8.   PriceOracle should not return a price of 0

// 9.   Swap connector should decrease the balanceOf(TokenOut)
//      and increase the balanceOf(TokenIn)



/**************************************************
 *                LINKED CONTRACTS                *
 **************************************************/
// Declaration of contracts used in the spec

// using DummyERC20Impl as dummyERC20Token
// using DummyERC20A as tokenA
// using DummyERC20B as tokenB
 using WrappedNativeTokenMock as WRToken
 using PriceOracleHarness as oracle
// using StrategyMock as strategyMock

/**************************************************
 *              METHODS DECLARATIONS              *
 **************************************************/
methods {
    // Harness method getters:

    ////////////////////////////////////////
	// ERC20 methods
	transferFrom(address, address, uint256) => DISPATCHER(true)
	transfer(address, uint256) => DISPATCHER(true)
    balanceOf(address) => DISPATCHER(true)
    approve(address, uint256) => DISPATCHER(true)
    decimals() => DISPATCHER(true)
    WRToken.balanceOf(address) returns(uint256) envfree
    //mint(uint256, address) => DISPATCHER(true)
    //burn(uint256, address) => DISPATCHER(true)

	// //
    // tokenA.balanceOf(address) envfree
	// tokenB.balanceOf(address) envfree
	// dummyERC20Token.balanceOf(address) envfree
	// //
    // tokenA.totalSupply() envfree
	// tokenB.totalSupply() envfree
	// dummyERC20Token.totalSupply() envfree

    ////////////////////////////////////////
    // SwapConnectorMock methods
    // packages/smart-vault/contracts/test/core/SwapConnectorMock.sol
    swap(uint8, address, address, uint256, uint256, bytes) returns (uint256) => DISPATCHER(true)
    // swap(
    //     ISwapConnector.Source, /* source */ //enum --> uint8
    //     address tokenIn,
    //     address tokenOut,
    //     uint256 amountIn,
    //     uint256 minAmountOut,
    //     bytes memory data
    // ) external override returns (uint256 amountOut) => DISPATCHER(true)

    ////////////////////////////////////////
    // DexMock methods (called by SwapConnectorMock)
    // packages/smart-vault/contracts/test/samples/DexMock.sol
    swap(address, address, uint256, uint256, bytes) returns (uint256) => DISPATCHER(true)
    // swap(address tokenIn, address tokenOut, uint256 amountIn, uint256, bytes memory)
    //     returns (uint256 amountOut)

    ////////////////////////////////////////
    // node_modules/@openzeppelin/contracts/utils/Address.sol
    // sendValue(address, uint256) => DISPATCHER(true) // not working well, probably because is internal!
    // getting call resolutions for swap(), exit(), withdraw()
    // sendValue(address, uint256) => HAVOC_ECF
    // RESOLVED using --settings -optimisticFallback=true \
    
    ////////////////////////////////////////
    // SmartVault.sol = the main contract
    // call(address, bytes, uint256, bytes) returns (bytes) => HAVOC_ECF
    // ------------- WARNING! -------------
    // call is considered a reserved keyword in CVL, meanwhile HOTFIX by Alex works partially:
    // --staging alex/remove-call-cvl-keyword \
    // --disableLocalTypeChecking
    // we are getting the default: havoc all contracts except SmartVaultHarness


    ////////////////////////////////////////
    // node_modules/@mimic-fi/v2-strategies/contracts/IStrategy.sol
    // packages/strategies/contracts/IStrategy.sol
    // both files above were identical
    // the interface is implemented by mock at:
    // packages/smart-vault/contracts/test/core/StrategyMock.sol
    // token() => DISPATCHER(true)
    // valueRate() returns (uint256) => DISPATCHER(true)
    lastValue(address) returns (uint256) 
    // lastValue(address) returns (uint256) => DISPATCHER(true) // causes error in rule sanity -> exit()
    // claim(bytes) returns (address[], uint256[]) => DISPATCHER(true) // works, but too slow
    //claim(bytes) returns (address[], uint256[]) 
    // join(uint256, uint256, bytes) returns (uint256) => DISPATCHER(true) // old version
    //join(address[],uint256[],uint256,bytes) returns (address[], uint256[], uint256) // causes error in rule sanity -> exit()
    // exit(uint256, uint256, bytes) returns (uint256, uint256) => DISPATCHER(true) // old version
    //exit(address[],uint256[],uint256,bytes) returns (address[], uint256[], uint256) 

    // the StrategyMock dispatchers caused the tool to TIMEOUT because of
    // incorrect calling in the SmartVault.sol
    // fixed the original code by changing "strategy." to "IStrategy(strategy)."

    implementationOf(address) returns (address) => DISPATCHER(true)
    implementationData(address) returns (bool, bool, bytes32) => DISPATCHER(true)
    ANY_ADDRESS() returns (address) envfree
    isStrategyAllowed(address) returns (bool) envfree
    investedValue(address) returns (uint256) envfree
    isAuthorized(address, bytes4) returns (bool) envfree
    getPriceFeed(address, address) returns (address) envfree
    getPrice(address, address) returns (uint256) envfree
    uint32ToBytes4(uint32) returns (bytes4) envfree
    uint32Sol(uint256) returns (uint32) envfree
    setSwapFee(uint256, uint256, address, uint256)

    // Price oracle
    oracle._getFeedData(address) returns (uint256, uint256) envfree
    oracle.getFeedDecimals(address) returns (uint256) envfree
    oracle.getERC20Decimals(address) returns (uint256) envfree
    oracle.pow10(uint256) returns (uint256) envfree
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
function requireValidDecimals(uint256 decimals) {
    require decimals >=4 && decimals <= 27;
}

// Consistency of the decimals between the ERC20 definition for the quote,
// and the decimals from the chainlink oracle feed.
function matchDecimals(address base, address quote) {
    require oracle.getFeedDecimals(getPriceFeed(base, quote)) == 
        oracle.getERC20Decimals(quote);
}

// Condition to match mutual prices from chainlink price oracle
function matchMutualPrices(address base, address quote) returns bool {
    address feed1 = getPriceFeed(base, quote);
    address feed2 = getPriceFeed(quote, base);
    uint256 price1; uint256 dec1;
    uint256 price2; uint256 dec2;
    price1, dec1 = oracle._getFeedData(feed1);
    price2, dec2 = oracle._getFeedData(feed2);
    return (price1 * price2 == oracle.pow10(dec1 + dec2));
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

rule sanity(method f) {
    env e;
    calldataarg args;
    f(e, args);
    assert false;
}

rule exitSanity() {
    env e;
    calldataarg args;
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;
    require amountsIn[0] > 0;
    exit(e, strategy, tokensIn, amountsIn, slippage, data);
    assert false;
}


rule whoChangedWithdrawFeeSettings(method f)
{
    env e;
    calldataarg args;

    // withdrawFee parameters before
    uint256 pct0; uint256 cap0; address token0; uint256 period0; uint256 totalCharged0; uint256 nextResetTime0;
    require (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == withdrawFee(e);
    
    // call any function to try and modify withdrawFee
    f(e,args);

    // withdrawFee parameters after
    uint256 pct1; uint256 cap1; address token1; uint256 period1; uint256 totalCharged1; uint256 nextResetTime1;
    require (pct1, cap1, token1, period1, totalCharged1, nextResetTime1) == withdrawFee(e);

    assert (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == (pct1, cap1, token1, period1, totalCharged1, nextResetTime1);
}


rule whoChangedPerformanceFeeSettings(method f)
{
    env e;
    calldataarg args;

    // performanceFee parameters before
    uint256 pct0; uint256 cap0; address token0; uint256 period0; uint256 totalCharged0; uint256 nextResetTime0;
    require (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == performanceFee(e);
    
    // call any function to try and modify performanceFee
    f(e,args);

    // performanceFee parameters after
    uint256 pct1; uint256 cap1; address token1; uint256 period1; uint256 totalCharged1; uint256 nextResetTime1;
    require (pct1, cap1, token1, period1, totalCharged1, nextResetTime1) == performanceFee(e);

    assert (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == (pct1, cap1, token1, period1, totalCharged1, nextResetTime1);
}


rule whoChangedSwapFeeSettings(method f)
{
    env e;
    calldataarg args;

    // swapFee parameters before
    uint256 pct0; uint256 cap0; address token0; uint256 period0; uint256 totalCharged0; uint256 nextResetTime0;
    require (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == swapFee(e);
    
    // call any function to try and modify swapFee
    f(e,args);

    // swapFee parameters after
    uint256 pct1; uint256 cap1; address token1; uint256 period1; uint256 totalCharged1; uint256 nextResetTime1;
    require (pct1, cap1, token1, period1, totalCharged1, nextResetTime1) == swapFee(e);

    assert (pct0, cap0, token0, period0, totalCharged0, nextResetTime0) == (pct1, cap1, token1, period1, totalCharged1, nextResetTime1);
}


rule whoChangedThePriceOracle(method f)
{
    env e;
    calldataarg args;

    // priceOracle address before
    address priceOracle0;
    require priceOracle0 == priceOracle(e);
    
    // call any function to try and modify priceOracle
    f(e,args);

    // priceOracle address after
    address priceOracle1;
    require priceOracle1 == priceOracle(e);

    assert priceOracle0 == priceOracle1;
}


rule whoChangedTheSwapConnector(method f)
{
    env e;
    calldataarg args;

    // swapConnector address before
    address swapConnector0;
    require swapConnector0 == swapConnector(e);
    
    // call any function to try and modify swapConnector
    f(e,args);

    // swapConnector address after
    address swapConnector1;
    require swapConnector1 == swapConnector(e);

    assert swapConnector0 == swapConnector1;
}


rule whoChangedTheFeeCollector(method f)
{
    env e;
    calldataarg args;

    // feeCollector address before
    address feeCollector0;
    require feeCollector0 == feeCollector(e);
    
    // call any function to try and modify feeCollector
    f(e,args);

    // feeCollector address after
    address feeCollector1;
    require feeCollector1 == feeCollector(e);

    assert feeCollector0 == feeCollector1;
}


rule whoChangedStrategyPermissions(method f)
{
    env e;
    calldataarg args;

    // isStrategyAllowed[address strategy0] should not change
    address strategy0;
    bool strategy0bool;
    require strategy0bool == isStrategyAllowed(strategy0);
    
    // call any function to try and modify isStrategyAllowed[strategy]
    f(e,args);

    address strategy1;
    bool strategy1bool;
    require strategy1bool == isStrategyAllowed(strategy1);

    assert (strategy0 == strategy1) => (strategy0bool == strategy1bool);
}


rule whoChangedInvestedValue(method f)
{
    env e;
    calldataarg args;

    // investedValue[address strategy0] should not change
    address strategy0;
    uint256 strategy0investedValue;
    require strategy0investedValue == investedValue(strategy0);
    
    // call any function to try and modify investedValue[strategy]
    f(e,args);

    address strategy1;
    uint256 strategy1investedValue;
    require strategy1investedValue == investedValue(strategy1);

    assert (strategy0 == strategy1) => (strategy0investedValue == strategy1investedValue);
}


rule testGhostAuthorization() {
    env e1; 
    env e2;
    address base;
    address quote;
    address feed;
    singleAddressAuthorization(e1.msg.sender, uint32ToBytes4(select_setPriceFeed()));
    setPriceFeed(e1, base, quote, feed);
    setPriceFeed(e2, base, quote, feed);
    assert e1.msg.sender == e2.msg.sender;
}

rule onlyAuthUserCanCallFunctions(method f) 
filtered {f -> !f.isView && !f.isFallback} {
    // this rule checks that only authorized user can run all the methods in the contract without reverting
    // all the other users when trying to execute any method should revert
    // therefore the rule should only fail on
    // * initialize(address) - this method should be run only once
    // * setPriceFeeds(address[],address[],address[]) - doesn't revert if the loop isn't executed
    // regarding setPriceFeeds() we manually checked that it also requires authorization
    env e1;
    env e2;
    calldataarg args;

    // setup - only e1.msg.sender is authorized to run any function:
    singleAddressGetsTotalControl(e1.msg.sender);
    //singleAddressAuthorization(e1.msg.sender, uint32ToBytes4(select_setPriceFeeds()));

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
    singleAddressAuthorization(priceFeedAuthorized, uint32ToBytes4(select_setPriceFeed()));
    require ghostAuthorized[priceFeedAuthorized][uint32ToBytes4(select_setPriceFeed())];
    require priceFeedAuthorized != e.msg.sender;
    f(e, args);

    address feed1 = getPriceFeed(base, quote);

    assert feed0 == feed1;
}

rule uniquenessOfAuthorization(method f, method g) 
filtered{f -> !f.isView, g -> !g.isView} {
//filtered{f -> f.selector == setPriceFeed(address, address, address).selector,
//g -> g.selector == setSwapFee(uint256, uint256, address, uint256).selector}{
    env ef;
    env eg;
    calldataarg args_f;
    calldataarg args_g;
    // Unique address authorization for the called methods.
    singleAddressAuthorization(ef.msg.sender, uint32ToBytes4(f.selector));
    singleAddressAuthorization(eg.msg.sender, uint32ToBytes4(g.selector));
    bool authorized_G = ghostAuthorized[eg.msg.sender][g.selector];

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
    require isAuthorized(e.msg.sender, uint32ToBytes4(select_unwrap()));
    uint256 wrappedAmount = wrap(e, amount, data);
    unwrap@withrevert(e, amountToUnwrap, data);
    
    assert amountToUnwrap <= wrappedAmount => !lastReverted;
}

rule wrapCannotRevertAfterUnwrap(uint256 amount) {
    env e;
    bytes data;
    uint256 amountToWrap;
    require amountToWrap > 0;
    require isAuthorized(e.msg.sender, uint32ToBytes4(select_wrap()));
    uint256 unwrappedAmount = unwrap(e, amount, data);
    wrap@withrevert(e, amountToWrap, data);
    
    assert amountToWrap <= unwrappedAmount => !lastReverted;
}

// Currently there is an inconsistency problem so this rule is violated.
// A well-functioning ghost should yield a correct rule.
rule ghostAuthorizationConsistency() {
    bytes4 what;
    address who;
    bool auth = isAuthorized(who, what);
    assert auth == (ghostAuthorized[who][what] || ghostAuthorized[ANY_ADDRESS()][what]);
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
// delegatecall since it can potentially change the price feeds addresses and therefore
// the oracle prices for any pair.
invariant tokensPriceReciprocity(address base, address quote)
     matchMutualPrices(base, quote)

rule getPriceReciprocity(address base, address quote) {
    requireInvariant tokensPriceReciprocity(base, quote);
    matchDecimals(base, quote);
    matchDecimals(quote, base);
    // Just making things simpler...
    // require oracle.getERC20Decimals(base) == 18;
    // require oracle.getERC20Decimals(quote) == 12;

    assert getPrice(base, quote)*getPrice(quote, base) ==
       FixedPoint_ONE()*FixedPoint_ONE();
}

// Tests the prover's modeling of pow10(x) = 10**x
rule pow10Integrity(uint256 x, uint256 y) {
    uint256 z = x+y;
    assert oracle.pow10(z) == oracle.pow10(x)*oracle.pow10(y);
    assert oracle.pow10(1) == 10;
    assert oracle.pow10(2) == 100;
}