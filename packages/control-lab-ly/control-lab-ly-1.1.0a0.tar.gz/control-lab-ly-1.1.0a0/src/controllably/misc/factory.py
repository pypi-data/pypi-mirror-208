# %% -*- coding: utf-8 -*-
"""
This module holds the factory functions in Control.lab.ly.

Classes:
    DottableDict (dict)
    ModuleDirectory (dataclass)

Functions:
    get_class
    get_details
    get_machine_addresses
    get_plans
    include_this_module
    load_components
    register
    unregister

Other constants and variables:
    HOME_PACKAGE (tuple)
    modules (ModuleDirectory)
"""
# Standard library imports
from dataclasses import dataclass, field
import importlib
import inspect
import numpy as np
import pprint
import sys
from typing import Callable, Optional

# Third party imports
import yaml # pip install pyyaml

# Local application imports
from . import helper
print(f"Import: OK <{__name__}>")

HOME_PACKAGE = ('controllably','lab')
"""Names and aliases of base package"""

class DottableDict(dict):
    """DottableDict provides a way to use dot notation on dictionaries"""
    
    def __init__(self, *args, **kwargs):
        """Instantiate the class"""
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self
        
    def allow_dotting(self, state:bool = True):
        """
        Turn on or off the dot notation feature

        Args:
            state (bool, optional): whether to turn on dot notation feature. Defaults to True.
        """
        if state:
            self.__dict__ = self
        else:
            self.__dict__ = dict()

@dataclass
class ModuleDirectory:
    """
    ModuleDirectory represents the entire collection of imported modules into `controllably`
    
    ### Properties
    - `at`: dictionary structure of imported Classes
    
    ### Methods
    - `get_class`: get Class object from collection
    - `get_parent`: get parent dictionary of target Class
    """
    
    _modules: DottableDict = field(default_factory=DottableDict, init=False)
    
    def __repr__(self) -> str:
        return pprint.pformat(self._modules)
    
    @property
    def at(self):
        return self._modules
    
    def get_class(self, dot_notation:str) -> Callable:
        """
        Get Class object from collection

        Args:
            dot_notation (str): dot notation of target Class

        Returns:
            Callable: Class object
        """
        name = dot_notation.split('.')[-1]
        temp = self.get_parent(dot_notation=dot_notation)
        return temp.get(name)
    
    def get_parent(self, dot_notation:str) -> DottableDict:
        """
        Get parent dictionary of target Class

        Args:
            dot_notation (str): dot notation of target Class

        Returns:
            DottableDict: parent dictionary of target Class
        """
        keys = dot_notation.split('.')
        keys = keys[:-1]
        temp = self._modules
        for key in keys:
            if key in HOME_PACKAGE:
                continue
            temp = temp[key]
        return temp
        
modules = ModuleDirectory()
"""Holds all `controllably` and user-registered classes and functions"""

def get_class(dot_notation:str) -> Callable:
    """
    Retrieve the relevant class from the sub-package

    Args:
        dot_notation (str): dot notation of Class object

    Returns:
        Callable: target Class
    """
    print('\n')
    top_package = __name__.split('.')[0]
    import_path = f'{top_package}.{dot_notation}'
    package = importlib.import_module('.'.join(import_path.split('.')[:-1]))
    _class = modules.get_class(dot_notation=dot_notation)
    return _class

def get_details(configs:dict, addresses:Optional[dict] = None) -> dict:
    """
    Decode dictionary of configuration details to get np.ndarrays and tuples

    Args:
        configs (dict): dictionary of configuration details
        addresses (Optional[dict], optional): dictionary of registered addresses. Defaults to None.

    Returns:
        dict: dictionary of configuration details
    """
    addresses = {} if addresses is None else addresses
    for name, details in configs.items():
        settings = details.get('settings', {})
        
        for key,value in settings.items():
            if key == 'component_config':
                value = get_details(value, addresses=addresses)
            if type(value) == str:
                if key in ['cam_index', 'port'] and value.startswith('__'):
                    settings[key] = addresses.get(key, {}).get(settings[key], value)
            if type(value) == dict:
                if "tuple" in value:
                    settings[key] = tuple(value['tuple'])
                elif "array" in value:
                    settings[key] = np.array(value['array'])

        configs[name] = details
    return configs

def get_machine_addresses(registry:dict) -> dict:
    """
    Get the appropriate addresses for current machine

    Args:
        registry (str): dictionary of yaml file with com port addresses and camera ids

    Returns:
        dict: dictionary of com port addresses and camera ids for current machine
    """
    node_id = helper.get_node()
    addresses = registry.get('machine_id',{}).get(node_id,{})
    if len(addresses) == 0:
        print("\nAppend machine id and camera ids/port addresses to registry file")
        print(yaml.dump(registry))
        raise Exception(f"Machine not yet registered. (Current machine id: {node_id})")
    return addresses

def get_plans(config_file:str, registry_file:Optional[str] = None, package:Optional[str] = None) -> dict:
    """
    Read configuration file (yaml) and get details

    Args:
        config_file (str): filename of configuration file
        registry_file (Optional[str], optional): filename of registry file. Defaults to None.
        package (Optional[str], optional): name of package to look in. Defaults to None.

    Returns:
        dict: dictionary of configuration parameters
    """
    configs = helper.read_yaml(config_file, package)
    registry = helper.read_yaml(registry_file, package)
    addresses = get_machine_addresses(registry=registry)
    configs = get_details(configs, addresses=addresses)
    return configs

def include_this_module(
    where: Optional[str] = None, 
    module_name: Optional[str] = None, 
    get_local_only: bool = True
):
    """
    Include the module py file that this function is called from

    Args:
        where (Optional[str], optional): location within structure to include module. Defaults to None.
        module_name (Optional[str], optional): dot notation name of module. Defaults to None.
        get_local_only (bool, optional): whether to only include objects defined in caller py file. Defaults to True.
    """
    if module_name is None:
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        module_name = mod.__name__
    
    objs = inspect.getmembers(sys.modules[module_name])
    __where__ = [obj for name,obj in objs if name == "__where__"]
    where = f"{__where__[0]}." if (len(__where__) and where is None) else where
    classes = [(nm,obj) for nm,obj in objs if inspect.isclass(obj)]
    functions = [(nm,obj) for nm,obj in objs if inspect.isfunction(obj)]
    objs = classes + functions
    if get_local_only:
        objs = [obj for obj in objs if obj[1].__module__ == module_name]
    
    for name,obj in objs:
        if name == inspect.stack()[0][3]:
            continue
        mod = obj.__module__ if where is None else where
        register(obj, '.'.join(mod.split('.')[:-1]))
    return

def load_components(config:dict) -> dict:
    """
    Load components of compound tools

    Args:
        config (dict): dictionary of configuration parameters

    Returns:
        dict: dictionary of component tools
    """
    components = {}
    for name, details in config.items():
        _module = details.get('module')
        if _module is None:
            continue
        dot_notation = [_module, details.get('class', '')]
        _class = get_class('.'.join(dot_notation))
        settings = details.get('settings', {})
        components[name] = _class(**settings)
    return components

def register(new_object:Callable, where:str):
    """
    Register the object into target location within structure

    Args:
        new_object (Callable): new Callable object (Class or function) to be registered
        where (str): location within structure to register the object in
    """
    keys = where.split('.')
    temp = modules._modules
    for key in keys:
        if key in HOME_PACKAGE:
            continue
        if key not in temp:
            temp[key] = DottableDict()
        temp = temp[key]
    name = new_object.__name__
    if name in temp:
        overwrite = input(f"An object with the same name ({name}) already exists, Overwrite? [y/n]")
        if overwrite.lower()[0] == 'n':
            print(f"Skipping {name}...")
            return
    temp[new_object.__name__] = new_object
    return

def unregister(dot_notation:str):
    """
    Unregister an object from structure, using its dot notation reference

    Args:
        dot_notation (str): dot notation reference to target object
    """
    keys = dot_notation.split('.')
    keys, name = keys[:-1], keys[-1]
    temp = modules._modules
    for key in keys:
        if key in HOME_PACKAGE:
            continue
        temp = temp[key]
    temp.pop(name)
    
    # Clean up empty dictionaries
    def remove_empty_dicts(d):
        """
        Purge empty dictionaries from nested dictionary

        Args:
            d (dict): dictionary to be purged
        """
        for k, v in list(d.items()):
            if isinstance(v, dict):
                remove_empty_dicts(v)
            if not v:
                del d[k]
    remove_empty_dicts(modules._modules)
    return
