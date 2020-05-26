from random import choice, randint, randrange

# Mathematical note:
#
# For additive secret sharing to work, we need all of the numbers we're working with
# to be in a finite abelian group under addition. [1] 
# 
# (Technically, for SMPC with additive secret sharing, we'd like multiplication to work
# as well, so we're actually operating in a ring.)
# 
# This is not a problem, because int64 is a finite ring! [2]
# 
# Another popular choice of a finite abelian ring is the integers modulo a prime [3], 
# with the caveat that this doesn't support negative numbers. Thus, this implementation
# defaults to using the int64 ring. We support prime rings as well, which are explicitly
# used in the PrivateCompare algorithm.
#
# [1] 6.1 in https://cs.nyu.edu/courses/spring07/G22.3033-013/scribe/lecture01.pdf
# [2] https://math.stackexchange.com/q/3692052/28855
# [3] https://mortendahl.github.io/2017/09/03/the-spdz-protocol-part1/

MAX_INT64 =  9223372036854775807
MIN_INT64 = -9223372036854775808

def mod(n, Q=None):
    '''Keeps n inside the finite ring. That is:
         - If we're in a prime ring (Q is the prime size), modulo it by Q
         - If we're in the int64 ring, do the normal int64 overflow behavior
           (we need to explicitly overflow since Python3 ints are unbounded)
    '''
    if Q is not None: return n % Q
    return (n + MAX_INT64 + 1) % 2**64 - (MAX_INT64 + 1)  # https://stackoverflow.com/a/7771499/908744
    
def rand_element(Q=None):
    '''Generates a random int64, or a random integer [0, Q) if Q is specified.
       i.e. an element of the int64 ring, or the size-Q prime ring.'''
    if Q is not None: return randrange(Q)
    return randint(MIN_INT64, MAX_INT64)

class VirtualMachine():
    '''A very simple class that represents a machine's data. 
       It just has a name and owns objects (PrivateScalars and Shares).'''
    def __init__(self, name):
        self.name = name
        self.objects = []
    
    def __repr__(self):
        string = f'Machine(\'{self.name}\') has:\n'
        for obj in self.objects: string += f'    {obj}\n'
        return string

class PrivateScalar():
    '''A class that represents a (secret) number that belongs to a machine.'''
    def __init__(self, value, owner):
        self.value = value
        self.owner = owner
        owner.objects.append(self)

    def share(self, machines, Q=None):
        '''Generate additive secret shares of self.value, and distribute them to machines.'''
        # Make sure we're sharing across unique machines
        assert self.owner not in machines
        assert len(machines) == len(set(machines))        
        
        # Make sure the value fits into the finite ring so it's possible to reconstruct it!
        if Q is None: assert MIN_INT64 <= self.value <= MAX_INT64, f'{self} is not an int64 and cannot be reconstructed. Use a smaller value.'
        else: assert 0 <= self.value < Q, f'{self} does not fit in this size-{Q} prime ring, so cannot be split into shares that can reconstruct it. Use a larger Q or a smaller value.'
        
        # Generate the value of each share using additive secret sharing
        values = [rand_element(Q) for _ in machines]
        values.append(mod(self.value - sum(values), Q))

        # Give one share to each machine
        shares = [Share(value, machine, Q) for value, machine in
                  zip(values, machines + [self.owner])]

        # Return a SharedScalar that tracks all of these shares
        return SharedScalar(shares, Q)
    
    def __repr__(self):
        return f'PrivateScalar({self.value}, \'{self.owner.name}\')'
            
class Share():
    '''A class that represents a secret share that belongs to a machine.
       It supports normal arithmetic with other Shares or integers (+, -, *).'''
    def __init__(self, value, owner, Q=None):
        if Q is not None: assert 0 <= value < Q        
        self.value = value
        self.owner = owner
        self.Q = Q
        owner.objects.append(self)
    
    # Called by: self + other
    def __add__(self, other):
        if self.Q is None:
            # Addition of a Share and a public integer known to all machines
            if isinstance(other, int):
                sum_value = mod(self.value + other)

            # Addition of two Shares
            elif isinstance(other, Share):
                assert self.owner == other.owner
                sum_value = mod(self.value + other.value)

            return Share(sum_value, self.owner)
        
        else:
            # Addition of a Share and a public integer known to all machines
            if isinstance(other, int):
                sum_value = mod(self.value + other, self.Q)

            # Addition of two Shares
            elif isinstance(other, Share):
                assert self.owner == other.owner
                sum_value = mod(self.value + other.value, self.Q)

            return Share(sum_value, self.owner, self.Q)
    
    # Called by: other + self (when other is not a Share)
    def __radd__(self, other):
        return self.__add__(other)
    
    # Called by: self - other
    def __sub__(self, other):
        return self.__add__(-1*other)
    
    # Called by: other - self (when other is not a Share)
    def __rsub__(self, other):
        return (-1*self).__add__(other)
    
    # Called by: self * other
    def __mul__(self, other):
        if self.Q is None:
            # Multiplication of a Share and a public integer known to all machines
            if isinstance(other, int):
                prod_value = mod(self.value * other)

            # Multiplication of two Shares
            elif isinstance(other, Share):
                assert self.owner == other.owner
                prod_value = mod(self.value * other.value)

            return Share(prod_value, self.owner)

        else:
            # Multiplication of a Share and a public integer known to all machines
            if isinstance(other, int):
                prod_value = mod(self.value * other, self.Q)

            # Multiplication of two Shares
            elif isinstance(other, Share):
                assert self.owner == other.owner
                prod_value = mod(self.value * other.value, self.Q)

            return Share(prod_value, self.owner, self.Q)
    
    # Called by: other * self (when other is not a Share)  
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __repr__(self):
        return f'Share({self.value}, \'{self.owner.name}\', Q={self.Q})'
    
class SharedScalar():
    '''A class that tracks all secret shares that corresponds to one PrivateScalar.
       It supports *secure* arithmetic with other SharedScalars or integers (+, -, *).'''
    def __init__(self, shares, Q=None):
        if Q is None: assert all(share.Q == Q for share in shares)
        self.shares = shares
        self.owners = {share.owner for share in shares}
        self.share_of = {share.owner: share for share in shares}
        self.Q = Q
        
    def reconstruct(self, owner):
        '''Send all secret shares to owner (can be anyone), and reconstruct the PrivateScalar value on that machine.'''
        values = [share.value for share in self.shares]
        if self.Q is None:
            value = mod(sum(values))
        else:
            value = mod(sum(values), self.Q)
        return PrivateScalar(value, owner)
    
    # Called by: self + other
    def __add__(self, other):
        # Addition of a SharedScalar and a public integer known to all machines
        if isinstance(other, int):
            # To do the addition, we add the integer to one (random) share only
            new_share = self.shares[0] + other
            return SharedScalar([new_share] + self.shares[1:], Q=self.Q)

        # Addition of two SharedScalars
        elif isinstance(other, SharedScalar):
            # To do the addition, we add each machine's shares together
            assert self.owners == other.owners
            sum_shares = [self.share_of[owner] + other.share_of[owner]
                          for owner in self.owners]
            return SharedScalar(sum_shares, Q=self.Q)
        
    # Called by: other + self (when other is not a SharedScalar)
    def __radd__(self, other):
        return self.__add__(other)
    
    # Called by: self - other
    def __sub__(self, other):
        return self.__add__(-1*other)
    
    # Called by: other - self (when other is not a SharedScalar)
    def __rsub__(self, other):
        return (-1*self).__add__(other)
    
    # Called by: self * other
    def __mul__(self, other):
        # Multiplication of a SharedScalar and a public integer known to all machines
        if isinstance(other, int):
            # To do the multiplication, we multiply the integer with all shares
            prod_shares = [share * other for share in self.shares]
            return SharedScalar(prod_shares, Q=self.Q)
            
        # Multiplication of two SharedScalars
        elif isinstance(other, SharedScalar):
            # To do the multiplication, we do the SPDZ protocol as described in:
            # https://bristolcrypto.blogspot.com/2016/10/what-is-spdz-part-2-circuit-evaluation.html
            assert self.owners == other.owners

            # Generate a random multiplication triple (public)
            if self.Q is None:
                a, b = randint(MIN_INT64, MAX_INT64), randint(MIN_INT64, MAX_INT64)
                c = mod(a * b)
            else:
                a, b = randrange(self.Q), randrange(self.Q)
                c = mod(a * b, self.Q)

            # Share the triple across machines
            rand_owner = choice(self.shares).owner
            other_owners = list(self.owners - {rand_owner})
            shared_a = PrivateScalar(a, rand_owner).share(other_owners, Q=self.Q)
            shared_b = PrivateScalar(b, rand_owner).share(other_owners, Q=self.Q)
            shared_c = PrivateScalar(c, rand_owner).share(other_owners, Q=self.Q)

            # Compute self - a, other - b (shared)
            shared_self_m_a = self - shared_a
            shared_other_m_b = other - shared_b

            # Reconstruct self - a, other - b (public)
            self_m_a = shared_self_m_a.reconstruct(rand_owner).value
            other_m_b = shared_other_m_b.reconstruct(rand_owner).value
            
            # Magic! Compute each machine's share of the product
            shared_prod = shared_c + (self_m_a * shared_b) + (other_m_b * shared_a) + (self_m_a * other_m_b)
            return shared_prod
            
    # Called by: other * self (when other is not a SharedScalar)  
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __repr__(self):
        string = 'SharedScalar(\n'
        for share in self.shares: string += f'    {share}\n'
        return string + ')'