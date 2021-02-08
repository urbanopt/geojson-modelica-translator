"""
****************************************************************************************************
:copyright (c) 2019-2021 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

import filecmp
import os
import unittest

from geojson_modelica_translator.modelica.input_parser import InputParser


class InputParserTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_missing_file(self):
        fn = "non-existent-path"
        with self.assertRaises(Exception) as exc:
            InputParser(fn)
        self.assertEqual(f"Modelica file does not exist: {fn}", str(exc.exception))

    def test_roundtrip(self):
        filename = os.path.join(self.data_dir, "test_1.mo")
        new_filename = os.path.join(self.output_dir, "test_1_output_1.mo")
        f = InputParser(filename)
        f.save_as(new_filename)
        # Previous file should be the same as the updated file
        self.assertTrue(filecmp.cmp(filename, new_filename))

    def test_remove_object(self):
        filename = os.path.join(self.data_dir, "test_1.mo")
        new_filename = os.path.join(self.output_dir, "test_1_output_2.mo")
        f1 = InputParser(filename)
        f1.remove_object("ReaderTMY3")
        f1.save_as(new_filename)
        self.assertFalse(filecmp.cmp(filename, new_filename))

        f1.reload()
        f2 = InputParser(new_filename)
        self.assertGreater(len(f1.model["objects"]), len(f2.model["objects"]))
        # verify that it exists in f1 but not in f2
        self.assertGreaterEqual(f1.find_model_object("ReaderTMY3")[0], 0)
        self.assertIsNone(f2.find_model_object("ReaderTMY3")[0])

    def test_gsub_field(self):
        filename = os.path.join(self.data_dir, "test_1.mo")
        new_filename = os.path.join(self.output_dir, "test_1_output_3.mo")
        f1 = InputParser(filename)
        # This example is actually updating an annotation object, not a model, but leave it here for now.
        f1.replace_model_string(
            "Modelica.Blocks.Sources.CombiTimeTable",
            "internalGains",
            "Internals",
            "NotInternals",
        )
        f1.save_as(new_filename)

        f2 = InputParser(new_filename)
        index, model = f2.find_model_object(
            "Modelica.Blocks.Sources.CombiTimeTable internalGains"
        )
        self.assertFalse(filecmp.cmp(filename, new_filename))
        # the 5th index is the rotation... non-ideal look up
        self.assertTrue("NotInternals" in model)

    def test_rename_filename(self):
        filename = os.path.join(self.data_dir, "test_1.mo")
        new_filename = os.path.join(self.output_dir, "test_1_output_4.mo")
        f1 = InputParser(filename)
        # This example is actually updating an annotation object, not a model, but leave it here for now.
        f1.replace_model_string(
            'Modelica.Blocks.Sources.CombiTimeTable',
            'internalGains',
            'modelica://Project/B5a6b99ec37f4de7f94020090/B5a6b99ec37f4de7f94020090_Models/InternalGains_B5a6b99ec37f4de7f94020090Floor.mat',  # noqa
            'modelica://a/new/path.mat'
        )
        f1.save_as(new_filename)

        f2 = InputParser(new_filename)
        index, model = f2.find_model_object(
            "Modelica.Blocks.Sources.CombiTimeTable internalGains"
        )
        self.assertFalse(filecmp.cmp(filename, new_filename))
        # the 5th index is the rotation... non-ideal look up
        self.assertTrue("a/new/path.mat" in model)

    def test_add_model_obj(self):
        filename = os.path.join(self.data_dir, "test_1.mo")
        new_filename = os.path.join(self.output_dir, "test_1_output_5.mo")
        f1 = InputParser(filename)
        data = [
            'annotation (Placement(transformation(extent={{-10,90},{10,110}}), iconTransformation(extent={{-10,90},{10,110}})));'  # noqa
        ]
        f1.add_model_object(
            "Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a", "port_a", data
        )
        f1.save_as(new_filename)

        # verify in the new file that the new model object exists
        f2 = InputParser(new_filename)
        index, model = f2.find_model_object(
            "Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a port_a"
        )
        self.assertFalse(filecmp.cmp(filename, new_filename))
        self.assertGreaterEqual(index, 0)

    def test_gsub_connect(self):
        filename = os.path.join(self.data_dir, "test_1.mo")
        new_filename = os.path.join(self.output_dir, "test_1_output_6.mo")
        f1 = InputParser(filename)
        f1.add_connect(
            "port_a",
            "thermalZoneTwoElements.intGainsConv",
            "annotation (Line(points={{0,100},{96,100},{96,20},{92,20}}, color={191,0,0}))",
        )
        f1.save_as(new_filename)

        # verify in the new file that the new model object exists
        f2 = InputParser(new_filename)
        self.assertFalse(filecmp.cmp(filename, new_filename))
        index, c = f2.find_connect("port_a", "thermalZoneTwoElements.intGainsConv")
        self.assertGreaterEqual(index, 0)

    def test_rename_connection(self):
        filename = os.path.join(self.data_dir, "test_1.mo")
        new_filename = os.path.join(self.output_dir, "test_1_output_7.mo")
        f1 = InputParser(filename)
        # connect(weaDat.weaBus, HDifTil[3].weaBus)
        f1.replace_connect_string(
            "eqAirTemp.TEqAir", "prescribedTemperature.T", "NothingOfImportance", None
        )
        f1.replace_connect_string("weaDat.weaBus", None, "weaBus", None, True)
        f1.save_as(new_filename)

        f2 = InputParser(new_filename)
        self.assertFalse(filecmp.cmp(filename, new_filename))
        index, c = f2.find_connect('weaBus', 'weaBus')
        # there should exist the new connection
        self.assertGreaterEqual(index, 0)

        # the old one should not exist
        index, c = f2.find_connect('weaDat.weaBus', 'weaBus')
        self.assertIsNone(index)

    def test_remove_connection(self):
        filename = os.path.join(self.data_dir, "test_1.mo")
        new_filename = os.path.join(self.output_dir, "test_1_output_8.mo")
        f1 = InputParser(filename)
        f1.remove_connect_string('weaDat.weaBus', 'weaBus')
        f1.save_as(new_filename)

        f2 = InputParser(new_filename)
        self.assertFalse(filecmp.cmp(filename, new_filename))
        index, c = f2.find_connect('weaDat.weaBus', 'weaBus')
        # the connection should no longer exist
        self.assertIsNone(index)

    def test_modelica_parameter(self):
        filename = os.path.join(self.data_dir, "test_1.mo")
        new_filename = os.path.join(self.output_dir, "test_1_output_9.mo")
        f1 = InputParser(filename)
        f1.add_parameter('Real', 'aVarNam', 0.8, "A description where aVarName is 0.8")
        f1.add_parameter('String', 'aVarNamStr', 'A-string-value', "A description string A-string-value")
        f1.save_as(new_filename)

        # just read the file and ensure that the string exists
        test_strs = [
            'parameter String aVarNamStr="A-string-value" "A description string A-string-value";',
            'parameter Real aVarNam=0.8 "A description where aVarName is 0.8";'
        ]
        with open(new_filename) as f:
            file_data = f.read()
            for test_str in test_strs:
                self.assertIn(test_str, file_data)
