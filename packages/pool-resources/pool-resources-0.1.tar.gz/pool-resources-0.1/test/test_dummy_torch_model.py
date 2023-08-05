from torch import nn
import torch as tr
from pool_resources import PoolResources
from pool_resources.resource import TorchResource

from torch import nn
import torch as tr
from pool_resources import PoolResources
from pool_resources.resource import TorchResource

class Model(nn.Module):
    def __init__(self, input_shape, output_shape):
        super().__init__()
        self.fc = nn.Linear(input_shape, output_shape)

    def forward(self, x):
        return self.fc(x)

def forward_fn(item):
    model, data = item
    return model.forward(data)

class TestDummyTorchModel:
    def test_dummy_torch_model(self):
        # batch size, num models, num resources
        B, k, n = 13, 10, 3
        modules = [Model(input_shape=20, output_shape=30) for _ in range(k)]
        data = tr.randn(k, B, 20)

        resources = [TorchResource(f"cpu:{i}") for i in range(n)]
        res_sequential = list(map(forward_fn, zip(modules, data)))
        res_parallel = PoolResources(resources).map(forward_fn, zip(modules, data))

        assert (tr.stack(res_sequential) - tr.stack(res_parallel)).abs().sum() <= 1e-5

