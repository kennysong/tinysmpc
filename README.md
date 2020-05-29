# TinySMPC 🛡️

A tiny library for [secure multi-party computation](https://en.wikipedia.org/wiki/Secure_multi-party_computation), in pure Python!

This code is intended for educational rather than practical purposes. It exposes a simple API, and the underlying implementation is kept minimalistic and well commented. 

## Overview

*The goal is to allow multiple users/computers to collaboratively compute a function over their secret data (e.g. average, equality, logistic regression), while not exposing anyone's secret data.*

Create a few `VirtualMachines` (think: separate computers that can communicate to each other).

```python
alice = VirtualMachine('alice')
bob = VirtualMachine('bob')
charlie = VirtualMachine('charlie')
```

Create secret numbers on Alice, Bob, and Charlie's machines.

```python
a = PrivateScalar(25, alice)
b = PrivateScalar(50, bob)
c = PrivateScalar(10, charlie)
```

Distribute an encrypted fraction of each number to each machine (this is secret sharing!).

```python
shared_a = a.share([bob, charlie])
shared_b = b.share([alice, charlie])
shared_c = c.share([alice, bob])
```

Compute any arithmetic function over the encrypted shares.

```python
shared_output = (shared_a * shared_b) - 5 * (shared_a + shared_c)
```

Decrypt the function's output by sending all encrypted shares to Charlie (or anyone).

```python
shared_output.reconstruct(charlie)
>>> PrivateScalar(1075, 'charlie')
```

Alice, Bob, and Charlie have jointly computed a function on their data, without seeing anyone else's secret data!

## Status

Todos:
- [ ] Make `PrivateScalar` work for floats with fixed-point encoding
- [ ] Implement common functions, e.g. sigmoid, exponential, ReLU (probably Taylor series)
- [ ] Write basic tutorial notebook
- [ ] Clean up intermediate `Shares` used in arithmetic operations from `VirtualMachines`

Done:
- [x] Get `PrivateScalars` onto `VirtualMachines`
- [x] Share a `PrivateScalar` into a `SharedScalar`
- [x] Implement shared addition
- [x] Implement shared multiplication
- [x] Implement finite ring arithmetic for int64 and mod prime
- [x] Support negative integers
- [x] Implement shared comparison
- [x] Update readme with three VMs
- [x] Clean up package structure

Not in scope:
- [ ] Implement shared division

## Resources

- [Bristol Cryptography Club: What is SPDZ?](https://bristolcrypto.blogspot.com/2016/10/what-is-spdz-part-2-circuit-evaluation.html)
- [Morten Dahl: The SPDZ Protocol](https://mortendahl.github.io/2017/09/03/the-spdz-protocol-part1/)
- [Multiparty Computation from Somewhat Homomorphic Encryption](https://eprint.iacr.org/2011/535.pdf) (original SPDZ paper, much harder to read)
