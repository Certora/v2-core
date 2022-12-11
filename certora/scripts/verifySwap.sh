certoraRun  certora/harness/SmartVaultHarnessSwap.sol \
            certora/harness/PriceOracleHarness.sol \
            packages/smart-vault/contracts/test/samples/DexMock.sol \
            certora/harness/Tokens/DummyERC20A.sol certora/harness/Tokens/DummyERC20B.sol \
            certora/harness/Tokens/DummyERC20FeeCollectorMock.sol \
\
--verify SmartVaultHarnessSwap:certora/specs/SwapCheck.spec \
\
--link  SmartVaultHarnessSwap:dex=DexMock \
        SmartVaultHarnessSwap:priceOracle=PriceOracleHarness \
\
\
--packages @openzeppelin=node_modules/@openzeppelin @mimic-fi=node_modules/@mimic-fi @uniswap=node_modules/@uniswap @chainlink=node_modules/@chainlink \
--path . \
--solc solc8.2 \
--send_only \
--staging \
--loop_iter 2 \
--optimistic_loop \
--rule $1 \
--rule_sanity basic \
--settings -optimisticFallback=true,-contractRecursionLimit=1,-byteMapHashingPrecision=10,-mediumTimeout=800 \
--msg "SmartVault: swap - $1 - " 