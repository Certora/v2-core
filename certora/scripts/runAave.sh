certoraRun  certora/harness/SmartVaultHarnessAave.sol:SmartVaultHarness \
            certora/harness/PriceOracleHarness.sol \
            packages/smart-vault/contracts/test/samples/TokenMock.sol \
            packages/smart-vault/contracts/test/samples/WrappedNativeTokenMock.sol \
            packages/registry/contracts/registry/Registry.sol \
            packages/strategies/contracts/aave-v2/AaveV2Strategy.sol \
            certora/harness/Aave/AaveV2Token.sol \
            certora/harness/Aave/incentivesControllerMock.sol:incentivesController \
            certora/harness/Aave/lendingPoolMock.sol:lendingPool \
\
--verify SmartVaultHarness:certora/specs/SmartVault.spec \
\
--link  SmartVaultHarness:wrappedNativeToken=WrappedNativeTokenMock \
        SmartVaultHarness:priceOracle=PriceOracleHarness \
        SmartVaultHarness:aaveStrategy=AaveV2Strategy \
        AaveV2Strategy:token=TokenMock \
        AaveV2Strategy:aToken=AaveV2Token \
        AaveV2Strategy:lendingPool=lendingPool \
        AaveV2Strategy:incentivesController=incentivesController \
        AaveV2Token:pool=lendingPool \
        AaveV2Token:incentivesController=incentivesController \
\
\
--packages @openzeppelin=node_modules/@openzeppelin @mimic-fi=node_modules/@mimic-fi @uniswap=node_modules/@uniswap @chainlink=node_modules/@chainlink hardhat=packages/swap-connector/node_modules/hardhat \
--path . \
--solc solc8.2 \
--send_only \
--staging jtoman/cer-1481 \
--loop_iter 3 \
--rule exitSanity \
--optimistic_loop \
--settings -optimisticFallback=true,-contractRecursionLimit=1,-mediumTimeout=200,-copyLoopUnroll=9 \
--msg "mimic SmartVault Aave : exit sanity cer1481" 