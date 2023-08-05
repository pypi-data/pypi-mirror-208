#!/usr/bin/env python3

"""daqpp.

This module defines a wrapper for the DAQ++ package, allowing to
build a data acquisition system from python taking advantage of
DAQ++.
One can also interface with existing libraries that implement
different models for Module and RunManager objects. For that daqpp
provides load_lib that will return a Hook object from with you can
call the Module and RunManager factories. daqpp uses dl for loading
the shared libraries. It also 'borrows' the RTLD_* constants from
the dl module.
Note: The libraries should provide Object factories, that is,
functions declared with extern 'C' that are able to create your
objects from the arguments passed. They should be something like:
extern 'C' void create_module(const char *type) {
   if ( type=='type1') {
      new ModuleType1(...)
   }
   else if ( type='...') {
       ...
   }
}
The idea behind is that you can afterwards access the module with
the DAQmanager.find_module() or DAQmanager.find_runmanager() functions.
This module also provides a helper function that does exactly that:
- create_module
- create_runmanager
"""

import sys
import ctypes
import re
from pathlib import Path

from daqpp.DAQpp import *


class HookList(dict):
    """HookList.

    Maintains a list of all the existing Hooks. This is implemented as
    a singleton. The basic idea behind is that we do not want the
    libraries to be unloaded until the very end, so that all their
    routines are available.
    """

    def __new__(cls, *args, **kwargs):
        """That makes the class a singleton."""
        if '_inst' not in vars(cls):
            cls._inst = dict.__new__(cls, *args, **kwargs)

        return cls._inst

    def __init__(self):
        """Initialization."""
        super(HookList, self).__init__()

    def __setitem__(self, key, value):
        """Item setter.

        Args:
        ----
            key (str): the item key
            value : The item value

        """
        if value.handler:
            super(HookList, self).__setitem__(key, value)
        else:
            print('Invalid handler. Hook not stored')

    def __del__(self):
        """Delete."""
        print('Deleting the list of Hooks')
        self.clear()


def load_lib(lib):
    """Load a library.

    Load a shared library into the system. It will return a
    reference to a Hook object that contains the library handler
    that will allow to access to the library symbols.

    Args:
    ----
    lib: the path of the shared library

    Returns
    -------
    A Hook object that will allow to access the library symbols

    """
    class Hook(object):
        """Hook.

        This class defines what I call a hook. It is in fact a holder
        of a shared library handler as given by the dl module.

        To access the symbols or routines exported by the library, just
        call

            hook.func_name(...)

        where func_name is the name of a routine in the library. One
        can also use the call operator. This follows the dl module
        convention.
        """

        def __init__(self, lib):
            self.handler = None
            try:
                self.lib = Path(lib).resolve(strict=True)
                self.handler = ctypes.cdll.LoadLibrary(self.lib)
            except SystemError as e:
                print("Could not load library", self.lib)
                print(e)
                sys.exit(1)
            except Exception as e:
                print("Could not load module", self.lib)
                print(e)

        def __getattr__(self, name):
            if name not in self.__dict__ and self.handler:
                try:
                    function = getattr(self.handler, name)

                    def func(str, *args):
                        return function(str, *args)

                    self.__dict__[name] = func
                    return func
                except AttributeError:
                    raise AttributeError('Symbol %s is not in %s' % (name, self.lib))

            else:
                return super(Hook, self).__getattr__(name)

        def __call__(self, name, str, *args):
            if self.handler:
                ff = getattr(self.handler, name)
                return ff(str, *args)
            else:
                raise AttributeError('Invalid handler')

        def __del__(self):
            print('...deleting Hook(%s)' % self.lib)
            del self.handler

    return HookList().setdefault(lib, Hook(lib))


def create_module(name, func_name, libpath):
    """Create a module from a given library.

    Args:
    ----
    name: The DAQid of the new module
    func_name: the name of the factory function that actually creates the module
    libpath: the path of the library where dl will search for func_name

    Returns
    -------
    An instance of the module.

    """
    if not Path(libpath).exists():
        print("Library ", libpath, " doesnot exist")
        return

    hook = load_lib(libpath)
    func = getattr(hook, func_name)

    print("Trying to create module", name)
    func(name.encode())
    return find_module(name)


def create_runmanager(name, func_name, libpath):
    """Create a RunManager from a given library.

    Args:
    ----
    name: The DAQid of the new RunManager
    func_name: the name of the factory function that actually creates the RunManager
    libpath: the path of the library where dl will search for func_name

    Returns
    -------
    an instance of the RunModule.

    """
    hook = load_lib(libpath)
    func = getattr(hook, func_name)
    func(name.encode())
    return find_runmanager(name)


_spc = re.compile('\|-<(?P<str>.*)>-\|', re.MULTILINE | re.DOTALL)


def isSpecialParam(s):
    """Check if it is a specil parameter.

    Parameters whose type cannot be easily figured out are sent and
    received as strings. When receiving, they are coded in a very
    'naive' way. This method tells you if this is one of those
    'special' parameter by returning the decoded string, and None if
    the type was properly gotten.

    Args:
    ----
    s: the parameter

    Returns
    -------
    the string representation of the parameter value.

    """
    try:
        r = _spc.match(s)
        if r:
            return r.group('str')
        else:
            return None
    except TypeError:  # this is not a string
        return None


class FileIODescriptor(object):
    """A class that defines a data stream."""

    def __init__(self, id, format):
        """Initialization.

        Args:
        ----
            id (DAQid): The identifier
            format (str): The data format

        """
        self.id = id
        self.format = format
        self.oid = None
# ------------------------------------------------------------------
