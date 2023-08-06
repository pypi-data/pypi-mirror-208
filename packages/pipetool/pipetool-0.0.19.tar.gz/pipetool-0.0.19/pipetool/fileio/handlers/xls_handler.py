import json

import pandas as pd
from .base import BaseFileHandler

class XlsHandler(BaseFileHandler):
    str_like = False
    
    def load_from_fileobj(self, file, **kwargs):
        df = pd.read_excel(file,**kwargs)
        return df.to_dict('records')
    
    def dump_to_fileobj(self, obj, file, **kwargs): 
        df = pd.DataFrame(data = obj)
        df.to_excel(file,index=0,**kwargs)

    def dump_to_str(self, obj, **kwargs): 
        return json.dumps(obj, **kwargs)
