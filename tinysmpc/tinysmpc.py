from .finite_ring import assert_is_element, mod, rand_element
from .secret_share import n_to_shares, n_from_shares
from .shared_addition import add_2sh, add_sh_pub
from .shared_multiplication import mult_2sh, mult_sh_pub

class VirtualMachine():
    '''A very simple class that represents a machine's data. 
       It just has a name and owns objects (PrivateScalars and Shares).'''
    def __init__(self, name):
        self.name = name
        self.objects = []
    
    def __repr__(self):
        return f'VirtualMachine(\'{self.name}\')\n - ' + '\n - '.join(map(str, self.objects))

class PrivateScalar():
    '''A class that represents a secret number that belongs to a machine.'''
    def __init__(self, value, owner):
        self.value = value
        self.owner = owner
        owner.objects.append(self)

    def share(self, machines, Q=None):
        '''Split self.value into secret shares and distribute them across machines (tracked in a SharedScalar).'''
        shares = n_to_shares(self.value, machines + [self.owner], Q)
        return SharedScalar(shares, Q)
    
    def __repr__(self):
        return f'PrivateScalar({self.value}, \'{self.owner.name}\')'
    
class SharedScalar():
    '''A class that tracks all secret shares that corresponds to one PrivateScalar.
       It supports *secure* arithmetic with other SharedScalars or integers (+, -, *).'''
    def __init__(self, shares, Q=None):
        assert all(share.Q == Q for share in shares)
        self.shares = shares
        self.share_of = {share.owner: share for share in shares}
        self.owners = {share.owner for share in shares}
        self.Q = Q
        
    def reconstruct(self, owner):
        '''Send all shares to one machine, and reconstruct the hidden value as a PrivateScalar.'''
        value = n_from_shares(self.shares, owner, self.Q)
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
        return 'SharedScalar\n - ' + '\n - '.join(map(str, self.shares))
    
    def _assert_can_operate(self, other):
        '''Assert that two SharedScalars have the same owners and rings.'''
        assert self.owners == other.owners, f'{self}\nand\n{other}\ndo not have the same owners.'
        assert self.Q == other.Q, f'{self}\nand\n{other}\nare not over the same rings.'