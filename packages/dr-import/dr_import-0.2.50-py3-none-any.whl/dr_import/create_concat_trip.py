""" Tool used to create a concat version of an already uploaded trip

The tool will take the existing multis and create a single concat video for each camera using
the order defined by each video. Assumes that the Camera attribute is filled out appropriately.

From that, it will create the multis of concat videos.

This assumes that the temporal gap video exists in both the source and destination projects.
Temporal gaps will be applied whenever there is less than the maximum amount of cameras.

"""

import argparse
import logging
import os
import sys
import yaml

import tator

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def main(
    token: str,
    src_info: dict,
    dest_info: dict,
    src_trip_name: str,
    dest_trip_name: str) -> None:
    """

    .concat trips are created by creating individual .concat

    :param token: Tator API token
    :param src_info: .yaml project info where original trip is
    :param dest_info: .yaml project info where destination trip will be cloned to
    :param src_trip_name: Name of Tator section to copy
    :param dest_trip_name: Name of new Tator section containing clone
    """

    # Pull information from config
    concat_duration = dest_info["concat_duration"]
    gap_name = dest_info["gap_name"]

    tator_api = tator.get_api(host=dest_info["host"], token=token)
    src_project = tator_api.get_project(id=src_info["project"])
    dest_project = tator_api.get_project(id=dest_info["project"])

    # Get all the multis in the source trip
    src_section = tator_api.get_section_list(
        project=src_project.id,
        name=src_trip_name)[0]

    src_multis = tator_api.get_media_list(
        project=src_project.id,
        type=src_info["multi_type_id"],
        section=src_section.id)

    # Get all the medias of the single camera videos and get the number of cameras.
    video_ids = []
    for multi in src_multis:
        video_ids.extend(multi.media_files.ids)

    src_videos = tator_api.get_media_list_by_id(
        project=src_project.id,
        media_id_query={'ids': video_ids})

    camera_ids = set()
    src_video_map = {}
    for video in src_videos:
        src_video_map[video.id] = video

        video_camera = video.attributes["Camera"]
        if video_camera not in camera_ids:
            camera_ids.add(video_camera)

    max_cameras = len(camera_ids)
    logger.info(f"Cameras ({max_cameras}): {camera_ids}")

    # Get the temporal gap video in the destination project
    medias = tator_api.get_media_list(project=dest_project.id, name=gap_name)
    video_gap_media = medias[0]

    # Now go through each of the multis and stitch the camera videos together
    # If for a given multi the camera ID is missing, it is assumed it's a temporal gap so
    # the temporal gap video is applied in place.
    camera_map = {}
    for camera_id in camera_ids:
        camera_map[camera_id] = []

    prime_video_mapping = {} # Keys = src_multi.media_files.ids[0], values = dest_multi.media_files.ids
    src_multis.sort(key=lambda x: x.name)
    logger.info("--- Cloning camera clips in source multis")
    for multi in src_multis:

        # Clone the individual video media
        spec = {
          "dest_project": dest_project.id,
          "dest_type": dest_info["video_type_id"],
          "dest_section": dest_trip_name + " single 1hr"
        }
        logger.info(f"Cloning source multi.media_files.ids: {multi.media_files.ids}")
        response = tator_api.clone_media_list(
            project=src_project.id,
            media_id=multi.media_files.ids,
            clone_media_spec=spec)
        logger.info(response.message)
        clone_media_map_ids = {}
        for clone_id, orig_id in zip(response.id, multi.media_files.ids):
            clone_media_map_ids[orig_id] = clone_id

        prime_video_mapping[multi.media_files.ids[0]] = response.id

        # Map the per-camera information for concat
        clip_camera_map = {}
        for camera_id in camera_ids:
            clip_camera_map[camera_id] = None

        num_frames = -1
        saved_video = None
        for video_id in multi.media_files.ids:
            video_media = src_video_map[video_id]
            camera_id = video_media.attributes["Camera"]
            clip_camera_map[camera_id] = video_media
            if video_media.num_frames > num_frames:
                num_frames = video_media.num_frames
                saved_video = video_media

        for camera_id in clip_camera_map:
            if clip_camera_map[camera_id] is None:

                logger.info(f"Cloning video gap media")

                response = tator_api.clone_media_list(
                    project=dest_project.id,
                    media_id=[video_gap_media.id],
                    clone_media_spec={
                      "dest_project": dest_project.id,
                      "dest_type": dest_info["video_type_id"],
                      "dest_section": dest_trip_name + " single 1hr"
                    })
                logger.info(response.message)
                cloned_gap_media_id = response.id[0]

                tator_api.update_media(id=cloned_gap_media_id, media_update={
                  "attributes": {
                    "Date": saved_video.attributes["Date"],
                    "Time": saved_video.attributes["Time"],
                    "Trip": saved_video.attributes["Trip"],
                    "Camera": camera_id
                  }
                })

                camera_map[camera_id].append({
                    "multi": multi,
                    "media_id": cloned_gap_media_id.id,
                    "num_frames": num_frames})

            else:
                camera_map[camera_id].append({
                    "multi": multi,
                    "media_id": clone_media_map_ids[clip_camera_map[camera_id].id],
                    "num_frames": num_frames})

    # With all the media cloned, apply the GPS states
    logger.info("--- Copying over GPS states")
    for src_video_id, dest_video_ids in prime_video_mapping.items():
        states = tator_api.get_state_list(
            project=src_project.id, media_id=[src_video_id], type=src_info["gps_type_id"])

        dest_state_specs = []
        for state in states:
            spec = {
                "type": dest_info["gps_type_id"],
                "media_ids": dest_video_ids,
                "localization_ids": [],
                "version": dest_info["baseline_version_id"],
                **state.attributes
            }
            if state.frame is not None:
                spec["frame"] = state.frame

            keys_to_remove = []
            for key in spec:
                if spec[key] is None:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del spec[key]

            dest_state_specs.append(spec)

        if len(states) > 0:
            response = tator_api.create_state_list(project=dest_project.id, state_spec=dest_state_specs)
            logger.info(response.message)

    # With the cloned video clips lined up by camera, create each of the concat files
    for camera_id in camera_map:
        logger.info(f"--- Creating single camera .concat videos for: {camera_id}")

        start_clip = True
        for video_info in camera_map[camera_id]:
            if start_clip:
                clip_name = os.path.splitext(video_info["multi"].name)[0]
                clip_ids = []
                clip_duration = 0
                offsets = [0]
                start_clip = False

            clip_ids.append(video_info["media_id"])
            clip_duration += video_info["num_frames"]
            offsets.append(offsets[-1] + video_info["num_frames"] / dest_info["baseline_fps"])

            # TODO Figure out offsets (I believe this is only necessary for gap videos)
            if clip_duration > concat_duration:
                start_clip = True
                offsets.pop(-1)
                logger.info(f"Creating concat video {clip_name} with:\nIDs: {clip_ids}\n Offsets: {offsets}")
                response = tator.util.make_concat(
                    api=tator_api,
                    name=clip_name,
                    media_ids=clip_ids,
                    section=f"{dest_trip_name} single 12hr",
                    offsets=offsets)
                logger.info(response.message)
                concat_def = [{"id": media_id, "timestampOffset": offset} for media_id, offset in zip(clip_ids, offsets)]
                response = tator_api.update_media(response.id, {
                    "concat": concat_def,
                    "summaryLevel": dest_info["scrub_interval"],
                    "num_frames": clip_duration})
                logger.info(response.message)

        if clip_duration > 0 and not start_clip:
            offsets.pop(-1)
            logger.info(f"Creating concat video {clip_name} with:\nIDs: {clip_ids}\n Offsets: {offsets}")
            response = tator.util.make_concat(
                api=tator_api,
                name=clip_name,
                media_ids=clip_ids,
                section=f"{dest_trip_name} single 12hr",
                offsets=offsets)
            logger.info(response.message)
            concat_def = [{"id": media_id, "timestampOffset": offset} for media_id, offset in zip(clip_ids, offsets)]
            response = tator_api.update_media(response.id, {
                "concat": concat_def,
                "summaryLevel": dest_info["scrub_interval"],
                "num_frames": clip_duration})
            logger.info(response.message)

def parse_args() -> argparse.Namespace:
    """ Parse the script arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, required=True, help="Tator API user token")
    parser.add_argument("--src-config", type=str, required=True, help=".yaml file of source project")
    parser.add_argument("--dest-config", type=str, required=True, help=".yaml file of destination project")
    parser.add_argument("--trip-name", type=str, required=True, help="Section name of trip to clone in source project")
    parser.add_argument("--dest-trip-name", type=str, required=False, help="Name of cloned trip in destination project. If omitted, the same trip name is used.")
    args = parser.parse_args()
    return args

if __name__ == "__main__":

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