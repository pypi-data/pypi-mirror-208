import torch


def set_psi(self, identifier, kwargs):

    if identifier == 'numpy':

        array_numpy = kwargs['array']

        self.psi = torch.tensor(array_numpy / self.units.unit_wave_function, device=self.device)

    else:

        error_message = 'set_psi(identifier, **kwargs): identifier \'{0:s}\' not supported'.format(identifier)

        exit(error_message)
