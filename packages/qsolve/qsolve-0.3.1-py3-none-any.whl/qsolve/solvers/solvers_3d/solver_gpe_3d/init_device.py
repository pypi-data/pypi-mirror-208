import torch


def init_device(self, kwargs):

    if 'device' in kwargs:

        if kwargs['device'] == 'cuda:0':

            self.device = torch.device('cuda:0')

        elif kwargs['device'] == 'cpu':

            self.device = torch.device('cpu')

        else:

            message = 'device \'{0:s}\' not supported'.format(kwargs['device'])

            raise Exception(message)

    else:

        self.device = torch.device('cpu')

    if 'num_threads_cpu' in kwargs:

        torch.set_num_threads(kwargs['num_threads_cpu'])
