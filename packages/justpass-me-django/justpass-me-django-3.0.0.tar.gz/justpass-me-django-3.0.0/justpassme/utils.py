import importlib

def import_mod(path,*args,**kwargs):
    parts = path.split(".")
    p = ".".join(parts[:-1])
    return getattr(importlib.import_module(p),parts[-1])