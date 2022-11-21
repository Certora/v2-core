if [[ "$1" ]]
then
    RULE="--rule $1"
fi

if [[ "$2" ]]
then
    MSG=": $2"
fi

certoraRun  certora/harness/CompoundStrategyHarness.sol \
--verify CompoundStrategyHarness:certora/specs/CompoundStrategy.spec \
--packages @chainlink=node_modules/@chainlink @openzeppelin=node_modules/@openzeppelin @mimic-fi=node_modules/@mimic-fi \
--path . \
--solc solc8.2 \
--loop_iter 2 \
--optimistic_loop \
--settings -optimisticFallback=true \
--settings -contractRecursionLimit=1 \
$RULE  \
--msg "mimic CompoundStrategy -$RULE $MSG" \
--send_only \
--staging