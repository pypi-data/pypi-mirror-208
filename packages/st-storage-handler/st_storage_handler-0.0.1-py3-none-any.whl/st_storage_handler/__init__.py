import streamlit.components.v1 as components
import os

import streamlit as st 

_RELEASE = True

# Declare the component
if not _RELEASE:
    _component_func = components.declare_component(
        "st_storage_handler",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_storage_handler", path=build_dir)

def set_item(set_keys:dict,widget_key:str="set_method"):
    """
    Set items in the local storage.

    Args:
        set_keys (dict): A dictionary where each key-value pair will be set in the local storage.
        widget_key (str, optional): Unique key for the widget. Defaults to "set_method".

    Returns:
        ComponentValue: The return value of the component function.
    """
    _component_func(method="set", set_keys=set_keys,key=widget_key)
    

def get_item(key:list,widget_key:str="get_method"):
    """
    Get items from the local storage.

    Args:
        key (list): A list of keys to get from the local storage.
        widget_key (str, optional): Unique key for the widget. Defaults to "get_method".

    Returns:
        ComponentValue: The return value of the component function.
    """
    
    if isinstance(key, list) == False:
        key = [key]
    return _component_func(method="get", get_key=key, key = widget_key)

def remove_item(key:list, widget_key:str="remove_method"):
    """
    Remove items from the local storage.

    Args:
        key (list): A list of keys to remove from the local storage.
        widget_key (str, optional): Unique key for the widget. Defaults to "remove_method".

    Returns:
        ComponentValue: The return value of the component function.
    """
    if isinstance(key, list) == False:
        key = [key]
    _component_func(method="remove", remove_key=key , key = widget_key)
    #st.experimental_rerun()
    return 

def clear(widget_key:str="clear_method"):
    """
    Clear the local storage.

    Args:
        widget_key (str, optional): Unique key for the widget. Defaults to "clear_method".

    Returns:
        ComponentValue: The return value of the component function.
    """
    return _component_func(method="clear", key = widget_key)
