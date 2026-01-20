# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md


import shutil
import unittest
from pathlib import Path

import pytest
from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.scaffold import Scaffold


class ScaffoldTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / "data"
        self.output_dir = Path(__file__).parent / "output"
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def test_scaffold_default(self):
        """Test default scaffold creation with all standard packages"""
        scaffold = Scaffold(self.output_dir, "scaffold_01", overwrite=True)
        scaffold.create()
        scaffold.save()

        # Check that all default packages were created
        project_path = self.output_dir / "scaffold_01"
        assert project_path.exists()
        assert (project_path / "package.mo").exists()
        assert (project_path / "Loads").exists()
        assert (project_path / "Districts").exists()
        assert (project_path / "Plants").exists()
        assert (project_path / "Substations").exists()
        assert (project_path / "Networks").exists()
        assert (project_path / "Schedules").exists()

        # Check backward compatibility - ModelicaPath objects
        assert hasattr(scaffold, "loads_path")
        assert (Path(self.output_dir) / "scaffold_01" / "Resources" / "Scripts" / "Loads" / "Dymola").exists()

    def test_scaffold_with_ignore_paths(self):
        """Test scaffold creation with some packages ignored"""
        scaffold = Scaffold(self.output_dir, "scaffold_02", overwrite=True)
        scaffold.create(ignore_paths=["Networks", "Plants", "Substations"])
        scaffold.save()

        project_path = self.output_dir / "scaffold_02"

        # Check that ignored packages were NOT created
        assert not (project_path / "Networks").exists()
        assert not (project_path / "Plants").exists()
        assert not (project_path / "Substations").exists()

        # Check that non-ignored packages WERE created
        assert (project_path / "Loads").exists()
        assert (project_path / "Districts").exists()
        assert (project_path / "Schedules").exists()

    def test_scaffold_with_explicit_subpackages(self):
        """Test scaffold creation with explicit subpackage list"""
        scaffold = Scaffold(self.output_dir, "scaffold_03", overwrite=True)
        scaffold.create(subpackages=["Districts", "CustomPackage"])
        scaffold.save()

        project_path = self.output_dir / "scaffold_03"

        # Check that only specified packages were created
        assert (project_path / "Districts").exists()
        assert (project_path / "CustomPackage").exists()

        # Check that default packages were NOT created
        assert not (project_path / "Loads").exists()
        assert not (project_path / "Plants").exists()

    def test_add_subpackage_at_root(self):
        """Test dynamically adding a subpackage at root level"""
        scaffold = Scaffold(self.output_dir, "scaffold_04", overwrite=True)
        scaffold.create(subpackages=["Districts"])

        # Add a custom subpackage
        custom_pkg = scaffold.add_subpackage("CustomModels")
        scaffold.save()

        project_path = self.output_dir / "scaffold_04"
        assert (project_path / "CustomModels").exists()
        assert (project_path / "CustomModels" / "package.mo").exists()
        assert hasattr(scaffold, "custommodels_path")

        # Verify it's a PackageParser instance
        assert isinstance(custom_pkg, PackageParser)

    def test_add_subpackage_nested(self):
        """Test dynamically adding a nested subpackage"""
        scaffold = Scaffold(self.output_dir, "scaffold_05", overwrite=True)
        scaffold.create(subpackages=["Districts"])

        # Add a nested subpackage under Districts
        models_pkg = scaffold.add_subpackage("Models", parent="Districts")
        scaffold.save()

        project_path = self.output_dir / "scaffold_05"
        assert (project_path / "Districts" / "Models").exists()
        assert (project_path / "Districts" / "Models" / "package.mo").exists()
        assert isinstance(models_pkg, PackageParser)

    def test_package_property_access(self):
        """Test accessing packages via the package property"""
        scaffold = Scaffold(self.output_dir, "scaffold_06", overwrite=True)
        scaffold.create(subpackages=["Districts"])

        # Access package via property
        package = scaffold.package
        assert isinstance(package, PackageParser)

        # Access subpackage via attribute notation
        districts = package.districts
        assert isinstance(districts, PackageParser)
        assert districts.package_name == "Districts"

        # Add model to subpackage
        districts.add_model("TestModel", create_subpackage=False)
        scaffold.save()

        # Verify it was added to package.order
        with open(self.output_dir / "scaffold_06" / "Districts" / "package.order") as f:
            assert "TestModel" in f.read()

    def test_loads_ets_subpackage_creation(self):
        """Test that Loads/ETS subpackage is created by default"""
        scaffold = Scaffold(self.output_dir, "scaffold_07", overwrite=True)
        scaffold.create()
        scaffold.save()

        project_path = self.output_dir / "scaffold_07"

        # Check that ETS subpackage was created under Loads
        assert (project_path / "Loads" / "ETS").exists()
        assert (project_path / "Loads" / "ETS" / "package.mo").exists()
        assert hasattr(scaffold, "heat_pump_ets_path")

        # Verify ETS is accessible via scaffold.package.loads.ets
        ets_pkg = scaffold.package.loads.ets
        assert isinstance(ets_pkg, PackageParser)
        assert ets_pkg.package_name == "ETS"

        # Verify within statement
        with open(project_path / "Loads" / "ETS" / "package.mo") as f:
            content = f.read()
            assert "within scaffold_07.Loads;" in content

    def test_loads_ets_can_be_ignored(self):
        """Test that Loads/ETS can be excluded via ignore_paths"""
        scaffold = Scaffold(self.output_dir, "scaffold_07b", overwrite=True)
        scaffold.create(ignore_paths=["Loads/ETS"])
        scaffold.save()

        project_path = self.output_dir / "scaffold_07b"

        # Check that Loads exists but ETS doesn't
        assert (project_path / "Loads").exists()
        assert not (project_path / "Loads" / "ETS").exists()

    def test_package_within_statements(self):
        """Test that within statements are correctly set in nested packages"""
        scaffold = Scaffold(self.output_dir, "scaffold_08", overwrite=True)
        scaffold.create(subpackages=["Districts"])
        scaffold.package.districts.add_model("SubModel", create_subpackage=True)
        scaffold.save()

        # Check within statement in Districts/package.mo
        with open(self.output_dir / "scaffold_08" / "Districts" / "package.mo") as f:
            content = f.read()
            assert "within scaffold_08;" in content

        # Check within statement in Districts/SubModel/package.mo
        with open(self.output_dir / "scaffold_08" / "Districts" / "SubModel" / "package.mo") as f:
            content = f.read()
            assert "within scaffold_08.Districts;" in content

    def test_scaffold_overwrite_protection(self):
        """Test that scaffold protects against overwriting existing projects"""
        scaffold1 = Scaffold(self.output_dir, "scaffold_09", overwrite=True)
        scaffold1.create()
        scaffold1.save()

        # Try to create again without overwrite flag
        with pytest.raises(Exception, match=r"(?i)already exists"):
            Scaffold(self.output_dir, "scaffold_09", overwrite=False)

    # def test_add_building(self):
    #     scaffold = Scaffold(self.output_dir, "scaffold_02", overwrite=True)
    #     load_1 = FakeConnector(None)
    #     self.assertIsInstance(load_1, building_base)
    #     scaffold.loads.append(load_1)
    #     scaffold.create()
    #
    #     r = scaffold.to_modelica()
    #     self.assertTrue(r)
