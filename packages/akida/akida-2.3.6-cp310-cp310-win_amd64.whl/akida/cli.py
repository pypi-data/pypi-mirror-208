import argparse
import os
import glob

from .core import devices, __version__
from .deploy import deploy_engine
from .generate.model import deploy_cmake
from .generate.application_generator import generate_files


def list_devices():
    devices_list = devices()
    if len(devices_list) == 0:
        print("No devices detected")
    else:
        print("Available devices:")
        for device in devices_list:
            print(device.desc)


def default_fixture_path():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    fixture_path = current_dir + "/generate/test/engine/fixtures/*.py"
    return glob.glob(fixture_path)


def main():
    parser = argparse.ArgumentParser()
    sp = parser.add_subparsers(dest="action")
    sp.add_parser("devices", help="List available devices")
    sp.add_parser("version", help="Return akida version")
    gen_parser = sp.add_parser("generate",
                               help="Generate application(s) from fixture file(s).")
    gen_parser.add_argument("--fixture-files",
                            help="A list of python fixture files",
                            nargs="+",
                            type=str,
                            required=True)
    gen_parser.add_argument("--modules-paths",
                            help="Path to additional modules required for fixtures",
                            nargs="+",
                            type=str,
                            default=None)
    gen_parser.add_argument("--dest-path",
                            type=str,
                            default=None,
                            required=True,
                            help="The destination path.")
    engine_parser = sp.add_parser("engine", help="Deploy engine sources and applications")
    # Create parent subparser for arguments shared between engine methods
    engine_parent = argparse.ArgumentParser(add_help=False)
    engine_parent.add_argument(
        "--dest-path",
        type=str,
        default=None,
        required=True,
        help="The destination path.")
    engine_action_parser = engine_parser.add_subparsers(
        dest="engine_action",
        help="Action: deploy or generate.")
    engine_action_parser.add_parser(
        "deploy",
        help="Deploy the engine library.",
        parents=[engine_parent])
    args = parser.parse_args()
    if args.action == "devices":
        list_devices()
    elif args.action == "version":
        print(__version__)
    elif args.action == "engine":
        if args.engine_action == "deploy":
            deploy_engine(args.dest_path)
            fixture_files = default_fixture_path()
            dest_path = os.path.join(args.dest_path, "engine/test/akd1000")
            generate_files(fixture_files, dest_path, None)
    elif args.action == "generate":
        deploy_cmake(args.dest_path)
        generate_files(args.fixture_files, args.dest_path, args.modules_paths)
