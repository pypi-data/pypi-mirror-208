# Copyright (c) OpenMMLab. All rights reserved.
import sys
import time
import warnings
from getpass import getuser
from socket import gethostname
from types import ModuleType
from typing import Optional 
import numpy as np
import random,os
import pipetool


def get_host_info() -> str:
    """Get hostname and username.

    Return empty string if exception raised, e.g. ``getpass.getuser()`` will
    lead to error in docker container
    """
    host = ''
    try:
        host = f'{getuser()}@{gethostname()}'
    except Exception as e:
        warnings.warn(f'Host or user not found: {str(e)}')
    finally:
        return host


def get_time_str() -> str:
    return time.strftime('%Y%m%d_%H%M%S', time.localtime())


def obj_from_dict(info: dict,
                  parent: Optional[ModuleType] = None,
                  default_args: Optional[dict] = None):
    """Initialize an object from dict.

    The dict must contain the key "type", which indicates the object type, it
    can be either a string or type, such as "list" or ``list``. Remaining
    fields are treated as the arguments for constructing the object.

    Args:
        info (dict): Object types and arguments.
        parent (:class:`module`): Module which may containing expected object
            classes.
        default_args (dict, optional): Default arguments for initializing the
            object.

    Returns:
        any type: Object built from the dict.
    """
    assert isinstance(info, dict) and 'type' in info
    assert isinstance(default_args, dict) or default_args is None
    args = info.copy()
    obj_type = args.pop('type')
    if pipetool.is_str(obj_type):
        if parent is not None:
            obj_type = getattr(parent, obj_type)
        else:
            obj_type = sys.modules[obj_type]
    elif not isinstance(obj_type, type):
        raise TypeError('type must be a str or valid type, but '
                        f'got {type(obj_type)}')
    if default_args is not None:
        for name, value in default_args.items():
            args.setdefault(name, value)
    return obj_type(**args)


def seed_everything(seed=None):
    max_seed_value = np.iinfo(np.uint32).max
    min_seed_value = np.iinfo(np.uint32).min

    if (seed is None) or not (min_seed_value <= seed <= max_seed_value):
        random.randint(np.iinfo(np.uint32).min, np.iinfo(np.uint32).max)
    print(f"Global seed set to {seed}")
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch 
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except:
        pass
    
    try:
        import paddle 
        paddle.seed(seed)
    except:
        pass
    
    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
    except:
        pass
    
    return seed

def seg_generator(iterables, seg_len, seg_backoff=0):
    '''
    滑窗实现
    '''
    if seg_len <= 0:
        yield iterables, 0
    else:
        #  # 确保iterables列表中每一项的条目数相同
        #  assert sum([len(x)
        #              for x in iterables]) == len(iterables[0]) * len(iterables)
        assert iterables[0] is not None
        s0 = 0
        while s0 < len(iterables[0]):
            s1 = s0 + seg_len
            segs = [x[s0:s1] if x else None for x in iterables]
            yield segs, s0
            s0 += seg_len - seg_backoff