""" Utilize an input .yaml file to clone a MREM trip

Expected .yaml format:
host: str
project: int

"""
import argparse
import yaml

from dr_import import clone_mrem_section
import tator

def main(
        token: str,
        src_info: dict,
        dest_info: dict,
        src_trip_name: str,
        dest_trip_name: str) -> None:
    """
    """

    print("\n")
    print("----------------------------------------------------------------")
    print(f"Clone Tator Trip: STARTED")
    print("- Cloning videos, multis, and GPS states")
    print("- Creating new trip_summary image")
    print("----------------------------------------------------------------")

    tator_api = tator.get_api(host=src_info["host"], token=token)
    src_project = tator_api.get_project(id=src_info["project"])
    dest_project = tator_api.get_project(id=dest_info["project"])
    print(f"Cloning {src_trip_name} from {src_project.name} to {dest_project.name} | {dest_trip_name}")

    clone_mrem_section.main(
        in_host=src_info["host"],
        in_token=token,
        in_src_project=src_info["project"],
        in_dest_project=dest_info["project"],
        in_src_section_name=src_trip_name,
        in_dest_section_name=dest_trip_name,
        in_copy_annotations=False)

    print("----------------------------------------------------------------")
    print(f"Clone Tator Trip: FINISHED")
    print("----------------------------------------------------------------")
    print("\n")

def parse_args() -> None:
    """ Process script's arguments
    """

    parser=argparse.ArgumentParser()
    parser.add_argument("--token", type=str, required=True, help="Tator API user token")
    parser.add_argument("--src-config", type=str, required=True, help=".yaml file of source project")
    parser.add_argument("--dest-config", type=str, required=True, help=".yaml file of destination project")
    parser.add_argument("--trip-name", type=str, required=True, help="Name of trip to clone in source project")
    parser.add_argument("--dest-trip-name", type=str, required=False, help="Name of cloned trip in destination project. If omitted, the same trip name is used.")
    args = parser.parse_args()
    return args

def script_main() -> None:
    """ Script's entry point
    """

    args = parse_args()

    with open(args.src_config, "r") as file_handle:
        src_info = yaml.safe_load(file_handle)

    with open(args.dest_config, "r") as file_handle:
        dest_info = yaml.safe_load(file_handle)

    if args.dest_trip_name is not None:
        dest_trip_name = args.dest_trip_name
    else:
        dest_trip_name = args.trip_name

    main(
        token=args.token,
        src_info=src_info,
        dest_info=dest_info,
        src_trip_name=args.trip_name,
        dest_trip_name=dest_trip_name)

if __name__ == "__main__":
    script_main()