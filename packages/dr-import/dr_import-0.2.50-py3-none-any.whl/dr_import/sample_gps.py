"""Tool to sample existing GPS states from a trip

This tool is used to reduce the GPS states from a multiview trip using the provided sample interval.

Notes:
Existing GPS will be deleted and new GPS states will be created at the sample interval.
New GPS states will be printed out for each interval with datecodes matching the intervals.
User will have to provide an input stating y/N if they want to proceed with the GPS replacement.
No interpolation is performed.

Algorithm:
1. Grab all the media from the provided section
2. Get all the states associated with the media list
3. Line up the states by time
4. Create sample bins based on the first media start time. Each bin is the width of the provided sample interval.
5. For each bin, use the GPS with the highest satellite count
6. If a bin does not have GPS, look in the next sample window and use the first non-0 satelite GPS
   from there. If that bin does not have GPS, look in the previous sample window and use
   the last non-0 satellite GPS. It is possible that a bin will not have GPS.
7. Existing GPS will be deleted
8. New GPS states created using the selected GPS. The datecode matches the start of the sample interval.

"""

import argparse
import inspect
import logging
import sys
import yaml

import tator

from dr_import import gps_utilities

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """ Parse script's arguments
    """

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--host", type=str, default="https://cloud.tator.io")
    parser.add_argument("--token", type=str, required=True)
    parser.add_argument("--project-config", type=str, required=True, help=".yaml file of trip project")
    parser.add_argument("--trip-name", type=str, required=True, help="Name of trip in project")
    parser.add_argument("--sample-interval", type=int, help="Number of minutes between GPS samples", default=300)
    parser.add_argument("--minimum-satellite-count", type=int, help="Number of satellite counts for valid GPS", default=1)
    args = parser.parse_args()
    return args

def script_main() -> None:
    """ Script's main entrypoint
    """

    # Init
    args = parse_args()

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

    # Gather up the media and associated GPS information.
    # Then build in the timeline.
    multi_medias = tator_api.get_media_list(
        project=config["project"],
        type=config["multi_type_id"],
        section=section.id)

    gps_info = gps_utilities.MultiviewsGPSInfo(
        tator_api=tator_api,
        project=config["project"],
        gps_state_type_id=config["gps_type_id"],
        multi_medias=multi_medias,
        logger=logger)

    gps_info.setup_timeline()

    # Create the samples and the GPS specs
    final_samples = gps_info.get_sampled_states(
        sample_interval=args.sample_interval,
        minimum_satellite_count=args.minimum_satellite_count)

    gps_specs = []
    original_gps_count = len(gps_info.get_gps_states())
    num_samples_with_gps = 0
    num_samples_no_gps = 0
    num_best_gps = 0
    num_prev_gps = 0
    num_next_gps = 0
    for sample in final_samples:

        if sample["valid_gps"] is None:
            logger.info(f'{sample["start"]} - No GPS')
            num_samples_no_gps += 1

        else:
            state = sample["valid_gps"]["state"]
            position = state.attributes["Position"]
            satellite_count = state.attributes["Satellite Count"]
            media_frame = sample["frame"]

            spec = {
                "type": state.meta,
                "media_ids": state.media,
                "frame": sample["frame"]}
            spec.update(state.attributes)
            spec["Datecode"] = sample["start"].isoformat()
            gps_specs.append(spec)

            num_samples_with_gps += 1

            if sample["valid_gps_type"] == "best":
                num_best_gps += 1
            elif sample["valid_gps_type"] == "next":
                num_prev_gps += 1
            elif sample["valid_gps_type"] == "prev":
                num_next_gps += 1

            logger.info(f'{sample["start"]} - GPS Position: {position}, Satellite Count: {satellite_count}, Frame: {media_frame}')

    logger.info(f"Number of original GPS samples: {original_gps_count}")
    logger.info(f"Number of samples with GPS: {num_samples_with_gps} | Best: {num_best_gps} | Next: {num_next_gps} | Prev: {num_prev_gps}")
    logger.info(f"Number of samples without GPS: {num_samples_no_gps}")

    ok = input("Continue with import to Tator? [y/N]: ")
    if ok.lower() == 'y':

        # Delete the existing states
        prime_media_ids = gps_info.get_prime_media_ids()
        for media_id in prime_media_ids:

            existing = tator_api.get_state_list(
                project=config["project"],
                media_id=[media_id],
                type=config["gps_type_id"])

            logger.info(f"Found {len(existing)} on media {media_id} - clearing out.")

            tator_api.delete_state_list(
                project=config["project"],
                media_id=[media_id],
                type=config["gps_type_id"])

        # Create the new states
        created_ids = []
        for response in tator.util.chunked_create(
                tator_api.create_state_list,
                config["project"],
                state_spec=gps_specs):
            created_ids += response.id
            print(response.message)

        print(f"Successfully imported {len(created_ids)} GPS entries!")

        logger.info("Completed GPS sampling")
    else:
        logger.info("GPS sampling aborted")

if __name__ == "__main__":
    script_main()