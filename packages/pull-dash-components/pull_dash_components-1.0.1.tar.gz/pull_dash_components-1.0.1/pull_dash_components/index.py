# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class index(Component):
    """An index component.


Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- id (string; default Math.random().toString(36).substring(2, 7)):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional)

- type (string; default 'text')

- value (boolean | number | string | dict | list; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'pull_dash_components'
    _type = 'index'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, type=Component.UNDEFINED, className=Component.UNDEFINED, value=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'type', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'type', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(index, self).__init__(children=children, **args)
