import sys
import imp
from pymetabiosis import import_module


class PyMetabiosisHook(object):
    """An import hook to first try importing in pypy and if that fails, try
    with the embedded CPython via `pymetabiosis.import_module`.
    """
    def __init__(self):
        self.module = None

    def _is_root_package_in_pypy(self, fullname):
        """Checks if the first package in the module given is in pypy or not.

        For example, if IPython.core is imported, then IPython is the "root"
        package.
        """
        root = fullname.split('.')[0]
        result = True
        try:
            info = imp.find_module(root)
        except ImportError:
            result = False
        return result

    def find_module(self, fullname, path=None):
        module = None
        if not self._is_root_package_in_pypy(fullname):
            module = import_module(fullname)
        self.module = module
        return self if module is not None else None

    def load_module(self, name):
        module = self.module
        sys.modules[name] = module
        return module


def install():
    """Install the import_hook and return a function that removes the
    hook when called (with no arguments).

    Not removing the hook causes problems and segfaults when exiting the
    interpreter.
    """
    import_hook = PyMetabiosisHook()
    sys.meta_path.append(import_hook)
    return lambda: sys.meta_path.remove(import_hook)


def auto():
    """Automatically install the import hook and uninstall the hook
    via atexit.
    """
    from pymetabiosis.import_hook import install
    import atexit
    atexit.register(install())
