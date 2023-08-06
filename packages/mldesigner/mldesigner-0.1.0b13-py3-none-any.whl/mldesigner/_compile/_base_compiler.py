# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
from pathlib import Path

from mldesigner._azure_ai_ml import Component
from mldesigner._compile._compile_collector import CompileCollector
from mldesigner._constants import InternalNodeType, IoConstants, ComponentSource
from mldesigner._exceptions import MldesignerCompileError


class BaseCompiler:
    """Base compiler to compile SDK-defined components to yaml components"""

    SCHEMA_KEY = "$schema"

    def __init__(self, component: Component, collector: CompileCollector):
        self._validate_component(component)
        self._component = component
        self._collector = collector
        self._output = collector._output
        # component content should be component dict which is generated in _update_compile_content function
        self._component_content = None
        # snapshot are all the dependency files needed for a component
        self._snapshot = None

    def compile(self):
        self._update_compile_content()

        if self._component_content is None:
            raise MldesignerCompileError("Component content is empty, nothing to compile.")
        # make sure yaml file keys are ordered
        self._component_content = self._get_reordered_dict(self._component_content)
        self._collector._compile_with_data(
            component=self._component, data=self._component_content, snapshot_list=self._snapshot
        )

    @classmethod
    def _validate_component(cls, component):
        result = component._customized_validate()
        if not result.passed:
            raise MldesignerCompileError(message=result.error_messages)

    @classmethod
    def _update_component_inputs(cls, component_dict):
        """Transform dumped component input value to corresponding type"""
        keys = ["default", "min", "max"]
        inputs = component_dict["inputs"]

        # better way to handle this issue is to change ParameterSchema to use dumpable integer/float/string
        # however this change has a large impact in current code logic, may investigate this as another work item
        for _, input_dict in inputs.items():
            for key in keys:
                if key in input_dict and input_dict["type"] in IoConstants.PARAM_PARSERS:
                    param_parser = IoConstants.PARAM_PARSERS[input_dict["type"]]
                    correct_value = param_parser(input_dict[key])
                    input_dict[key] = correct_value

    def _update_compile_content(self):
        """Update component content and snapshot which will be compiled, implemented by sub-compilers"""
        raise NotImplementedError()

    def _get_reordered_dict(self, original_dict):
        """Make sure dict keys are in order when getting dumped"""
        KEY_ORDER = [
            BaseCompiler.SCHEMA_KEY,
            "name",
            "display_name",
            "description",
            "type",
            "version",
            "is_deterministic",
            "tags",
            "component",
            "inputs",
            "outputs",
            "code",
            "environment",
            "command",
            "jobs",
        ]

        original_dict = copy.deepcopy(original_dict)
        new_dict = {}
        for key in KEY_ORDER:
            if key in original_dict:
                new_dict[key] = original_dict.pop(key)

        # for pipeline component yaml, need to sort job node dict and node's component dict
        if "jobs" in new_dict and isinstance(new_dict["jobs"], dict):
            for node_name, node_dict in new_dict["jobs"].items():
                if "component" in node_dict and isinstance(node_dict["component"], dict):
                    node_dict["component"] = self._get_reordered_dict(node_dict["component"])
                new_dict["jobs"][node_name] = self._get_reordered_dict(new_dict["jobs"][node_name])

        # in case there are missed keys in original dict
        new_dict.update(original_dict)
        return new_dict

    def _get_component_snapshot(self, code):
        """Generate a list that contains all dependencies of a component"""
        # when compiling yaml component, code could be None and use its source file directory as code
        source_path = Path(self._component._source_path)
        code = code or "."
        code = source_path.parent / code

        snapshot_list = list(
            file.resolve().as_posix()
            for file in Path(code).glob("*")
            if not (
                (file.is_dir() and file.name == "__pycache__")
                or (file.is_file() and file.suffix in (".pyc", ".additional_includes"))
            )
        )

        # add additional includes into snapshot list
        snapshot_list += self._get_additional_includes()

        # remove original yaml file if the input is yaml as we need to update code to "."
        # and output new yaml with original file name
        if self._component._source == ComponentSource.YAML_COMPONENT:
            original_yaml = Path(self._component._source_path).resolve().as_posix()
            if original_yaml in snapshot_list:
                snapshot_list.remove(original_yaml)

        return snapshot_list

    def _get_additional_includes(self):
        """Get a list of additional includes for the component"""
        res = []
        # currently only support v1.5 component since additional includes is not supported yet in v2
        if self._component.type in InternalNodeType.all_values():
            additional_includes_obj = self._component._InternalComponent__additional_includes
            if additional_includes_obj and additional_includes_obj.with_includes:
                code_path = additional_includes_obj.code_path
                res = [Path(code_path / file).resolve().as_posix() for file in additional_includes_obj.includes]
        return res
