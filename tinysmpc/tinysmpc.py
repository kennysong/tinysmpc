from .finite_ring import assert_is_element, mod, rand_element 
from .shared_addition import add_2sh, add_sh_pub
from .shared_multiplication import mult_2sh, mult_sh_pub

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
    '''A class that represents a secret number that belongs to a machine.'''
    def __init__(self, value, owner):
        self.value = value
        self.owner = owner
        owner.objects.append(self)

    def share(self, machines, Q=None):
        '''Generate additive secret shares of self.value, and distribute them to machines.'''
        # Make sure we're sharing across unique machines
        assert self.owner not in machines
        assert len(machines) == len(set(machines))
        
        # Make sure the number actually fits into the finite ring, so we can reconstruct it!
        assert_is_element(self, Q)
        
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
        assert_is_element(value, Q)
        self.value = value
        self.owner = owner
        self.Q = Q
        owner.objects.append(self)
    
    def __add__(self, other):
        '''Called by: self + other.'''
        self._assert_can_operate(other)
        other_value = other if isinstance(other, int) else other.value 
        sum_value = mod(self.value + other_value, self.Q)
        return Share(sum_value, self.owner, self.Q)
    
    def __radd__(self, other):
        '''Called by: other + self (when other is not a Share).'''
        return self.__add__(other)
    
    def __sub__(self, other):
        '''Called by: self - other.'''
        return self.__add__(-1*other)
    
    def __rsub__(self, other):
        '''Called by: other - self (when other is not a Share).'''
        return (-1*self).__add__(other)
    
    def __mul__(self, other):
        '''Called by: self * other.'''
        self._assert_can_operate(other)
        other_value = other if isinstance(other, int) else other.value
        prod_value = mod(self.value * other_value, self.Q)
        return Share(prod_value, self.owner, self.Q)
    
    def __rmul__(self, other):
        '''Called by: other * self (when other is not a Share).'''
        return self.__mul__(other)
    
    def __repr__(self):
        return f'Share({self.value}, \'{self.owner.name}\', Q={self.Q})'
    
    def _assert_can_operate(self, other):
        '''Assert that both Shares have the same owners and rings.'''
        if isinstance(other, int): return  # It's okay to do operations with any public integers
        assert self.owner == other.owner, f'{self} and {other} do not have the same owners.'
        assert self.Q == other.Q, f'{self} and {other} are not over the same rings.'
    
class SharedScalar():
    '''A class that tracks all secret shares that corresponds to one PrivateScalar.
       It supports *secure* arithmetic with other SharedScalars or integers (+, -, *).'''
    def __init__(self, shares, Q=None):
        if Q is None: assert all(share.Q == Q for share in shares)
        self.shares = shares
        self.share_of = {share.owner: share for share in shares}
        self.owners = {share.owner for share in shares}
        self.Q = Q
        
    def reconstruct(self, owner):
        '''Send all secret shares to owner (can be anyone), and reconstruct the PrivateScalar value on that machine.'''
        values = [share.value for share in self.shares]
        value = mod(sum(values), self.Q)
        return PrivateScalar(value, owner)
        
    def __add__(self, other):
        '''Called by: self + other.'''
        if isinstance(other, int):            return add_sh_pub(self, other)
        elif isinstance(other, SharedScalar): return add_2sh(self, other)
        
    def __radd__(self, other):
        '''Called by: other + self (when other is not a SharedScalar).'''
        return self.__add__(other)
    
    def __sub__(self, other):
        '''Called by: self - other.'''
        return self.__add__(-1*other)
    
    def __rsub__(self, other):
        '''Called by: other - self (when other is not a SharedScalar).'''
        return (-1*self).__add__(other)
    
    def __mul__(self, other):
        '''Called by: self * other.'''
        if isinstance(other, int):            return mult_sh_pub(self, other)
        elif isinstance(other, SharedScalar): return mult_2sh(self, other)
            
    def __rmul__(self, other):
        '''Called by: other * self (when other is not a SharedScalar).'''
        return self.__mul__(other)
    
    def __repr__(self):
        string = 'SharedScalar(\n'
        for share in self.shares: string += f'    {share}\n'
        return string + ')'
    
    def _assert_can_operate(self, other):
        '''Assert that both SharedScalars have the same owners and rings.'''
        assert self.owners == other.owners, f'{self} and {other} do not have the same owners.'
        assert self.Q == other.Q, f'{self} and {other} are not over the same rings.'