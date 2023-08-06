import functools

import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def gpu_from_numpy():
    torch.default_from_numpy = torch.from_numpy

    def func(*args, **kwargs):
        result = torch.default_from_numpy(*args, **kwargs)
        return result.float().to(device)

    torch.from_numpy = func


class MyModuleType(type):

    def __call__(self, *args, **kwargs):
        ins = super().__call__(*args, **kwargs)
        ins.to(device)
        return ins


class GpuModule(torch.nn.Module, metaclass=MyModuleType):


    def __init__(self):
        super(GpuModule, self).__init__()

def on_gpu():
    """

    :return:
    """
    # Create tensor on gpu by default
    torch.set_default_tensor_type('torch.cuda.FloatTensor')

    gpu_from_numpy()

    # Bind module to gpu by default
    torch.nn.Module = GpuModule
