"""Downloads the trip locally to the specified folder

Provided trip name expected to be a section of Tator multi-type media files.
Media names are expected to be in isoformat.

"""

import argparse
import logging
import os
import sys
import yaml

import progressbar
import tator

from dr_import.gps_utilities import MultiviewsGPSInfo

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--host", type=str, default="https://cloud.tator.io", help="Tator URL")
    parser.add_argument("--token", type=str, required=True, help="Tator user specific API token")
    parser.add_argument("--project-config", type=str, required=True, help=".yaml file of trip project")
    parser.add_argument("--trip-name", type=str, required=True, help="Trip name to download")
    parser.add_argument("--output-folder", type=str, required=True, help="Folder to download the files to")
    parser.add_argument("--camera-id", type=str, help="Camera ID to download videos of")
    args = parser.parse_args()
    return args

def script_main() -> None:
    """ Script's main function
    """

    args = parse_args()

    # Verify the provided output folder exists
    if not os.path.isdir(args.output_folder):
        raise ValueError(f"Output directory does not exist: {args.output_folder}")

    # Init Tator API connection and project information
    tator_api = tator.get_api(host=args.host, token=args.token)

    with open(args.project_config, "r") as file_handle:
        config = yaml.safe_load(file_handle)

    # Find section matching provided trip name
    sections = tator_api.get_section_list(project=config["project"], name=args.trip_name)

    if len(sections) < 1:
        raise ValueError(f"Could not find any sections with the provided trip name: {args.trip_name}")

    elif len(sections) > 1:
        raise ValueError(f"Multiple sections with the provided trip name: {args.trip_name}")

    section = sections[0]

    # Gather up the media and sort by camera
    multi_medias = tator_api.get_media_list(
        project=config["project"],
        type=config["multi_type_id"],
        section=section.id)

    camera_medias = {}
    for multi in multi_medias:
        for single_id in multi.media_files.ids:
            single = tator_api.get_media(id=single_id)
            camera_id = single.attributes.get("Camera", "unknown")
            if camera_id not in camera_medias:
                camera_medias[camera_id] = []

            camera_medias[camera_id].append(single)

    logger.info(f"Camera IDs: {camera_medias.keys()}")

    # Download per camera
    for camera_id in camera_medias:

        if args.camera_id is not None:
            if camera_id != args.camera_id:
                logger.info(f"Skipping {camera_id}")
                continue

        logger.info(f"Downloading {len(camera_medias[camera_id])} video files for camera {camera_id}")
        bar = progressbar.ProgressBar()
        for media in bar(camera_medias[camera_id]):
            file_date = f"{media.attributes.get('Date')}T{media.attributes.get('Time').split('.')[0]}"
            out_path = os.path.join(args.output_folder, f"{file_date}_camera{camera_id}.mp4")
            for _ in tator.util.download_media(api=tator_api, media=media, out_path=out_path):
                continue

if __name__ == "__main__":
    script_main()