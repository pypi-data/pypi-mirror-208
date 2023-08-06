import torch


def init_seed(self, kwargs):

    if 'seed' in kwargs:

        seed = kwargs['seed']

    else:

        seed = 0

    torch.manual_seed(seed)
