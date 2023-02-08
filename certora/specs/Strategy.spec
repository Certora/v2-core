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
// using SmartVaultHarnessSwap as SmartVault
using PriceOracleHarness as Oracle
// using DummyERC20FeeCollectorMock as FeeCollector
// using DummyERC20A as ERC20A
using DummyERC20B as ERC20B
// using DexMock as Dex
using AaveV2Token as AToken
using TokenMock as Token
using incentivesController as IncCont
using lendingPool as LendingPool

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
    incentivesController() returns (address) envfree
    feeCollector() returns (address) envfree
    lastValue(address) returns(uint256) envfree

    // Price Oracle & helpers
    Oracle._getFeedData(address) returns (uint256, uint256) envfree
    Oracle.getFeedDecimals(address) returns (uint256) envfree
    Oracle.getERC20Decimals(address) returns (uint256) envfree
    Oracle.pow10(uint256) returns (uint256) envfree
    Oracle.balanceOfToken(address, address) returns(uint256) envfree
    Oracle.uint32ToBytes4(uint32) returns (bytes4) envfree
    Oracle.uint32Sol(uint256) returns (uint32) envfree
    Oracle.getERC20Allowance(address, address, address) returns (uint256) envfree
    Oracle.mulDownFP(uint256, uint256) returns (uint256) envfree
    Oracle.pivot() returns(address) envfree

    IncCont.getUserUnclaimedRewards(address) returns(uint256) envfree

    LendingPool.getReserveDataAToken(address) returns(address) envfree

    deposit() => DISPATCHER(true)
}



// Disclaimer: this verification is done based on AAVE's Strategy implementation with harnesses
// since array as a return value is not supported in CVL




// STATUS - verified (could be an invariant but fails in instate becuase it's not set in constructor)
// lendingPool.reserveData[asset].aTokenAddress matches the aToken address in SmartVault
rule LendPoolAndSmartVaulrMatch(env e, method f) filtered 
{ 
    f -> f.selector != 0xcc58002c    // sighash of call(address,bytes,uint256,bytes)  
    &&  f.selector != bridge(uint8,uint256,address,uint256,uint8,uint256,bytes).selector    // removing bridge() because it fails reachability
} {
    require LendingPool.getReserveDataAToken(Token) == aToken(e);

    calldataarg args;
    f(e, args);

    assert LendingPool.getReserveDataAToken(Token) == aToken(e), "Remember, with great power comes great responsibility.";
}


/**************************************************
 *                  JOIN INTEGRITY                *
 **************************************************/


// STATUS - verified
// InvestedValue of strategy and aToken balance of SmartVault should be changed according to amountOut value.
rule joinIntergrity_investedValueAndATokenBalance(env e) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values
    require amountsIn.length < 10;  // bug workaround
    require tokensIn.length < 10;   // bug workaround

    address tokenOut;
    uint256 amountOut;

    uint256 investedValueBefore = investedValue(strategy);
    uint256 aTokenBalanceBefore = AToken.balanceOf(e, currentContract);

    tokenOut, amountOut = joinHarness(e, strategy, tokensIn, amountsIn, slippage, data);

    uint256 investedValueAfter = investedValue(strategy);
    uint256 aTokenBalanceAfter = AToken.balanceOf(e, currentContract);

    assert investedValueAfter - investedValueBefore == amountOut, "Remember, with great power comes great responsibility.";
    assert aTokenBalanceAfter - aTokenBalanceBefore == amountOut, "Remember, with great power comes great responsibility.";
}


// STATUS - verified
// Token balance of SmartVault and aToken contracts should be changed according to amountOut value.
// amountOut should match amountsIn[0].
rule joinIntergrity_tokenBalance(env e,env e2) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values
    require amountsIn.length < 10;  // bug workaround
    require tokensIn.length < 10;   // bug workaround
    require LendingPool.getReserveDataAToken(Token) == aToken(e);

    address tokenOut;
    uint256 amountOut;

    uint256 tokenBalanceCCBefore = Token.balanceOf(e, currentContract);
    uint256 tokenBalanceATokenBefore = Token.balanceOf(e, aToken(e));

    tokenOut, amountOut = joinHarness(e2, strategy, tokensIn, amountsIn, slippage, data);

    uint256 tokenBalanceCCAfter = Token.balanceOf(e, currentContract);
    uint256 tokenBalanceATokenAfter = Token.balanceOf(e, aToken(e));

    assert tokenBalanceCCBefore - tokenBalanceCCAfter == amountOut, "Remember, with great power comes great responsibility.";
    assert tokenBalanceATokenAfter - tokenBalanceATokenBefore == amountOut, "Remember, with great power comes great responsibility.";
    assert amountsIn[0] == amountOut, "Remember, with great power comes great responsibility.";     // broken becuase of the bug in CVL with arrays
}


// STATUS - verified
// 2 small joins shouldn't bring more profit than one big (useless with ratio 1:1 but might be good for other future strategies)
rule joinIntergrity_bigVsSmalls(env e) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsInBig; uint256[] amountsInSmall1; uint256[] amountsInSmall2;
    uint256 slippage;
    bytes data;

    require amountsInBig[0] == amountsInSmall1[0] + amountsInSmall2[0];  
    require amountsInBig.length < 10;       // bug workaround
    require amountsInSmall1.length < 10;    // bug workaround
    require amountsInSmall2.length < 10;    // bug workaround
    require tokensIn.length < 10;           // bug workaround

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

    address tokenOut;
    uint256 amountOutBig; uint256 amountOutSmall1; uint256 amountOutSmall2;

    uint256 investedValueBefore = investedValue(strategy);
    uint256 aTokenBalanceBefore = AToken.balanceOf(e, currentContract);

    storage initialStorage = lastStorage;

    tokenOut, amountOutBig = joinHarness(e, strategy, tokensIn, amountsInBig, slippage, data);

    uint256 investedValueAfterBig = investedValue(strategy);
    uint256 aTokenBalanceAfterBig = AToken.balanceOf(e, currentContract);

    tokenOut, amountOutSmall1 = joinHarness(e, strategy, tokensIn, amountsInSmall1, slippage, data) at initialStorage;
    tokenOut, amountOutSmall2 = joinHarness(e, strategy, tokensIn, amountsInSmall2, slippage, data);

    uint256 investedValueAfterSmall = investedValue(strategy);
    uint256 aTokenBalanceAfterSmall = AToken.balanceOf(e, currentContract);

    assert investedValueAfterBig >= investedValueAfterSmall, "Remember, with great power comes great responsibility.";
    assert aTokenBalanceAfterBig >= aTokenBalanceAfterSmall, "Remember, with great power comes great responsibility.";
}


// STATUS - verified
// No other balance, except involved in join(), of Token, AToken and investedValue was toched
rule joinIntergrity_untouchableBalance(env e) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values
    require amountsIn.length < 10;  // bug workaround
    require tokensIn.length < 10;   // bug workaround

    address tokenOut;
    uint256 amountOut;

    address anotherAddress;
    require anotherAddress != currentContract
            && anotherAddress != Token
            && anotherAddress != AToken
            && anotherAddress != strategy;

    uint256 investedValueBefore = investedValue(anotherAddress);
    uint256 aTokenBalanceBefore = AToken.balanceOf(e, anotherAddress);
    uint256 tokenBalanceCCBefore = Token.balanceOf(e, anotherAddress);

    tokenOut, amountOut = joinHarness(e, strategy, tokensIn, amountsIn, slippage, data);

    uint256 investedValueAfter = investedValue(anotherAddress);
    uint256 aTokenBalanceAfter = AToken.balanceOf(e, anotherAddress);
    uint256 tokenBalanceCCAfter = Token.balanceOf(e, anotherAddress);
    
    assert investedValueBefore == investedValueAfter, "Remember, with great power comes great responsibility.";
    assert aTokenBalanceBefore == aTokenBalanceAfter, "Remember, with great power comes great responsibility.";
    assert tokenBalanceCCBefore == tokenBalanceCCAfter, "Remember, with great power comes great responsibility.";     // broken becuase of the bug in CVL with arrays
}

/**************************************************
 *                 CLAIM INTEGRITY                *
 **************************************************/


// STATUS - verified
// investedValue should be the same after claim
rule claimIntergrity_investedValue(env e) {
    address strategy;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

    address tokenOut;
    uint256 amountOut;

    uint256 investedValueBefore = investedValue(strategy); 

    tokenOut, amountOut = claimHarness(e, strategy, data);

    uint256 investedValueAfter = investedValue(strategy);

    assert investedValueAfter == investedValueBefore, "Remember, with great power comes great responsibility.";
}


// STATUS - verified
// unclaimedRewards of SmartVault before should be greater or equal to unclaimedRewards of SmartVault after.
// Claims everything.
rule claimIntergrity_unclaimedRewards(env e) {
    address strategy;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

    address tokenOut;
    uint256 amountOut;

    uint256 unclaimedRewardsBefore = IncCont.getUserUnclaimedRewards(currentContract); 

    tokenOut, amountOut = claimHarness(e, strategy, data);

    uint256 unclaimedRewardsAfter = IncCont.getUserUnclaimedRewards(currentContract);

    assert unclaimedRewardsBefore >= unclaimedRewardsAfter, "Remember, with great power comes great responsibility.";
    assert unclaimedRewardsAfter == 0, "Remember, with great power comes great responsibility.";
}


// STATUS - verified
// cannot claim more than unclaimedRewards 
// (might be useful for other strategies if they have more complicated rewards logic.)
// A rule below is enough for the AAVE strategy
rule claimIntergrity_noMoreThanUnclaimedRewards(env e) {
    address strategy;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

    address tokenOut;
    uint256 amountOut;

    uint256 unclaimedRewards = IncCont.getUserUnclaimedRewards(currentContract); 
    uint256 rewardBalanceBefore = ERC20B.balanceOf(e, currentContract);

    tokenOut, amountOut = claimHarness(e, strategy, data);

    uint256 rewardBalanceAfter = ERC20B.balanceOf(e, currentContract);

    assert rewardBalanceAfter - rewardBalanceBefore <= unclaimedRewards, "Remember, with great power comes great responsibility.";
}


// STATUS - verified
// Balance of incentivesController and SmartVault in rewardToken should be updated correctly
rule claimIntergrity_balancesUpdate(env e) {
    address strategy;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

    address tokenOut;
    uint256 amountOut;

    uint256 unclaimedRewards = IncCont.getUserUnclaimedRewards(currentContract); 
    uint256 rewardBalanceSmartVaultBefore = ERC20B.balanceOf(e, currentContract);
    uint256 rewardBalanceIncContBefore = ERC20B.balanceOf(e, incentivesController());

    tokenOut, amountOut = claimHarness(e, strategy, data);

    uint256 rewardBalanceSmartVaultAfter = ERC20B.balanceOf(e, currentContract);
    uint256 rewardBalanceIncContAfter = ERC20B.balanceOf(e, incentivesController());

    assert rewardBalanceIncContBefore - rewardBalanceIncContAfter == unclaimedRewards, "Remember, with great power comes great responsibility.";
    assert rewardBalanceSmartVaultAfter - rewardBalanceSmartVaultBefore == unclaimedRewards, "Remember, with great power comes great responsibility.";
}


// STATUS - verified
// No other balance of rewardToken was toched by claim
rule claimIntergrity_untouchableBalance(env e) {
    address strategy;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

    address tokenOut;
    uint256 amountOut;

    address anotherAddress;
    require anotherAddress != currentContract
            && anotherAddress != incentivesController();

    uint256 balanceBefore = ERC20B.balanceOf(e, anotherAddress);

    tokenOut, amountOut = claimHarness(e, strategy, data);

    uint256 balanceAfter = ERC20B.balanceOf(e, anotherAddress);
    
    assert balanceBefore == balanceAfter, "Remember, with great power comes great responsibility.";     // broken becuase of the bug in CVL with arrays
}


// STATUS - verified
// Cannot claim if strategy wasn't allowed.
rule claimIntergrity_allowanceToClaim(env e) {
    address strategy;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

    claimHarness@withrevert(e, strategy, data);
    bool isReverted = lastReverted;
    
    assert !isStrategyAllowed(strategy) => isReverted, "Remember, with great power comes great responsibility.";     // broken becuase of the bug in CVL with arrays
}


// STATUS - verified
// The second claim in two consecutive claims should bring 0 rewards 
rule claimIntergrity_uselessTheSecondClaim(env e) {
    address strategy;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values

    address tokenOut1; address tokenOut2;
    uint256 amountOut1; uint256 amountOut2;

    tokenOut1, amountOut1 = claimHarness(e, strategy, data);
    tokenOut2, amountOut2 = claimHarness(e, strategy, data);
    
    assert amountOut2 == 0, "Remember, with great power comes great responsibility.";     // broken becuase of the bug in CVL with arrays
}


/**************************************************
 *                  EXIT INTEGRITY                *
 **************************************************/


// STATUS - in progress
// Token balance of SmartVault and aToken contracts should be changed according to amountOut value.
// amountsIn[0] should be equal to the sum amountOut and paidFees
// cannot understand counter example, where tokens went? https://vaas-stg.certora.com/output/3106/b67fe9ca7dd944a0b5f1c401f17108be/?anonymousKey=fdaa99605ec65ca17347aecac4d49a51a71750f4
rule exitIntergrity_tokenBalance(env e, env e2) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;

    require LendingPool.getReserveDataAToken(Token) == aToken(e);   // setup for exit() because reserveData mapping in LendingPool isn't sychronized with the real aToken address

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values
    require amountsIn.length < 10;  // bug workaround
    require tokensIn.length < 10;   // bug workaround

    require currentContract != feeCollector()
            && feeCollector() != AToken
            && feeCollector() != Token
            && e2.msg.sender != feeCollector();     // avoid getting fees to a wrong adrress

    address tokenOut;
    uint256 amountOut;

    uint256 tokenBalanceCCBefore = Token.balanceOf(e, currentContract);
    uint256 tokenBalanceATokenBefore = Token.balanceOf(e, aToken(e));
    uint256 tokenBalanceFeeBefore = Token.balanceOf(e, feeCollector());

    tokenOut, amountOut = exitHarness(e2, strategy, tokensIn, amountsIn, slippage, data);

    uint256 tokenBalanceCCAfter = Token.balanceOf(e, currentContract);
    uint256 tokenBalanceATokenAfter = Token.balanceOf(e, aToken(e));
    uint256 tokenBalanceFeeAfter = Token.balanceOf(e, feeCollector());

    uint256 paidFees = to_uint256(tokenBalanceFeeAfter - tokenBalanceFeeBefore);
    uint256 exitTogether = to_uint256(amountOut + paidFees);

    assert tokenBalanceCCAfter - tokenBalanceCCBefore == amountOut, "Remember, with great power comes great responsibility.";
    assert tokenBalanceATokenBefore - tokenBalanceATokenAfter == exitTogether, "Remember, with great power comes great responsibility.";
    assert amountsIn[0] == exitTogether, "Remember, with great power comes great responsibility.";
}


// STATUS - verified
// aToken balance of SmartVault should be changed according to amountOut value. InvestedValue of strategy shouldn't increase.
rule exitIntergrity_investedValueAndATokenBalance(env e) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;

    require LendingPool.getReserveDataAToken(Token) == aToken(e);   // setup for exit() because reserveData mapping in LendingPool isn't sychronized with the real aToken address

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values
    require amountsIn.length < 10;
    require tokensIn.length < 10;

    address tokenOut;
    uint256 amountOut;

    uint256 investedValueBefore = investedValue(strategy);
    uint256 aTokenBalanceBefore = AToken.balanceOf(e, currentContract);

    tokenOut, amountOut = exitHarness(e, strategy, tokensIn, amountsIn, slippage, data);

    uint256 investedValueAfter = investedValue(strategy);
    uint256 aTokenBalanceAfter = AToken.balanceOf(e, currentContract);

    assert investedValueAfter <= investedValueBefore, "Remember, with great power comes great responsibility.";
    assert aTokenBalanceBefore - aTokenBalanceAfter == amountsIn[0], "Remember, with great power comes great responsibility.";
}


// STATUS - verified
rule exitIntergrity_untouchableBalance(env e) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values
    require amountsIn.length < 10;
    require tokensIn.length < 10;

    address tokenOut;
    uint256 amountOut;

    address anotherAddress;
    require anotherAddress != currentContract
            && anotherAddress != Token
            && anotherAddress != AToken
            && anotherAddress != strategy
            && anotherAddress != feeCollector();

    uint256 investedValueBefore = investedValue(anotherAddress);
    uint256 aTokenBalanceBefore = AToken.balanceOf(e, anotherAddress);
    uint256 tokenBalanceCCBefore = Token.balanceOf(e, anotherAddress);

    tokenOut, amountOut = exitHarness(e, strategy, tokensIn, amountsIn, slippage, data);

    uint256 investedValueAfter = investedValue(anotherAddress);
    uint256 aTokenBalanceAfter = AToken.balanceOf(e, anotherAddress);
    uint256 tokenBalanceCCAfter = Token.balanceOf(e, anotherAddress);
    
    assert investedValueBefore == investedValueAfter, "Remember, with great power comes great responsibility.";
    assert aTokenBalanceBefore == aTokenBalanceAfter, "Remember, with great power comes great responsibility.";
    assert tokenBalanceCCBefore == tokenBalanceCCAfter, "Remember, with great power comes great responsibility.";     // broken becuase of the bug in CVL with arrays
}


// STATUS - vefified (partically because of there are too many varaibles in the case of successful strategy 
// that the tool can easily create infeasable scenarious with fees and investedValue calculations)
// Checking if conditions for successful and unsuccessful strategy are correct:
// 1. if there were losses, then no fees are charged
// 2. if there were profits and withdraw more than gains, investValue is decreased
rule exitIntergrity_checkingConditions(env e,env e2) {
    address strategy;
    address[] tokensIn;
    uint256[] amountsIn;
    uint256 slippage;
    bytes data;

    require LendingPool.getReserveDataAToken(Token) == aToken(e);   // setup for exit() because reserveData mapping in LendingPool isn't sychronized with the real aToken address

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values
    require amountsIn.length < 10;  // bug workaround
    require tokensIn.length < 10;   // bug workaround

    require amountsIn[0] > 0;

    require currentContract != feeCollector()
            && feeCollector() != AToken
            && feeCollector() != Token;

    address tokenOut;
    uint256 amountOut;

    uint256 investedValueBefore = investedValue(strategy);
    uint256 tokenBalanceATokenBefore = AToken.balanceOf(e, currentContract);
    uint256 lastValueBefore = lastValue(strategy);
    uint256 tokenBalanceFeeBefore = Token.balanceOf(e, feeCollector());

    tokenOut, amountOut = exitHarness(e2, strategy, tokensIn, amountsIn, slippage, data);

    uint256 tokenBalanceATokenAfter = AToken.balanceOf(e, currentContract);
    uint256 tokenBalanceFeeAfter = Token.balanceOf(e, feeCollector());
    uint256 lastValueAfter = lastValue(strategy);
    uint256 investedValueAfter = investedValue(strategy);

    uint256 paidFees = to_uint256(tokenBalanceFeeAfter - tokenBalanceFeeBefore);
    uint256 calculatedValue = to_uint256(tokenBalanceATokenBefore - tokenBalanceATokenAfter);
    uint256 valueGains = to_uint256(lastValueBefore - investedValueBefore);

    assert tokenBalanceATokenBefore <= investedValueBefore => tokenBalanceFeeBefore == tokenBalanceFeeAfter, "Remember, with great power comes great responsibility.";
    assert lastValueBefore > investedValueBefore && valueGains < calculatedValue => investedValueBefore > investedValueAfter;  // checking fees is more complicated becuse there are more variables involved in caclculations
}



/**************************************************
 *                    SCENARIOS                   *
 **************************************************/


// STATUS - verified
// join/claim/exit on one strategy, shouldn't affect join on another strategy
rule frontrunJoinCheck(env e, method f) {
    address mainStrategy; address frontStrategy;
    address[] tokensInMain; address[] tokensInFront;
    uint256[] amountsInMain; uint256[] amountsInFront;
    uint256 slippage;
    bytes data;

    require data.length <= 64;  // need this to avoid the issue when bytes type affects other variables values
    require amountsInMain.length < 10;       // bug workaround
    require amountsInFront.length < 10;    // bug workaround
    require tokensInMain.length < 10;           // bug workaround
    require amountsInFront.length < 10;           // bug workaround

    require mainStrategy != frontStrategy;

    address tokenOut;
    uint256 amountOutMain; uint256 amountOutFront;

    storage initialStorage = lastStorage;

    tokenOut, amountOutMain = joinHarness(e, mainStrategy, tokensInMain, amountsInMain, slippage, data);

    require f.selector == join(address, address[], uint256[], uint256, bytes).selector 
            || f.selector == claim(address, bytes).selector 
            || f.selector == exit(address, address[], uint256[], uint256, bytes).selector;
    
    if (f.selector == join(address, address[], uint256[], uint256, bytes).selector) {
        joinHarness(e, frontStrategy, tokensInFront, amountsInFront, slippage, data) at initialStorage;
    } else if (f.selector == claim(address, bytes).selector) {
        claimHarness(e, frontStrategy, data) at initialStorage;
    } else {
        exitHarness(e, frontStrategy, tokensInFront, amountsInFront, slippage, data) at initialStorage;
    }

    tokenOut, amountOutFront = joinHarness(e, mainStrategy, tokensInMain, amountsInMain, slippage, data);

    assert amountOutMain == amountOutFront, "Remember, with great power comes great responsibility.";
}


// STATUS - verified
// Other functions cannot frontrun claim
rule noClaimFrontrun(env e, method f)
    filtered { f -> f.selector != claim(address, bytes).selector            // 2 claims can affect each other if 2 different strategies managed by the same vault. So we don't check it
                    && f.selector != claimHarness(address,bytes).selector   // 2 claims can affect each other if 2 different strategies managed by the same vault. So we don't check it
                    && f.selector != 0xcc58002c    // sighash of call(address,bytes,uint256,bytes)   // low-level call need to ask team what to do with it
                    && f.selector != bridge(uint8,uint256,address,uint256,uint8,uint256,bytes).selector  // do we have a solution for it?
} {
    address mainStrategy; address frontStrategy;
    address[] tokensInFront;
    uint256[] amountsInMain; uint256[] amountsInFront;
    uint256 slippage;
    bytes data;

    require data.length <= 64;                      // need this to avoid the issue when bytes type affects other variables values
    require amountsInMain.length < 10;              // bug workaround
    require amountsInFront.length < 10;             // bug workaround
    require amountsInFront.length < 10;             // bug workaround

    address tokenOut;
    uint256 amountOutMain; uint256 amountOutFront;

    storage initialStorage = lastStorage;

    tokenOut, amountOutMain = claimHarness(e, mainStrategy, data);

    if (f.selector == join(address, address[], uint256[], uint256, bytes).selector) {
        joinHarness(e, frontStrategy, tokensInFront, amountsInFront, slippage, data) at initialStorage;
    } else if (f.selector == exit(address, address[], uint256[], uint256, bytes).selector) {
        exitHarness(e, frontStrategy, tokensInFront, amountsInFront, slippage, data) at initialStorage;
    } else {
        calldataarg args; 
        f(e, args) at initialStorage;
    }

    tokenOut, amountOutFront = claimHarness(e, mainStrategy, data);

    assert amountOutMain == amountOutFront, "Remember, with great power comes great responsibility.";
}
