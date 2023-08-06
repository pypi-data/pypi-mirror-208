#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import ctypes
import os
import sys

try:
  import torch
  torch_version = torch.version.__version__
except:
  torch_version = ''

assert sys.version_info.major == 3 and sys.version_info.minor >= 8, "Only Python (>= 3.8) is supported by AutoRT"
assert torch_version.startswith('2.0.'), f"Expected Torch version (2.0.x) is not installed for AutoRT, please try: {os.path.basename(sys.executable)} -m pip install torch==2.0.0"

from .lib import antares_backend

def backend_name():
  return 'c-hlsl_win64'

def device():
  return 'privateuseone'

def print(*ts):
  data = ' '.join([f'<<< data={t.cpu().view(-1)}, shape={t.shape}, dtype={t.dtype} >>>' if isinstance(t, torch.Tensor) else f'{t}' for t in ts])
  sys.stdout.write(f'{data}\n')

def ones(*args, **kwargs):
  return torch.ones(*args, device=device(), **kwargs)

def full(*args, **kwargs):
  return torch.full(*args, device=device(), **kwargs)

def empty(*args, **kwargs):
  return torch.empty(*args, device=device(), **kwargs)

def from_npy(path):
  import numpy as np
  return torch.tensor(np.load(path), device=device())

def to_npy(x, path):
  import numpy as np
  np.save(path, x.cpu().numpy())


class OpClass:
  aops = torch.ops.antares_ops
  op_dict = {}

  def __getattr__(self, name: str):
    addr = id(name)
    if addr not in OpClass.op_dict:
      c_ptr = ctypes.create_string_buffer(name.encode('utf-8'), len(name))
      def handler(*args, extra=[]):
        result = OpClass.aops.custom(ctypes.addressof(c_ptr), args, extra)
        return result
      handler.c_ptr = c_ptr
      OpClass.op_dict[addr] = handler
    return OpClass.op_dict[addr]

os.environ['LIB_ROOT'] = os.path.dirname(os.path.abspath(__file__))
ops = OpClass()

int16 = torch.int16
int32 = torch.int32
int64 = torch.int64
float32 = torch.float32
float64 = torch.float64

''' py

  # Example:
  import autort as art

  x = art.full([2, 4], 1.2)
  art.print(x)
'''