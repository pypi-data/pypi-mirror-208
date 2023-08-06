from distutils.util import strtobool
import os
from typing import Callable, Union, List
import streamlit.components.v1 as components

DEBUG = strtobool(os.getenv('STOGUI_DEBUG', 'false'))


if DEBUG:
    _component_func = components.declare_component(
        'test_results_table', url='http://localhost:3001',
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, 'frontend/build')
    _component_func = components.declare_component('test_results_table', path=build_dir)


def test_results_table(
    *,
    sessions: Union[List[dict], Callable[[], List[dict]]] = None,
    query=None,
    is_multiselect=None,
):
    if callable(sessions):
        sessions = sessions()
    selected_sessions = _component_func(
        sessions=sessions, query=query, is_multiselect=is_multiselect
    )
    if not selected_sessions:
        return
    return selected_sessions if is_multiselect else selected_sessions[0]
