# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import glob
import sys
import time
import traceback
import types
from pathlib import Path
from typing import Union
from ruamel.yaml.parser import ParserError as YamlParserError

from azure.ml.component._util._yaml_utils import YAML
from azure.ml.component._util._loggerfactory import _LoggerFactory
from azure.ml.component.dsl._utils import is_dsl_component
from azureml.exceptions import UserErrorException

_logger = _LoggerFactory.get_logger("az-ml")

compile_enter_count = 0
is_compiling_message = 'is_compiling'


def _generate_yaml(spec_file_path: str, target_file_path: str):
    try:
        with open(spec_file_path, 'r', encoding='utf-8') as f:
            spec_dict = YAML.safe_load(f)
        del spec_dict['code']
        YAML._dump_yaml_file(spec_dict, target_file_path)
    except YamlParserError as e:
        raise UserErrorException('Failed to load spec file {0}, Please check the schema format of yaml file.'
                                 '\nException: \n{1}'.format(spec_file_path, e))
    except Exception as e:
        raise UserErrorException('Failed to load spec file {0}.\nException: \n{1}'.format(spec_file_path, e))


def _compile_component_from_path(source: str = None, name: str = None):
    from runpy import run_path

    global is_compiling_message

    if not source.endswith('.py'):
        raise UserErrorException('only support compile python file')

    start_time = time.time()
    file_list = glob.glob(source, recursive=True)
    if len(file_list) == 0:
        _logger.info(f'Does not find python file, please confirm whether the given source path is correct.\n'
                     f'Source: {source}')
        return
    compile_component_count = 0
    compile_file_count = 0
    _logger.info('Start compiling components.')
    for file in file_list:
        try:
            file_path = Path(file).resolve()
            _logger.debug(f'Start compile {file_path}')
            with open(file_path, encoding='utf-8') as f:
                contents = f.read()
                if r'command_component' not in contents:
                    _logger.debug(f'Skip compile component from {file_path}, '
                                  f'because the file content does not contain "command_component"')
                    continue
            module_dict = run_path(str(file_path))
            compile_file_count += 1
            for variable_name, variable in module_dict.items():
                if not is_dsl_component(variable):
                    continue
                component_func = variable
                if name is None or name == component_func._executor.component_name:
                    if Path(component_func._executor.compile_file_path).exists():
                        _logger.warning(f'Skip compile component: {component_func._executor.component_name!r} '
                                        f'due to target yaml already exsits.\n'
                                        f'Source: {file_path}, Target: {component_func._executor.compile_file_path}')
                    else:
                        _generate_yaml(component_func._executor.component_yaml_file,
                                       component_func._executor.compile_file_path)
                        compile_component_count += 1
                        _logger.info(f'Successfully compile component '
                                     f'{component_func._executor.compile_file_path} from {file_path}.')
        except UserErrorException as e:
            if e.message == is_compiling_message:
                error_list = traceback.format_exception(*sys.exc_info(), limit=None, chain=True)
                error_message = f'file {file_path}'
                file_path_str = str(file_path)
                for error_item in error_list:
                    if file_path_str in error_item:
                        error_message = error_item.strip().replace('\n', '').replace('  ', ' ')
                        break
                _logger.warning(f'Recursive compile is not allowed. '
                                f'Please delete the compile invocation in {error_message}.')
            else:
                _logger.error(f'Skip compile {file_path}, because load file error, {e}')
        except Exception as e:
            _logger.error(f'Skip compile {file_path}, because load file error, {e}')
        finally:
            _logger.debug(f'End compile {file_path}')
    end_time = time.time()
    _logger.info(f'Successfully compiled {compile_component_count} components from {compile_file_count} source files '
                 f'in {round(end_time - start_time, 2)} seconds.')
    _logger.info(f'Total {len(file_list)} files were scanned from {source}.')


def compile(source: Union[str, Path, types.FunctionType] = None, name: str = None):
    """
    compile the @command_component decorated function code as yaml
    :param source: the source code path or the @command_component decorated function
    :type: Union[str, Path, FunctionType]
    :param name: the component name that need to as yaml, If it is None, will compile all component code as yaml
    :type: str
    """
    global compile_enter_count, is_compiling_message

    try:
        compile_enter_count += 1
        if compile_enter_count > 1:
            raise UserErrorException(is_compiling_message)
        if isinstance(source, (str, Path)):
            _compile_component_from_path(str(source), name)
        elif is_dsl_component(source):
            _compile_component_from_path(str(source._executor._entry_file.resolve()), source._executor.component_name)
        else:
            raise UserErrorException(f'Not support {source}')
    except Exception as e:
        raise e
    finally:
        compile_enter_count -= 1
