# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DAOInfo(Component):
    """A DAOInfo component.
DAOInfo is the component on the top left of the second header
It receives the DAO name, the network(s), the address, the creation date,
and the participation statistics and shows them in a grid view.

Keyword arguments:

- id (string; default 'dao-info'):
    The ID used to identify the component in Dash callbacks.

- address (string; optional):
    The address of the organization.

- creation_date (string; optional):
    The creation date of the organization.

- first_activity (string; optional):
    The date where the first activity was recorded.

- name (string; default 'no name given'):
    The organization (DAO) name.

- network (string; optional):
    The network the DAO is deployed on.

- participation_stats (list of dicts; optional):
    The array of participation_stats objects."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dao_analyzer_components'
    _type = 'DAOInfo'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, name=Component.UNDEFINED, network=Component.UNDEFINED, address=Component.UNDEFINED, creation_date=Component.UNDEFINED, first_activity=Component.UNDEFINED, participation_stats=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'address', 'creation_date', 'first_activity', 'name', 'network', 'participation_stats']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'address', 'creation_date', 'first_activity', 'name', 'network', 'participation_stats']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DAOInfo, self).__init__(**args)
