# TinySMPC 🛡️

A tiny library for [secure multi-party computation](https://en.wikipedia.org/wiki/Secure_multi-party_computation), in pure Python!

This code is intended for educational rather than practical purposes. It exposes a simple API, and the underlying implementation is written to be understandable and minimalistic. 

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
shared_a = a.share([alice, bob, charlie])
shared_b = b.share([alice, bob, charlie])
shared_c = c.share([alice, bob, charlie])
```

Compute some arithmetic function directly on the encrypted shares.

```python
shared_output = (shared_a * shared_b) - 5 * (shared_a + shared_c)
```

Decrypt the function's output by sending all encrypted shares to Charlie (or anyone).

```python
shared_output.reconstruct(charlie)
>>> PrivateScalar(1075, 'charlie')
```

Alice, Bob, and Charlie have jointly computed a function on their data, without seeing anyone else's secret data!

## Implementation

TinySMPC implements [additive secret sharing](https://cs.nyu.edu/courses/spring07/G22.3033-013/scribe/lecture01.pdf) for creating encrypted shares on private data.

On top of additive secret sharing, we implement several [SMPC](https://en.wikipedia.org/wiki/Secure_multi-party_computation) protocols, which allow us to directly perform computations on encrypted data.

Here's a summary of the encrypted operations that TinySMPC provides.

|                    | Supported?              | Implementation                                                                          |
|--------------------|-------------------------|-----------------------------------------------------------------------------------------|
| **Addition**       | ✅                       | [SPDZ](https://eprint.iacr.org/2011/535.pdf) algorithm. <br/> See [shared_addition.py](https://github.com/kennysong/tinysmpc/blob/master/tinysmpc/shared_addition.py)             |
| **Subtraction**    | ✅                       | In terms of addition and multiplication.                                                 |
| **Multiplication** | ✅                       | [SPDZ](https://eprint.iacr.org/2011/535.pdf) algorithm.  <br/> See [shared_multiplication.py](https://github.com/kennysong/tinysmpc/blob/master/tinysmpc/shared_multiplication.py) |
| **Division**       | ❌ (too complicated)     | Possible with [SecureNN](https://eprint.iacr.org/2018/442.pdf).                                                                                       |
| **Exponentiation**       | ✅ (public integer only)     | In terms of multiplication.                                                                                       |
| **Greater Than**   | ✅ (public integer only) | [SecureNN](https://eprint.iacr.org/2018/442.pdf) algorithm. <br/> See [shared_comparison.py](https://github.com/kennysong/tinysmpc/blob/master/tinysmpc/shared_comparison.py)     |
