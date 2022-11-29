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
--rule whoChangedSmartVaultAllowance \
--settings -optimisticFallback=true,-contractRecursionLimit=1,-mediumTimeout=800 \
--msg "mimic SmartVault: whoChangedSmartVaultAllowance" 