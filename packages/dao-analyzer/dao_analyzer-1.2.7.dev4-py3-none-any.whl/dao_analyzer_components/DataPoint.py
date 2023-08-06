# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DataPoint(Component):
    """A DataPoint component.
Used from each DataPoint on the right side of the second header

Keyword arguments:

- id (string; optional):
    The css id to use.

- evolution (number; optional):
    The absolute difference between this month and the last.

- evolution_rel (number; optional):
    The relative difference between this month and the last.

- number (number | string; default NaN):
    The big number to show.

- title (string; required):
    The title of the datapoint."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dao_analyzer_components'
    _type = 'DataPoint'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, title=Component.REQUIRED, number=Component.UNDEFINED, evolution=Component.UNDEFINED, evolution_rel=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'evolution', 'evolution_rel', 'number', 'title']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'evolution', 'evolution_rel', 'number', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['title']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(DataPoint, self).__init__(**args)
