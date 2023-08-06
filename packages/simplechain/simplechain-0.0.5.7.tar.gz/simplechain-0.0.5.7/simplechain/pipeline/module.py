import functools
from inspect import signature

modules = {}


def register_module(name, func):
    if name in modules:
        raise ValueError(f"Module {name} already exists")
    modules[name] = func


def get(self, name):
    return self.modules[name]


def module(name: str):
    def _module(func):
        try:  # register module
            register_module(name, func)
        except ValueError:
            print(f"Module {name} already exists.")
            return

        sig = signature(func)
        print("Module registered: ", name)
        #print("Module function: ", func.__name__)
        #print("Module number of input arguments: ", len(sig.parameters))
        #print("Module input arguments: ", sig.parameters)
        #print(sig.return_annotation)

        @functools.wraps(func)
        def _module_wrapper(*args, **kwargs):
            #print("pre-process")
            #for arg in args:
            #   print(arg)
            #for key, value in kwargs.items():
            #   print(f"{key}: {value}")
            res = func(*args, **kwargs)
            #print("post-process")
            return res

        return _module_wrapper

    return _module
