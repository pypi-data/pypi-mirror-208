import json
  
from ..parse import list_from_file
from .base import BaseFileHandler


class TextsHandler(BaseFileHandler):

    def load_from_fileobj(self, file, **kwargs):    
        rs_list = list_from_file(file, **kwargs) 
        return rs_list

    def dump_to_fileobj(self, objs, file, **kwargs): 
        for obj in objs: 
            file.write(obj + '\n',**kwargs)

    def dump_to_str(self, obj, **kwargs): 
        return json.dumps(obj, **kwargs)