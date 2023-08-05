"""Test custom schema validation that cannot be verified by the Pydantic validation"""

import pytest
from pydantic import Field
from tomlkit import parse

from cppython_core.schema import (
    CPPythonGlobalConfiguration,
    CPPythonLocalConfiguration,
    CPPythonModel,
    PEP621Configuration,
    PyProject,
)


class TestSchema:
    """Test validation"""

    class Model(CPPythonModel):
        """Testing Model"""

        aliased_variable: bool = Field(default=False, alias="aliased-variable", description="Alias test")

    def test_model_construction(self) -> None:
        """Verifies that the base model type has the expected construction behaviors"""

        model = self.Model(**{"aliased_variable": True})
        assert model.aliased_variable is False

        model = self.Model(**{"aliased-variable": True})
        assert model.aliased_variable is True

    def test_model_construction_from_data(self) -> None:
        """Verifies that the base model type has the expected construction behaviors"""

        data = """
        aliased_variable = false\n
        aliased-variable = true
        """

        result = self.Model.parse_obj(parse(data).value)
        assert result.aliased_variable is True

    def test_cppython_local(self) -> None:
        """Ensures that the CPPython local config data can be defaulted"""
        CPPythonLocalConfiguration()

    def test_cppython_global(self) -> None:
        """Ensures that the CPPython global config data can be defaulted"""
        CPPythonGlobalConfiguration()

    def test_cppython_table(self) -> None:
        """Ensures that the nesting yaml table behavior can be read properly"""

        data = """
        [project]\n
        name = "test"\n
        version = "1.0.0"\n
        description = "A test document"\n

        [tool.cppython]\n
        """

        document = parse(data).value
        pyproject = PyProject(**document)
        assert pyproject.tool is not None
        assert pyproject.tool.cppython is not None

    def test_pep621_version(self) -> None:
        """Tests the dynamic version validation"""

        with pytest.raises(ValueError):
            PEP621Configuration(name="empty-test")

        with pytest.raises(ValueError):
            PEP621Configuration(name="both-test", version="1.0.0", dynamic=["version"])
