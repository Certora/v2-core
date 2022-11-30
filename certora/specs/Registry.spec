methods {
    implementationOf(address) returns(address) envfree
    implementationData(address) envfree
    clone(address, bytes) returns (address) envfree
    register(bytes32, address, bool)
    deprecate(address)
}

rule sanity(method f) {
    env e;
    calldataarg args;
    f(e, args);
    assert false;
}
 
rule cloneIsNotImplementation(address implementation) {
    bytes data;
    address instance = clone(implementation, data);
    assert implementation != instance;
}

rule canAlwaysCloneAClone(address impl) {
    bytes data1;
    bytes data2;
    address instance = clone(impl, data1);
    clone@withrevert(instance, data2);
    assert !lastReverted;
}

rule cannotRegisterClonedImplementation(address impl, method f)
filtered{f -> !f.isView} {
    env e1; env e2;
    calldataarg args;
    bytes data1;
    bytes32 namespace;
    bool stateless;
    address instance = clone(impl, data1);
    f(e1, args);
    register@withrevert(e2, namespace, instance, stateless);
    assert lastReverted;
}

rule cannotRegisterSameInstanceTwice(address instance, method f) 
filtered{f -> !f.isView} {
    env e1; env e2; env e3;
    calldataarg args;
    bytes32 namespace1;
    bytes32 namespace2;
    bool stateless1;
    bool stateless2;
    register(e1, namespace1, instance, stateless1);
    f(e2, args);
    register@withrevert(e3, namespace2, instance, stateless2);
    assert lastReverted;
}

rule cannotDeprecateTwice(address implementation) {
    env e1;
    env e2;
    deprecate(e1, implementation);
    deprecate@withrevert(e2, implementation);
    assert lastReverted;
}

rule frontRunning_clone(address impl, method f) {
    env e;
    calldataarg args;
    bytes data;
    storage initStorage = lastStorage;
    address instance = clone(impl, data);

    f(e, args) at initStorage;
    address instanceNew = clone@withrevert(impl, data);

    assert instance == instanceNew;
    assert (instance == instanceNew) => !lastReverted;
}

rule frontRunning_deprecate(address impl, method f) 
filtered{f -> f.selecotr != deprecate(address).selector} {
    env e1; env e2;
    calldataarg args;
    storage initStorage = lastStorage;
    deprecate(e1, impl);

    f(e2, args) at initStorage;
    deprecate@withrevert(e1, impl);

    assert !lastReverted;
}