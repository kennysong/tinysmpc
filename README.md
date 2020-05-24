# MicroSMPC

A minimal implementation of secure multi-party computation, in pure Python!

More useful for pedagogical rather than practical purposes. 

## Overview

*The goal is to allow multiple users/machines to collaboratively compute a function over their secret data (e.g. average, equality, logistic regression), while not exposing anyone's secret data.*

Create a few `VirtualMachines`.

```python
alice = VirtualMachine('alice')
bob = VirtualMachine('bob')
```

Create secret numbers on Alice and Bob's machines.

```python
a = PrivateScalar(25, alice)
b = PrivateScalar(50, bob)
```

Distribute an encrypted fraction of each number to each machine (this uses additive secret sharing).

```python
shared_a = a.share([bob])
shared_b = b.share([alice])
```

Compute any arithmetic function over the encrypted shares.

```python
shared_output =  (shared_a * shared_b) - 5 * (shared_a + shared_b)
```

Decrypt the function's output by sending all encrypted shares to Alice (or vice versa).

```python
shared_output.reconstruct(alice)
>>> PrivateScalar(875, 'alice')
```

Alice and Bob have jointly computed a function over their data, but Alice has no idea what Bob's input was (and vice versa)!

## Status

Todos:
- [ ] Make `PrivateScalar` work for floats with fixed-point encoding
- [ ] Implement shared division
- [ ] Implement shared comparison
- [ ] Implement common functions, e.g. sigmoid, exponential, ReLU (probably Taylor series)
- [ ] Write basic tutorial notebook
- [ ] Clean up intermediate `Shares` used in arithmetic operations from `VirtualMachines`

Done:
- [x] Get `PrivateScalars` onto `VirtualMachines`
- [x] Share a `PrivateScalar` into a `SharedScalar`
- [x] Implement shared addition
- [x] Implement shared multiplication


## Resources

- [Bristol Cryptography Club: What is SPDZ?](https://bristolcrypto.blogspot.com/2016/10/what-is-spdz-part-2-circuit-evaluation.html)
- [Morten Dahl: The SPDZ Protocol](https://mortendahl.github.io/2017/09/03/the-spdz-protocol-part1/)
- [Multiparty Computation from Somewhat Homomorphic Encryption](https://eprint.iacr.org/2011/535.pdf) (original SPDZ paper, much harder to read)
