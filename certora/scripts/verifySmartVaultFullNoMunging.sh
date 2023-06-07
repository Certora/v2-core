certoraRun  certora/harness/SmartVaultHarnessNoMunging.sol \
            certora/harness/PriceOracleHarnessNoMunging.sol \
            packages/smart-vault/contracts/test/samples/TokenMock.sol \
            packages/smart-vault/contracts/test/samples/WrappedNativeTokenMock.sol \
            packages/smart-vault/contracts/test/core/SwapConnectorMock.sol \
            packages/registry/contracts/registry/Registry.sol \
            packages/smart-vault/contracts/test/samples/DexMock.sol \
            certora/harness/Aave/AaveV2Token.sol \
            certora/harness/Aave/incentivesControllerMock.sol:incentivesController \
            certora/harness/Aave/lendingPoolMock.sol:lendingPool \
            packages/strategies/contracts/aave-v2/AaveV2Strategy.sol \
            packages/bridge-connector/contracts/BridgeConnector.sol \
            certora/harness/AggregatorV3Mock.sol \
\
--verify SmartVaultHarnessNoMunging:certora/specs/SmartVaultNoMunging.spec \
\
--link  SmartVaultHarnessNoMunging:wrappedNativeToken=WrappedNativeTokenMock \
        SmartVaultHarnessNoMunging:priceOracle=PriceOracleHarnessNoMunging \
        SmartVaultHarnessNoMunging:swapConnector=SwapConnectorMock \
        \
        AaveV2Strategy:token=TokenMock \
        AaveV2Strategy:aToken=AaveV2Token \
        AaveV2Strategy:lendingPool=lendingPool \
        AaveV2Strategy:incentivesController=incentivesController \
        \
        SmartVaultHarnessNoMunging:bridgeConnector=BridgeConnector \
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
--settings -optimisticFallback=true,-contractRecursionLimit=1,-mediumTimeout=800,-copyLoopUnroll=8 \
--msg "SmartVaultFull no-munging: copyLoopUn 8, added AaveV2Strategy, bridge, AggregatorV3Mock, all dispatcher true" \
--rule sanity
# --rule onlyAuthUserCanCallFunctions \
# --rule collectTransferIntegrity \
# --rule withdrawTransferIntegrity \
# --rule withdrawTransferIntegrityOfNativeToken \
# --rule wrapUnwrapIntegrity \
# --rule unwrapWrapIntegrity \
# --rule unwrapCannotRevertAfterWrap \
# --rule wrapCannotRevertAfterUnwrap
# --settings -optimisticFallback=true,-contractRecursionLimit=1,-mediumTimeout=800,-enableEventReporting \
# --staging yuvalbd/rule_events_error_checking_part_two \