# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
This module enable user to run a dsl component by command.

Example command:

.. code-block:: bash

    python -m azure.ml.component.dsl.executor --file {your_file_path}
    [--name {your_component_name}] --params --{your_param_key} {your_param_value} ...

--file, -f: The dsl component file path.

--name: The dsl component name. Optional if there is only one dsl component in the file.

--params: A mark to split parameters, dsl component function parameters goes after this.

"""
import argparse
import logging
import sys

from azure.ml.component._util._utils import environment_variable_overwrite, DSL_COMPONENT_EXECUTION
from azure.ml.component.dsl._component import ComponentExecutor


class _ExecutorParser(argparse.ArgumentParser):

    def __init__(self):
        super().__init__()
        self.add_argument("-f", "--file", required=True, help="The executed file name.")
        self.add_argument(
            "--name",
            help="The dsl component name. Optional if there is only one dsl component in the file.")
        self.add_argument(
            '--params', action='store_true',
            help="A mark to split parameters, dsl component function parameters goes after this.")

    def parse_known_args(self, args=None, namespace=None):
        if args is None:
            # args default to the system args
            args = sys.argv[1:]
        else:
            # make sure that args are mutable
            args = list(args)
        parsed_args, execution_parameters = super().parse_known_args(args, namespace)
        if ComponentExecutor.EXECUTION_PARAMETERS_KEY not in args:
            logging.warning(
                "The '--params' mark to split parameters not found, "
                "execute dsl component function with no parameters.")
            return parsed_args, []
        # Recalculate execution params by split args from '--params'
        execution_index = args.index(ComponentExecutor.EXECUTION_PARAMETERS_KEY)
        execution_parameters = args[execution_index:]
        # Recalculate parsed args as there may be duplicate keys in execution parameters.
        parsed_args, _ = super().parse_known_args(args[:execution_index + 1], namespace)
        if execution_parameters:
            # Pop the execution parameters key
            execution_parameters.pop(0)
        return parsed_args, execution_parameters


if __name__ == '__main__':
    parser = _ExecutorParser()
    executor_args, func_args = parser.parse_known_args()

    with environment_variable_overwrite(DSL_COMPONENT_EXECUTION, 'True'):
        ComponentExecutor.collect_component_from_file(
            executor_args.file, component_name=executor_args.name,
            from_executor=True, force_reload=True).execute(func_args)
