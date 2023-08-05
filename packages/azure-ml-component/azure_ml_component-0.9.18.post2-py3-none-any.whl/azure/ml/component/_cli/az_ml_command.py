# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import sys
import logging
import argparse

from azure.ml.component._debug._step_run_debugger import OnlineStepRunDebugger
from azure.ml.component.dsl._compile import compile as amlcompile
from azure.ml.component.dsl._graph_2_code._code_generator import PipelinePackageGenerator, PipelinePackageCompare
from azure.ml.component._util._loggerfactory import _LoggerFactory, track, _PUBLIC_API


_logger = _LoggerFactory.get_logger("az-ml")


def _set_workspace_argument_for_subparsers(subparser):
    subparser.add_argument(
        '--subscription_id', '-s', type=str,
        help="Subscription id, required when pass run id."
    )
    subparser.add_argument(
        '--resource_group', '-r', type=str,
        help="Resource group name, required when pass run id."
    )
    subparser.add_argument(
        '--workspace_name', '-w', type=str,
        help="Workspace name, required when pass run id."
    )

    subparser.add_argument(
        '--debug', action="store_true",
        help="Increase logging verbosity to show all debug logs"
    )


def _set_common_argument_for_subparsers(subparser):
    _set_workspace_argument_for_subparsers(subparser)
    subparser.add_argument(
        '--path', '-p', type=str,
        help="Path to export the pipeline to. If not specified, default will be set."
    )
    subparser.add_argument(
        '--include-components', type=str,
        help="""Included components to download snapshot.
        * to export all components;
        ',' separated string which contains a subset of components
        """
    )


def _entry(argv):
    """
    CLI tool to export UI graph to Component SDK code, compare codes of two pipelines
    or debug component using common-runtime.
    """
    parser = argparse.ArgumentParser(
        prog="az-ml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A CLI tool to export UI graph to Component SDK code, "
                    "compare codes of two pipelines or debug component using common-runtime."
    )

    subparsers = parser.add_subparsers()
    subparsers.required = True

    # az-ml export
    add_export_parser(subparsers)
    # az-ml compare
    add_compare_parser(subparsers)
    # az-ml run debug
    add_run_parser(subparsers)
    # az-ml compile
    add_compile_parser(subparsers)

    args = parser.parse_args(argv)

    if args.debug:
        for log_handler in _logger.handlers:
            if isinstance(log_handler, logging.StreamHandler):
                log_handler.setLevel(logging.DEBUG)

    if args.classname == PipelinePackageGenerator:
        _generate_package(
            url=args.url,
            subscription_id=args.subscription_id,
            resource_group=args.resource_group,
            workspace_name=args.workspace_name,
            run_id=args.pipeline_run,
            include_components=args.include_components,
            target_dir=args.path,
        )

    elif args.classname == PipelinePackageCompare:
        _compare_package(
            run_item1=args.pipeline1,
            run_item2=args.pipeline2,
            subscription_id=args.subscription_id,
            resource_group=args.resource_group,
            workspace_name=args.workspace_name,
            include_components=args.include_components,
            target_dir=args.path,
        )
    elif args.classname == OnlineStepRunDebugger:
        _setup_debug(args)
    elif args.classname == amlcompile:
        _aml_compile(args.source, args.name)


@track(activity_name="AZ_ML_Export", activity_type=_PUBLIC_API)
def _generate_package(
    url: str = None,
    subscription_id=None, resource_group=None, workspace_name=None, run_id=None,
    include_components=None, target_dir=None
):
    from azure.ml.component.dsl._graph_2_code._code_generator import _generate_package

    _generate_package(url=url, subscription_id=subscription_id, resource_group=resource_group,
                      workspace_name=workspace_name, run_id=run_id, include_components=include_components,
                      target_dir=target_dir)


@track(activity_name="AZ_ML_Compare", activity_type=_PUBLIC_API)
def _compare_package(
        run_item1: str = None, run_item2: str = None,
        subscription_id=None, resource_group=None, workspace_name=None,
        include_components: str = None, target_dir=None
):
    from azure.ml.component.dsl._graph_2_code._code_generator import _compare_package

    _compare_package(
        run_item1=run_item1,
        run_item2=run_item2,
        subscription_id=subscription_id,
        resource_group=resource_group,
        workspace_name=workspace_name,
        include_components=include_components,
        target_dir=target_dir,
    )


@track(activity_name="AZ_ML_Run_Debug", activity_type=_PUBLIC_API)
def _setup_debug(debug_args):
    from azure.ml.component._debug._step_run_debugger import _setup_debug

    common_runtime_debug_args = {"compute": "local", "runtime": "common", **vars(debug_args)}
    _setup_debug(common_runtime_debug_args)


@track(activity_name="AZ_ML_Compile", activity_type=_PUBLIC_API)
def _aml_compile(source, name):
    amlcompile(
        source=source,
        name=name
    )


def add_export_parser(subparsers):
    export_parser = subparsers.add_parser(
        'export',
        description='A CLI tool to export UI graph to Component SDK code.',
        help='az-ml export'
    )
    _set_common_argument_for_subparsers(export_parser)
    export_parser.add_argument(
        '--pipeline-run', type=str,
        help="ID of the Pipeline Run to export (guid)."
    )
    export_parser.add_argument(
        '--url', type=str,
        help="URL of the Pipeline run/draft/endpoint to export."
    )
    export_parser.set_defaults(classname=PipelinePackageGenerator)


def add_compare_parser(subparsers):
    compare_parser = subparsers.add_parser(
        'compare',
        description='A CLI tool to export UI graph to Component SDK code and compare codes of two pipelines.',
        help='az-ml compare'
    )
    _set_common_argument_for_subparsers(compare_parser)
    compare_parser.add_argument(
        'pipeline1', type=str,
        help="First URL of the Pipeline Run to export, and URL recommended to be enclosed in double quotes in cmd."
    )
    compare_parser.add_argument(
        'pipeline2', type=str,
        help="Second URL of the Pipeline Run to export, and URL recommended to be enclosed in double quotes in cmd"
    )
    compare_parser.set_defaults(classname=PipelinePackageCompare)


def add_run_parser(subparsers):
    run_parser = subparsers.add_parser(
        "run", description='A CLI tool to local debug component using common-runtime.',
        help='az-ml run').add_subparsers()
    local_debug_parser = run_parser.add_parser(
        "debug",
        description='A CLI tool to local debug using common runtime.',
        help='az-ml run debug'
    )
    _set_workspace_argument_for_subparsers(local_debug_parser)
    local_debug_parser.add_argument(
        "--run-id", type=str,
        help="The run id of step run to be debugged."
    )
    local_debug_parser.set_defaults(classname=OnlineStepRunDebugger)


def add_compile_parser(subparsers):
    compile_parser = subparsers.add_parser(
        'compile',
        description='A CLI tool to compile the @command_component decorated function code as yaml.',
        help='az-ml compile'
    )
    compile_parser.add_argument(
        '--source', type=str, required=True,
        help="The file path that @dsl.command_component decorated function code"
    )
    compile_parser.add_argument(
        '--name', type=str,
        help="The component name that needs to be compiled as yaml."
    )
    compile_parser.add_argument(
        '--debug', action="store_true",
        help="Increase logging verbosity to show all debug logs."
    )
    compile_parser.set_defaults(classname=amlcompile)


def az_ml_cli():
    """Use as a CLI entry function to use ComponentProject."""
    _entry(sys.argv[1:])
