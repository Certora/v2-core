if [[ "$1" ]]
then
    RULE="--rule $1"
fi

if [[ "$2" ]]
then
    MSG=": $2"
fi

certoraRun  certora/harness/PriceOracleHarness.sol \
--verify PriceOracleHarness:certora/specs/PriceOracle.spec \
--packages @chainlink=node_modules/@chainlink @openzeppelin=node_modules/@openzeppelin @mimic-fi=node_modules/@mimic-fi \
--path . \
--solc solc8.2 \
--loop_iter 1 \
--optimistic_loop \
--settings -optimisticFallback=true \
--settings -contractRecursionLimit=1 \
$RULE  \
--msg "mimic PriceOracle -$RULE $MSG" \
--staging