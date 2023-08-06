# IVA TPU Python API
## Main entities
### TPUDevice
TPUDevice is a device handle

### TPUProgram
TPUProgram contains TPU instructions and weigths data

### TPUProgramInfo
Object can be used to configure inference.
```
config = TPUProgramInfo()
config.max_tasks_count = 4 # configures depth of tasks queue in driver
config.disable_static_checker = true # disables static checker for program
program = TPUProgram("program.tpu", config)
```

### TPUInference
TPUInference contains input/output data

## Example

```python
import asyncio
import numpy as np
from iva_tpu import TPUDevice, TPUProgram, TPUInference

from iva_applications.resnet50 import image_to_tensor
from iva_applications.imagenet import tpu_tensor_to_classes
from PIL import Image

image = Image.open('ILSVRC2012_val_00000045.JPEG')
tensor = image_to_tensor(image)

device = TPUDevice()
program = TPUProgram("resnet50.tpu")  # default TPUProgramInfo is totally fine
device.load_program(program)
inference = TPUInference(program)
inference.load([tensor])
status_future = device._load_inference(inference)  # device returns future for inference status
event_loop = asyncio.get_event_loop()
status = event_loop.run_until_complete(status_future)
assert status.is_success  # check that there is no errors during inference
output = inference.get()  # get results
tpu_tensor_to_classes(output[0], top=1)
```

## TPU Dictionary interface
```
...
program = TPUProgram("resnet50.tpu")
inference = TPUInference(program)
inference.load({"Placeholder:0": tensor})
...
assert status.is_success
output = inference.get(as_dist=True)
tpu_tensor_to_classes(output["logits:0"], top=1)
```

## TPU Blocking interface
```
status = device.load_inference_sync(inference) #would block until completion
```

## TPU Raw buffer examples
```
import asyncio
from iva_tpu import TPUDevice, TPUProgram, TPUInference, ProcessingMode
program = TPUProgram("omega_program_dnn_quant_3.0.0.tpu")
device = TPUDevice()
device.load_program(program)
inference = TPUInference(program)

with open("f.bin", "rb") as f:
    buf=f.read()

inference.load([buf], mode=ProcessingMode.RAW)
asyncio.get_event_loop().run_until_complete(device.load_inference(inference))
outputs = inference.get(mode=ProcessingMode.RAW)

for i in range(3):
  o = outputs[i]
  with open(f"o{i}.bin", "wb") as f:
    f.write(o)
```

## TPU Single inference statistics examples
```
result = device.load_inference_sync(inference)
result.timings # contains statistics about inference
result.timings["queue_timings"] # contains array of timings for 3 queues (QUEUE_TRANSFER_TO, QUEUE_EXECUTOR, QUEUE_TRANSFER_FROM)
result.timings["queue_timings"][%d] # contains tuple of 2 elements: idle time and actual work time
result.timings["queue_timings"][%d][%d] # contains tuple of 3 values: last, average, maximum through all inferences for the device object
result.timings["execution_timing"][%d] # same as before but with execution on tpu timings
```

## TPU Global statistics examples
```
device = TPUDevice()
device.stats # returns object with global statistics about the current device
device.stats["mem"] # current usage of memory in the device
```
