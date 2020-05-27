# This module defines multiplication on SharedScalars.
# 
# Small hack:
# 
# We can't import the SharedScalar class in this module as that would
# create a circular dependency. 
# 
# However, we'd obviously still like to be able to construct new 
# SharedScalars here when doing arithmetic. To be able to do so, 
# we can use `type(sh)` to get access to the SharedScalar class &
# constructor.

from .finite_ring import mod, rand_element
from random import choice

def mult_2sh(sh1, sh2):
    '''Implements multiplication on two SharedScalars.'''
    # To do the multiplication, we do the SPDZ protocol as described in:
    # https://bristolcrypto.blogspot.com/2016/10/what-is-spdz-part-2-circuit-evaluation.html
    sh1._assert_can_operate(sh2)
    
    # A necessary evil. I can't think of a way around this dynamic import yet.
    from .tinysmpc import PrivateScalar
    
    # Generate a random multiplication triple (public)
    a, b = rand_element(sh1.Q), rand_element(sh1.Q)
    c = mod(a * b, sh1.Q)

    # Share the triple across machines
    rand_owner = choice(sh1.shares).owner
    other_owners = list(sh1.owners - {rand_owner})
    shared_a = PrivateScalar(a, rand_owner).share(other_owners, Q=sh1.Q)
    shared_b = PrivateScalar(b, rand_owner).share(other_owners, Q=sh1.Q)
    shared_c = PrivateScalar(c, rand_owner).share(other_owners, Q=sh1.Q)

    # Compute sh1 - a, sh2 - b (shared)
    shared_self_m_a = sh1 - shared_a
    shared_other_m_b = sh2 - shared_b

    # Reconstruct sh1 - a, sh2 - b (public)
    self_m_a = shared_self_m_a.reconstruct(rand_owner).value
    other_m_b = shared_other_m_b.reconstruct(rand_owner).value

    # Magic! Compute each machine's share of the product
    shared_prod = shared_c + (self_m_a * shared_b) + (other_m_b * shared_a) + (self_m_a * other_m_b)
    return shared_prod

def mult_sh_pub(sh, pub):
    '''Implements multiplication on a SharedScalar and a public integer.'''
    # To do the multiplication, we multiply the integer with all shares
    prod_shares = [share * pub for share in sh.shares]
    return type(sh)(prod_shares, Q=sh.Q)
    
