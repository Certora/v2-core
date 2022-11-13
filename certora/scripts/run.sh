if [[ "$1" ]]
then
    RULE="--rule $1"
fi

if [[ "$2" ]]
then
    MSG=": $2"
fi

certoraRun  certora/harness/SmartVaultHarness.sol \
            certora/harness/DummyERC20Impl.sol \
            certora/harness/DummyERC20A.sol \
            certora/harness/DummyERC20B.sol \
            certora/harness/DummyERC20FeeCollectorMock.sol \
            packages/smart-vault/contracts/test/samples/TokenMock.sol \
            packages/smart-vault/contracts/test/samples/WrappedNativeTokenMock.sol \
            packages/smart-vault/contracts/test/core/PriceOracleMock.sol \
            packages/smart-vault/contracts/test/core/SwapConnectorMock.sol \
            packages/smart-vault/contracts/test/samples/DexMock.sol \
            packages/smart-vault/contracts/test/core/StrategyMock.sol \
            packages/registry/contracts/registry/Registry.sol \
--verify SmartVaultHarness:certora/specs/SmartVault.spec \
--link  SmartVaultHarness:wrappedNativeToken=WrappedNativeTokenMock \
        SmartVaultHarness:priceOracle=PriceOracleMock \
        SmartVaultHarness:swapConnector=SwapConnectorMock \
        SmartVaultHarness:feeCollector=DummyERC20FeeCollectorMock \
--packages @openzeppelin=node_modules/@openzeppelin @mimic-fi=node_modules/@mimic-fi \
--path . \
--solc solc8.2 \
--loop_iter 1 \
--optimistic_loop \
--settings -optimisticFallback=true \
--settings -contractRecursionLimit=1 \
$RULE  \
--msg "mimic -$RULE $MSG" \
--staging #alex/remove-call-cvl-keyword

# --staging alex/remove-call-cvl-keyword
# --disableLocalTypeChecking \
# --cloud #\
#

#--debug


#            node_modules/@openzeppelin/contracts/utils/Address.sol \
#--settings -contractRecursionLimit=1 \
#--settings -mediumTimeout=600 \
#--rule_sanity #\
#--debug

#--settings -depth=13 \
#--settings -divideNoRemainder=true \
#--optimistic_loop \
#--staging \
#--settings -t=800 \
#--settings -optimisticFallback=true --optimistic_loop \
#--settings -enableEqualitySaturation=false \


# additional parameters that might be helpful:
#--optimistic_loop
#--settings -optimisticFallback=true \
#--settings -enableEqualitySaturation=false
#--settings -simplificationDepth=10 \
#--settings -s=z3 \
#--setting -cegar=true \ #not working flag




# The goal of this script is the help run the tool
# without having to enter manually all the required
# parameters every time a test is executed
#
# The script should be executed from the terminal,
# with the project folder as the working folder
#
#
# The script can be run either with:
#
# 1) no parameters --> all the rules in the .spec file are tested
#    example:
#
#    ./certora/scripts/run.sh
# 
#
# 2) with one parameter only --> the parameter states the rule name
#    example, when the rule name is "integrityOfDeposit":
#
#    ./certora/scripts/run.sh integrityOfDeposit
#
#
# 3) with two parameters:
#     - the first parameter is the rule name, as in 2)
#     - the second parameter is an optional message to help distinguish the rule
#       the second parameter should be encircled "with quotes"
#    example:
#
#    ./certora/scripts/run.sh integrityOfDeposit "user should get X for any deposit"