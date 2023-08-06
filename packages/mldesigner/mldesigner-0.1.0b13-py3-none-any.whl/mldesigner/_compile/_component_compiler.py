# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from ._base_compiler import BaseCompiler


class CommandComponentCompiler(BaseCompiler):
    """Basic component compiler to compile command components to yaml components"""

    COMMAND_SCHEMA = "https://azuremlschemas.azureedge.net/development/commandComponent.schema.json"

    def _update_compile_content(self):
        """Generate component dict and refine"""
        component_dict = self._component._to_dict()
        # code will always be the default value "." in compiled yaml
        self._snapshot = self._get_component_snapshot(component_dict.pop("code", None))
        self._refine_component_dict(component_dict)
        self._component_content = component_dict

    def _refine_component_dict(self, component_dict):
        """Update component dict for fields like schema, inputs and code"""
        # Add schema for command component
        component_dict[BaseCompiler.SCHEMA_KEY] = self.COMMAND_SCHEMA
        # transform dumped component input value to corresponding type
        self._update_component_inputs(component_dict)
        # pop name and version for environment
        self._refine_component_environment(component_dict)

    @classmethod
    def _refine_component_environment(cls, component_dict: dict):
        """Pop name and version for environment"""
        if "environment" in component_dict and isinstance(component_dict["environment"], dict):
            env = component_dict["environment"]
            env.pop("name", None)
            env.pop("version", None)
            if "conda_file" in env and isinstance(env["conda_file"], dict):
                env["conda_file"].pop("name", None)
                env["conda_file"].pop("version", None)
