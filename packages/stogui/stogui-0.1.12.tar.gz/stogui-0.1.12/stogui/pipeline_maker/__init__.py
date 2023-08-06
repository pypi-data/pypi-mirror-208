from distutils.util import strtobool
import os
from typing import Callable, Iterable
import streamlit.components.v1 as components
import streamlit as st

DEBUG = strtobool(os.getenv('STOGUI_DEBUG', 'false'))


if DEBUG:
    _component_func = components.declare_component(
        'pipeline_maker', url='http://localhost:3001',
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, 'frontend/build')
    _component_func = components.declare_component('pipeline_maker', path=build_dir)


def pipeline_maker(
    *, items: Iterable = None, steps: Iterable = None, serializer: Callable = None,
):
    def identity(x):
        return x

    items = items or []
    steps = steps or []
    serializer = serializer or identity

    serialized_items = [serializer(i) for i in items]
    serialized_steps = [serializer(s) for s in steps]

    serialized_pipeline = _component_func(
        items=serialized_items, steps=serialized_steps
    )
    pipeline = (
        [
            next(iter(i for i in items if serializer(i) == s))
            for s in serialized_pipeline
        ]
        if serialized_pipeline
        else []
    )
    return pipeline


if __name__ == '__main__':

    def foo(a: int = 1, b: int = 2, c=3):
        """This is foo. It computes something"""
        return (a * b) + c

    def bar(x, greeting='hello'):
        """bar greets its input"""
        return f'{greeting} {x}'

    def confuser(a: int, x: float = 3.14):
        return (a ** 2) * x

    def serializer(item):
        return item.__name__

    items = [foo, bar, confuser]

    steps = [
        bar,
        foo,
    ]

    current_steps = pipeline_maker(items=items, steps=steps, serializer=serializer)

    print(current_steps)
