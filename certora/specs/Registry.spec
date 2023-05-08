methods {
    function implementationOf(address) external returns(address) envfree;
    function implementationData(address) external returns (bool, bool, bytes32) envfree;
    function clone(address, bytes) external returns (address) envfree;
    function register(bytes32, address, bool) external;
    function deprecate(address) external;
    function isAuthorized(address, bytes4) external returns (bool) envfree;
}

rule sanity(method f) {
    env e;
    calldataarg args;
    f(e, args);
    assert false;
}

rule onlyCloneChangesInstanceImplementation(address instance, method f) {
    env e;
    calldataarg args;
    address implementation1 = implementationOf(instance);
        f(e, args);
    address implementation2 = implementationOf(instance);
    
    assert implementation2 != implementation1 => f.selector == sig:clone(address, bytes).selector;
}

rule cloneIntegrity(address implementation) {
    bytes data;
    address otherInstance;
    address otherImplementation1 = implementationOf(otherInstance);
    address clonedInstance = clone(implementation, data);
    address otherImplementation2 = implementationOf(otherInstance);
    
    assert implementation == implementationOf(clonedInstance);
    assert clonedInstance != otherInstance => otherImplementation2 == otherImplementation1;
}

rule instanceImplemenationIsPreserved(address instance) {
    calldataarg args;
    
    address implementation = implementationOf(instance);
    require implementation !=0;

    address clonedInstance = clone(args);
    // Here we assume that the 'create' function cannot yield the same cloned address.
    require clonedInstance != instance;

    assert implementationOf(instance) == implementation;
}

rule ImplDataModifiedOnlyOnce(address implementation, method f, method g)
filtered{f -> !f.isView, g -> !g.isView} {
    env e1; env e2;
    calldataarg args1;
    calldataarg args2;
    bool statelessA; bool statelessB; bool statelessC;
    bool deprecatedA; bool deprecatedB; bool deprecatedC;
    bytes32 namespaceA; bytes32 namespaceB; bytes32 namespaceC;

    statelessA, deprecatedA, namespaceA = implementationData(implementation);
        f(e1, args1);
    statelessB, deprecatedB, namespaceB = implementationData(implementation);
        g(e2, args2);
    statelessC, deprecatedC, namespaceC = implementationData(implementation);

    // This is the post-constructor state:
    require !deprecatedA;
    require !statelessA;

    // Deprecate changes only once
    assert (deprecatedA != deprecatedB) => (deprecatedB == deprecatedC);
    // If deprecate is changed, it will stay 'true' always.
    assert (deprecatedA != deprecatedB) => deprecatedB;
    // Stateless changes only once.
    assert (statelessA != statelessB) => (statelessB == statelessC);
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

// This rule fails (even for view functions!) because the low-level call
// inside 'clone' is non-determinstic with respect to storage and input.
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
filtered{f -> f.selector != sig:deprecate(address).selector} {
    env e1; env e2;
    calldataarg args;
    storage initStorage = lastStorage;
    deprecate(e1, impl);

    f(e2, args) at initStorage;
    deprecate@withrevert(e1, impl);

    assert !lastReverted;
}

rule frontRunning_register(address instance, method f) {
    env e1; env e2;
    calldataarg args;
    bytes32 namespace;
    bool stateless;
    storage initStorage = lastStorage;
    register(e1, namespace, instance, stateless);
    
    f(e2, args) at initStorage;
    register@withrevert(e1, namespace, instance, stateless);

    assert !lastReverted;
}