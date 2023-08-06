from distutils.util import strtobool
import os
from typing import Callable, Union, List
import streamlit.components.v1 as components

DEBUG = strtobool(os.getenv('STOGUI_DEBUG', 'false'))


if DEBUG:
    _component_func = components.declare_component(
        'dpp_table', url='http://localhost:3001',
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, 'frontend/build')
    _component_func = components.declare_component('dpp_table', path=build_dir)


def dpp_table(
    *,
    data: Union[List[dict], Callable[[], List[dict]]] = None,
    query=None,
    is_multiselect=None,
):
    if callable(data):
        data = data()
    selected_dpp = _component_func(
        data=data, query=query, is_multiselect=is_multiselect
    )
    if selected_dpp:
        return selected_dpp if is_multiselect else selected_dpp[0]
