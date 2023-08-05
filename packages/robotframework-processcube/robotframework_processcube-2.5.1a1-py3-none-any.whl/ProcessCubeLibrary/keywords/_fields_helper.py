from dataclasses import fields
from threading import local

def filter_kwargs_for_dataclass(dataclassType, kwargs: dict) -> dict:
    local_kwargs = kwargs.copy()
    
    my_fields = fields(dataclassType)
    field_names = [field.name for field in my_fields]
    
    for key in kwargs:
        if key not in field_names:
            del local_kwargs[key] 


    return local_kwargs
