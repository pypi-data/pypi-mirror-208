# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from ._base_compiler import BaseCompiler


class InternalComponentCompiler(BaseCompiler):
    """A compiler to compile v1.5 components"""

    def _update_compile_content(self):
        """Generate component dict and refine"""
        component_dict = self._component._to_dict()
        # code will always be the default value "." in compiled yaml
        self._snapshot = self._get_component_snapshot(component_dict.pop("code", None))
        self._component_content = component_dict
