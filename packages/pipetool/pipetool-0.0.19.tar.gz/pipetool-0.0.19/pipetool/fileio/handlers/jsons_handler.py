import json

import numpy as np

from .base import BaseFileHandler
from ..parse import list_from_file

def set_default(obj):
    """Set default json values for non-serializable values.

    It helps convert ``set``, ``range`` and ``np.ndarray`` data types to list.
    It also converts ``np.generic`` (including ``np.int32``, ``np.float32``,
    etc.) into plain numbers of plain python built-in types.
    """
    if isinstance(obj, (set, range)):
        return list(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.generic):
        return obj.item()
    raise TypeError(f'{type(obj)} is unsupported for json dump')


class JsonsHandler(BaseFileHandler):

    def load_from_fileobj(self, file, **kwargs):    
        rs_list = list_from_file(file, **kwargs)
        try:
            rs_list = [json.loads(s) for s in rs_list]
        except:
            pass
        return rs_list

    def dump_to_fileobj(self, objs, file, **kwargs):
        kwargs.setdefault('default', set_default)
        for obj in objs:
            json.dump(obj, file, **kwargs)
            file.write('\n')

    def dump_to_str(self, obj, **kwargs):
        kwargs.setdefault('default', set_default)
        return json.dumps(obj, **kwargs)