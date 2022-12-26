//
//      This auxiliary spec contains various rules that help gain better
//      understanding of the contracts / project / tool behavior
// 


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

//10.   The call() function if authorized can call ***ANY*** contract
//      unlike the strategies / swap connector / oracles whose addresses have to be registered
//      in the registry thus offering some protection, the call() is unlimited
//      and potentially very dangerous
//      Suggestion: to add a check that the called contract is also in the registry


/**************************************************
 *                LINKED CONTRACTS                *
 **************************************************/
// Declaration of contracts used in the spec

// using DummyERC20Impl as dummyERC20Token
// using DummyERC20A as tokenA
// using DummyERC20B as tokenB



/**************************************************
 *              METHODS DECLARATIONS              *
 **************************************************/
methods {

    // Harness method getters:

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

    // Price oracle & helpers
    oracle._getFeedData(address) returns (uint256, uint256) envfree
    oracle.getFeedDecimals(address) returns (uint256) envfree
    oracle.getERC20Decimals(address) returns (uint256) envfree
    oracle.pow10(uint256) returns (uint256) envfree
    oracle.balanceOfToken(address, address) returns(uint256) envfree
    oracle.uint32ToBytes4(uint32) returns (bytes4) envfree
    oracle.uint32Sol(uint256) returns (uint32) envfree
    oracle.getERC20Allowance(address, address, address) returns (uint256) envfree

    // //
    // tokenA.balanceOf(address) envfree
	// tokenB.balanceOf(address) envfree
	// dummyERC20Token.balanceOf(address) envfree
	// //
    // tokenA.totalSupply() envfree
	// tokenB.totalSupply() envfree
	// dummyERC20Token.totalSupply() envfree

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
}


/**************************************************
 *                      MISC                      *
 **************************************************/

 rule exitSanity() {
    env e;
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


rule whoChangedSmartVaultAllowance(method f) {
    address token;
    address owner = currentContract;
    address spender;
    require spender != owner;

    env e;
    calldataarg args;
    uint256 allowanceBefore = oracle.getERC20Allowance(token, owner, spender);
        f(e, args);
    uint256 allowanceAfter = oracle.getERC20Allowance(token, owner, spender);

    assert allowanceBefore == allowanceAfter;
}


rule testGhostAuthorization() {
    env e1; 
    env e2;
    address base;
    address quote;
    address feed;
    singleAddressAuthorization(e1.msg.sender, oracle.uint32ToBytes4(select_setPriceFeed()));
    setPriceFeed(e1, base, quote, feed);
    setPriceFeed(e2, base, quote, feed);
    assert e1.msg.sender == e2.msg.sender;
}
