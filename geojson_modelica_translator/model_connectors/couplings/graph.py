"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the
distribution.

Neither the name of the copyright holder nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
****************************************************************************************************
"""
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
