# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from collections import defaultdict


class CouplingGraph:
    """Manages coupling relationships"""

    def __init__(self, couplings):
        if len(couplings) == 0:
            raise Exception('At least one coupling must be provided')
        self._couplings = couplings

        self._models_by_id = {}
        for coupling in self._couplings:
            a, b = coupling._model_a, coupling._model_b
            self._models_by_id[a.id] = a
            self._models_by_id[b.id] = b

        self._couplings_by_model_id = defaultdict(list)
        for coupling in self._couplings:
            a, b = coupling._model_a, coupling._model_b
            self._couplings_by_model_id[a.id].append(coupling)
            self._couplings_by_model_id[b.id].append(coupling)

        # _grouped_couplings_by_model_id stores couplings a model is involved with
        # grouped by the type of the _other_ model involved, e.g.
        # {
        #   ...
        #   'my_network_123': {
        #     'ets_couplings': [...],
        #     'system_couplings': [...]
        #   },
        #   ...
        # }
        self._grouped_couplings_by_model_id = {}
        for model_id, couplings in self._couplings_by_model_id.items():
            grouped_couplings = defaultdict(list)
            for coupling in couplings:
                other_model = coupling.get_other_model(self._models_by_id[model_id])
                coupling_type = f'{other_model.simple_gmt_type}_couplings'
                grouped_couplings[coupling_type].append(coupling)

            self._grouped_couplings_by_model_id[model_id] = grouped_couplings

    @property
    def couplings(self):
        return [coupling for coupling in self._couplings]

    @property
    def models(self):
        return [model for _, model in self._models_by_id.items()]

    def couplings_by_type(self, model_id):
        """Returns the model's associated couplings keyed by the types of the
        _other_ model involved

        For example if given model is ets, and its coupled to a load and network,
        the result would be:
        {
           'load_couplings': [<load coupling>],
           'network_couplings': [<network coupling>],
        }

        :param model_id: str
        :return: dict
        """
        model = self._models_by_id[model_id]
        grouped_couplings = self._grouped_couplings_by_model_id[model.id]
        result = {}
        for type_, couplings in grouped_couplings.items():
            result[type_] = [coupling.to_dict() for coupling in couplings]
        return result

    def directional_index(self, model_a_id, model_b_id):
        """Returns the index of model_b within model_a's adjacency list for
        model_b's type.

        For example, if our graph looks like this, and model_b is an ETS
        ```
        {
            ...
            model_a: {
                ets_couplings: [
                    { ets: model_b, ... }, { ets: model_c, ...}
                ],
                ...
            },
            ...
        }
        ```
        Then this method would return 0, because it's at index 0

        :param model_a_id: str, id of model_a
        :param model_b_id: str, id of model_b
        :return: int
        """
        if model_a_id not in self._models_by_id:
            raise Exception('Model A id was not found')
        if model_b_id not in self._models_by_id:
            raise Exception('Model B id was not found')

        model_a, model_b = self._models_by_id[model_a_id], self._models_by_id[model_b_id]
        grouped_couplings = self._grouped_couplings_by_model_id[model_a.id]
        coupling_type = f'{model_b.simple_gmt_type}_couplings'
        try:
            couplings = grouped_couplings[coupling_type]
            other_models = [coupling.get_other_model(model_a) for coupling in couplings]
            other_model_ids = [m.id for m in other_models]
            return other_model_ids.index(model_b.id)
        except KeyError:
            raise Exception(f'model_a has no coupling with model_b\'s type ({model_b.simple_gmt_type})')
        except ValueError:
            raise Exception('model_a has no coupling with model_b')

    def get_coupled_load(self, ets_id):
        """Returns the load coupled to the provided ets

        :param ets_id: str
        :return: dict
        """
        if ets_id not in self._grouped_couplings_by_model_id:
            raise Exception(f'No ETS with id {ets_id}')
        try:
            load_couplings = self._grouped_couplings_by_model_id[ets_id]['load_couplings']
            return load_couplings[0].to_dict()['load']
        except (KeyError, IndexError):
            raise Exception('ETS is not coupled to a load')

    def get_coupling(self, coupling_id):
        for coupling in self._couplings:
            if coupling.id == coupling_id:
                return coupling
        raise Exception(f'No coupling found with id "{coupling_id}"')
