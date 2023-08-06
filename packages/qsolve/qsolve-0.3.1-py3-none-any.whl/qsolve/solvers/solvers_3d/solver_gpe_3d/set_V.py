def set_V(self, kwargs):

    u = kwargs['u']

    self.V = self.potential.eval(u)
