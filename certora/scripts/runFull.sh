certoraRun  certora/harness/SmartVaultHarness.sol \
            certora/harness/PriceOracleHarness.sol \
            packages/smart-vault/contracts/test/samples/TokenMock.sol \
            packages/smart-vault/contracts/test/samples/WrappedNativeTokenMock.sol \
            packages/smart-vault/contracts/test/core/SwapConnectorMock.sol \
            packages/smart-vault/contracts/test/core/StrategyMock.sol \
            packages/registry/contracts/registry/Registry.sol \
            packages/smart-vault/contracts/test/samples/DexMock.sol \
\
--verify SmartVaultHarness:certora/specs/SmartVault.spec \
\
--link  SmartVaultHarness:wrappedNativeToken=WrappedNativeTokenMock \
        SmartVaultHarness:priceOracle=PriceOracleHarness \
        SmartVaultHarness:swapConnector=SwapConnectorMock \
        SwapConnectorMock:dex=DexMock \
\
--packages @openzeppelin=node_modules/@openzeppelin @mimic-fi=node_modules/@mimic-fi @uniswap=node_modules/@uniswap @chainlink=node_modules/@chainlink \
--path . \
--solc solc8.2 \
--send_only \
--staging \
--loop_iter 2 \
--optimistic_loop \
--rule priceInvertible \
--settings -optimisticFallback=true,-contractRecursionLimit=1 \
--msg "mimic SmartVault: priceInvertible" 