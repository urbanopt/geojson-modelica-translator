"""
****************************************************************************************************
:copyright (c) 2019-2020 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

from .context import geojson_modelica_translator  # noqa - Do not remove this line

import os
import unittest

from geojson_modelica_translator.utils import ModelicaPath


class ModelicaPathTest(unittest.TestCase):
    def test_properties(self):
        mp = ModelicaPath('Loads', root_dir=None)
        self.assertEqual(mp.files_dir, 'Loads')
        self.assertEqual(mp.resources_dir, os.path.join('Resources', 'Data', 'Loads'))

    def test_scaffold(self):
        root_dir = os.path.abspath(os.path.join('tests', 'output', 'test_02'))
        ModelicaPath('RandomContainer', root_dir)
        self.assertTrue(os.path.exists(os.path.join(root_dir, 'RandomContainer')))
        self.assertTrue(os.path.exists(os.path.join(root_dir, 'Resources', 'Data', 'RandomContainer')))


if __name__ == '__main__':
    unittest.main()
