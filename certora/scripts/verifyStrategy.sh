if [[ "$1" ]]
then
    RULE="--rule $1"
fi

if [[ "$2" ]]
then
    MSG=": $2"
fi

certoraRun  certora/harness/SmartVaultHarnessStrategy.sol \
            packages/smart-vault/contracts/test/samples/TokenMock.sol \
            certora/harness/Aave/AaveV2Token.sol \
            certora/harness/Aave/incentivesControllerMock.sol:incentivesController \
            certora/harness/Aave/lendingPoolMock.sol:lendingPool \
            certora/harness/PriceOracleHarness.sol \
\
--verify SmartVaultHarnessStrategy:certora/specs/Strategy.spec \
\
--link  SmartVaultHarnessStrategy:Token=TokenMock \
        SmartVaultHarnessStrategy:aToken=AaveV2Token \
        SmartVaultHarnessStrategy:priceOracle=PriceOracleHarness \
        SmartVaultHarnessStrategy:lendingPool=lendingPool \
        SmartVaultHarnessStrategy:incentivesController=incentivesController \
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
--rule_sanity basic \
--settings -optimisticFallback=true,-contractRecursionLimit=1,-byteMapHashingPrecision=10,-mediumTimeout=800 \
--msg "mimic: $RULE $MSG" 