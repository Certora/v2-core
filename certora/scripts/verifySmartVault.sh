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

if [[ "$1" ]]
then
    RULE="--rule $1"
fi

if [[ "$2" ]]
then
    MSG=": $2"
fi

certoraRun  certora/harness/SmartVaultHarness.sol \
            certora/harness/PriceOracleHarness.sol \
            packages/smart-vault/contracts/test/samples/TokenMock.sol \
            packages/smart-vault/contracts/test/samples/WrappedNativeTokenMock.sol \
            packages/smart-vault/contracts/test/core/SwapConnectorMock.sol \
            packages/registry/contracts/registry/Registry.sol \
            packages/smart-vault/contracts/test/samples/DexMock.sol \
            certora/harness/Aave/AaveV2Token.sol \
            certora/harness/Aave/incentivesControllerMock.sol:incentivesController \
            certora/harness/Aave/lendingPoolMock.sol:lendingPool \
\
--verify SmartVaultHarness:certora/specs/SmartVault.spec \
\
--link  SmartVaultHarness:wrappedNativeToken=WrappedNativeTokenMock \
        SmartVaultHarness:priceOracle=PriceOracleHarness \
        SmartVaultHarness:swapConnector=SwapConnectorMock \
        SmartVaultHarness:Token=TokenMock \
        SmartVaultHarness:aToken=AaveV2Token \
        SmartVaultHarness:lendingPool=lendingPool \
        SmartVaultHarness:incentivesController=incentivesController \
        SwapConnectorMock:dex=DexMock \
        AaveV2Token:pool=lendingPool \
        AaveV2Token:incentivesController=incentivesController \
\
\
--packages @openzeppelin=node_modules/@openzeppelin @mimic-fi=node_modules/@mimic-fi @uniswap=node_modules/@uniswap @chainlink=node_modules/@chainlink \
--path . \
--solc solc8.2 \
--send_only \
--staging \
--loop_iter 2 \
--optimistic_loop \
$RULE  \
--settings -optimisticFallback=true,-contractRecursionLimit=1,-mediumTimeout=800 \
--msg "mimic -$RULE $MSG"