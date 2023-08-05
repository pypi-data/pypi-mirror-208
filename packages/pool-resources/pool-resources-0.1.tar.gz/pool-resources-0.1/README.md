# Pool Resources

## Description
Library to generalize `multiprocessing.Pool(n: int)` to handle generic resources.

First class support for torch devices as a generic resource.

## Example for n torch GPUs and k torch Modules

```
from pool_resources import PoolResources
from pool_resources.resources import TorchResource

class Model(nn.Module):
    def __init__(self, input_shape, output_shape):
        super().__init__()
        self.fc = nn.Linear(input_shape, output_shape)

    def forward(self, x):
        return self.fc(x)

def forward_fn(item):
    model, data = item
    return model.forward(data)

modules = [Model(input_shape=20, output_shape=30) for _ in range(k)]
data = tr.randn(k, B, 20)
seq = zip(modules, data)

resources = [TorchResource(f"cuda:{i}") for i in range(n)]

res_sequential = list(map(forward_fn, seq))
res_parallel = PoolResources(resources).map(forward_fn, seq)


```