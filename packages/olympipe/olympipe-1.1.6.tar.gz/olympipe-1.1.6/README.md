# Olympipe

![coverage](https://gitlab.com/gabraken/olympipe/badges/master/coverage.svg?job=tests)![status](https://gitlab.com/gabraken/olympipe/badges/master/pipeline.svg)

![Olympipe](https://gitlab.com/gabraken/olympipe/-/raw/master/Olympipe.png)


This project will make pipelines 
easy to use to improve parallel computing using the basic multiprocessing module. This module uses type checking to ensure your data process validity from the start.

## Basic usage

Each pipeline starts from an interator as a source of packets (a list, tuple, or any complex iterator). This pipeline will then be extended by adding basic `.task(<function>)`. The pipeline process join the main process when using the `.wait_for_results()` or `.wait_for_completion()` functions.

```python

from olympipe import Pipeline

def times_2(x: int) -> int:
    return x * 2

p = Pipeline(range(10))

p1 = p.task(times_2) # Multiply each packet by 2
# or 
p1 = p.task(lambda x: x * 2) # using a lambda function

res = p1.wait_for_result()

print(res) # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

```


## Filtering

You can choose which packets to `.filter(<keep_function>)` by passing them a function returning True or False when applied to this packet.

```python

from olympipe import Pipeline

p = Pipeline(range(20))
p1 = p.filter(lambda x: x % 2 == 0) # Keep pair numbers
p2 = p1.batch(2) # Group in arrays of 2 elements

res = p2.wait_for_result()

print(res) # [[0, 2], [4, 6], [8, 10], [12, 14], [16, 18]]

```

## In line formalization

You can chain declarations to have a more readable pipeline.

```python

from olympipe import Pipeline

[res] = Pipeline(range(20)).filter(lambda x: x % 2 == 0).batch(2).wait_for_results()

print(res) # [[0, 2], [4, 6], [8, 10], [12, 14], [16, 18]]

```

## Debugging

Interpolate `.debug()` function anywhere in the pipe to print packets as they arrive in the pipe.

```python
from olympipe import Pipeline

p = Pipeline(range(20))
p1 = p.filter(lambda x: x % 2 == 0).debug() # Keep pair numbers
p2 = p1.batch(2).debug() # Group in arrays of 2 elements

p2.wait_for_completion()
```

## Pipeline forking

For the time being, you have to adapt the code a little bit if you wish to get several outputs for a same pipeline. [This section might be updated soon]

```python
from olympipe import Pipeline

p1 = Pipeline(range(10))
p2 = p1.filter(lambda x: x % 2 == 0)
p3 = p1.filter(lambda x: x % 2 == 1)

res2, res3 = Pipeline.wait_for_all_results([p2, p3])

print(res3) # [1, 3, 5, 7, 9]
print(res2) # [0, 2, 4, 6, 8]

```

## Real time processing (for sound, video...)

Use the `.temporal_batch(<seconds_float>)` pipe to aggregate packets received at this point each <seconds_float> seconds.

```python
import time
from olympipe import Pipeline

def delay(x: int) -> int:
    time.sleep(0.1)
    return x

p = Pipeline(range(20)).task(delay) # Wait 0.1 s for each queue element
p1 = p.filter(lambda x: x % 2 == 0) # Keep pair numbers
p2 = p1.temporal_batch(1.0) # Group in arrays of 2 elements

[res] = p2.wait_for_results()

print(res) # [[0, 2, 4, 6, 8], [10, 12, 14, 16, 18], []]
```

## Using classes in a pipeline

You can add a stateful class instance to a pipeline. The method used will be typecheked as well to ensure data coherence. You just have to use the `.class_task(<Class>, <Class.method>, ...)` method where Class.method is the actual method you will use to process each packet.

```python
item_count  = 5

class StockPile:
    def __init__(self, mul:int):
        self.mul = mul
        self.last = 0
        
    def pile(self, num: int) -> int:
        out = self.last
        self.last = num * self.mul
        return out
        

p1 = Pipeline(range(item_count))

p2 = p1.class_task(StockPile, StockPile.pile, [3])

[res] = p2.wait_for_results()

print(res) # [0, 0, 3, 6, 9]

```


This project is still an early version, feedback is very helpful.