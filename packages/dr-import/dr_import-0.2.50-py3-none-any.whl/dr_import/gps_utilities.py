""" Module encapsulating GPS related utilities used to process EM data on Tator
"""
from abc import ABC, abstractmethod

import datetime
import dateutil.parser
import logging
import pytz

import tator

class BaseGPSInfo(ABC):
    """ GPS helper class
    """

    def __init__(
            self,
            tator_api: tator.openapi.tator_openapi.api.tator_api.TatorApi,
            project: int,
            gps_state_type_id: int,
            logger: logging.Logger):
        """ Constructor

        :param tator_api: Connected interface to Tator server
        :param project: Associated Tator project ID
        :param gps_state_type_id: Tator ID of GPS state type
        :param logger: Log interface

        """

        self.tator_api = tator_api
        self.project = project
        self.gps_state_type_id = gps_state_type_id
        self.logger = logger

    def log_message(self, msg: str) -> None:
        """ Logs the provided message if a logger is setup
        :param msg: Message to log
        """

        if self.logger is not None:
            self.logger.info(msg)

    @abstractmethod
    def setup_timeline(self) -> None:
        """ Sets up the timeline using the saved media information
        """
        pass

    @abstractmethod
    def get_time(self, media_id: int, frame: int) -> datetime.datetime:
        """ Returns the datetime associated with the given media_id/frame combination

        :param media_id: Media ID associated with the provided frame
        :param frame: Media frame to get the associated time for

        :return:
          - Time (datetime.datetime)
        """
        pass

    @abstractmethod
    def get_lat_lon_time(self, media_id: int, frame: int) -> tuple:
        """ Returns the latitude/longitude associated with the given media_id/frame combo

        :param media_id: Media ID associated with the provided frame
        :param frame: Media frame to get the associated time for

        :return:
          - Time (datetime.datetime)
          - Latitude (float)
          - Longitude (float)
          - Satellite count (int)
        """
        pass

class MultiviewsGPSInfo(BaseGPSInfo):
    """ Implementation of abstract BaseGPSInfo class that uses Tator multiview media

    Datetime's are based on the media names

    GPS positions are used from registered states
      - GPS collections with 0 satellites are ignored
      - Position closest in time with existing GPS used
      - GPS collections with satellite counts of None but with numerical positions
        are considered valid

    """

    def __init__(
            self,
            tator_api: tator.openapi.tator_openapi.api.tator_api.TatorApi,
            project: int,
            gps_state_type_id: int,
            logger: logging.Logger,
            multi_medias: list) -> None:
        """ Constructor

        :param tator_api: Connected interface to Tator server
        :param project: Associated Tator project ID
        :param gps_state_type_id: Tator ID of GPS state type
        :param logger: Log interface
        :param multi_medias: List of multis Tator media objects associated with a trip

        """

        BaseGPSInfo.__init__(
            self,
            tator_api=tator_api,
            project=project,
            gps_state_type_id=gps_state_type_id,
            logger=logger)

        self.multi_medias = multi_medias

    def setup_timeline(self) -> None:
        """ [Inherited] See parent's comments.

        Time calls are based on the media's name and FPS, not GPS
        GPS position (latitude/longitude) are nearest (based on time).

        """

        self.log_message(msg="Setting up timeline")

        self.gps_states = []
        self.media_start_times = {} # Keys are single video media ids
        self.gps_entries = {} # Keys are the GPS datetimes
        self.start_media_time = datetime.datetime.now().replace(tzinfo=pytz.UTC)
        self.prime_medias = []
        for multi in self.multi_medias:

            self.log_message(msg=f"Processing time and position info of multi-view file: {multi.name}")

            start_datetime = dateutil.parser.parse(multi.name.replace("_",":").split(".")[0])
            start_datetime = start_datetime.replace(tzinfo=pytz.UTC)
            self.log_message(msg=str(start_datetime))

            if self.start_media_time > start_datetime:
                self.start_media_time = start_datetime

            # Get seconds per frame frorm the first media in the multiview
            primary_media = self.tator_api.get_media(id=multi.media_files.ids[0])
            self.prime_medias.append(primary_media)
            seconds_per_frame = 1.0 / primary_media.fps

            # Save the time information for the media
            self.media_start_times[multi.id] = {
                "start_datetime": start_datetime,
                "seconds_per_frame": seconds_per_frame}

            for media_id in multi.media_files.ids:
                self.media_start_times[media_id] = {
                    "start_datetime": start_datetime,
                    "seconds_per_frame": seconds_per_frame}

            # Next, get the GPS information.
            states = self.tator_api.get_state_list(
                project=self.project,
                media_id=[primary_media.id],
                type=self.gps_state_type_id)

            self.gps_states.extend(states)

            for state in states:
                seconds_from_start = int(seconds_per_frame * state.frame)
                gps_datetime = start_datetime + datetime.timedelta(seconds=seconds_from_start)

                satellite_count = 0
                position = ""
                position_valid = False
                if "Position" in state.attributes:
                    position = state.attributes["Position"]
                    if "Satellite Count" not in state.attributes and position is not None:
                        satellite_count = 1

                    elif state.attributes["Satellite Count"] is None and position is not None:
                        satellite_count = 1

                    else:
                        satellite_count = int(state.attributes["Satellite Count"])

                    try:
                        lon = float(position[0])
                        lat = float(position[1])
                        if lon != 0.0 and lat != 0.0:
                            position_valid = True

                    except:
                        pass

                knots = ""
                if "Knots" in state.attributes:
                    knots = state.attributes["Knots"]

                if satellite_count > 0 and position_valid:
                    self.gps_entries[gps_datetime] = {
                        "state": state,
                        "lon_lat": position,
                        "satellite_count": satellite_count,
                        "knots": knots}
                else:
                    self.log_message(msg=f"Ignoring GPS entry (satellite count = {satellite_count}, position = {position}) datetime - {gps_datetime}")

            # Now that we have all the GPS entries, sort the datetimes that can be used to
            # reference the self.gps_entries
            self.sorted_gps_times = sorted(self.gps_entries.keys())

    def get_time(
            self,
            media_id: int,
            frame: int) -> datetime.datetime:
        """ [Inherited] See parent's comments.
        """

        info = self.media_start_times[media_id]
        seconds_from_start = int(info["seconds_per_frame"] * frame)
        return info["start_datetime"] + datetime.timedelta(seconds=seconds_from_start)

    def get_lat_lon_time(
            self,
            media_id: int,
            frame: int) -> tuple:
        """ [Inherited] See parent's comments.
        """

        current_time = self.get_time(media_id=media_id, frame=frame)
        if len(self.gps_entries.keys()) > 0:
            index = min(self.gps_entries.keys(), key=lambda x: abs(x - current_time))
            return self.gps_entries[index]["lon_lat"][1], self.gps_entries[index]["lon_lat"][0], current_time, self.gps_entries[index]["satellite_count"]

        else:
            return "1", "-1", current_time, 0

    def get_sampled_states(
            self,
            sample_interval: int,
            minimum_satellite_count: int) -> list:
        """ Returns a list of media/GPS states at the given sample interval

        :param sample_interval: Seconds between states
        :param minimum_satellite_count: Minimum number of satellites for valid GPS
        :return list: List of dicts with the following keys
            "media_id": multi media ID
            "states": List of ordered GPS states that are separated by the sample interval
        """

        # Empty list if there is no GPS
        if len(self.sorted_gps_times) < 1:
            return []

        # Set up the sample list time boundaries
        current_start = self.start_media_time
        samples = [
            {
                "start": current_start,
                "next_start": current_start + datetime.timedelta(seconds=sample_interval),
                "gps": []
            }]

        last_gps_time = self.sorted_gps_times[-1]
        while current_start <= last_gps_time:
            current_start = current_start + datetime.timedelta(seconds=sample_interval)

            samples.append({
                "start": current_start,
                "next_start": current_start + datetime.timedelta(seconds=sample_interval),
                "gps": []
            })

        # Now, separate out the GPS states into the sample bins
        for gps_time in self.gps_entries:
            found_match = False
            for sample in samples:
                if gps_time >= sample["start"] and gps_time <= sample["next_start"]:
                    found_match = True
                    sample["gps"].append({
                        "state": self.gps_entries[gps_time]["state"],
                        "time": gps_time})

            if not found_match:
                self.log_message(msg=f"Could not find sample bin match for {gps_time}")

        # Sort the GPS in each bin
        for sample in samples:
            sample["gps"] = sorted(sample["gps"], key=lambda x: x["time"])

        # Perform the filtering for each bin
        # - Select the state with the highest satellite count
        # - If there are no states in the bin, look at the next bin if available and
        #   select the first state that meets the minimum satellite criteria
        # - If the previous step failed to get a state, look at the previous bin and
        #   select the last state that meets the minimum satellite criteria
        final_samples = []
        for sample_index, sample in enumerate(samples):
            valid_gps = None
            valid_gps_type = "none"

            for gps in sample["gps"]:
                if int(gps["state"].attributes["Satellite Count"]) >= minimum_satellite_count:
                    if valid_gps is None:
                        valid_gps = gps
                        valid_gps_type = "best"
                    else:
                        if int(gps["state"].attributes["Satellite Count"]) > int(valid_gps["state"].attributes["Satellite Count"]):
                            valid_gps = gps

            if valid_gps is None:
                if sample_index + 1 < len(samples):
                    next_sample = samples[sample_index + 1]
                    for gps in next_sample["gps"]:
                        if int(gps["state"].attributes["Satellite Count"]) >= minimum_satellite_count:
                            valid_gps = gps
                            valid_gps_type = "next"
                            break

            if valid_gps is None:
                if sample_index > 0:
                    prev_sample = samples[sample_index - 1]
                    for gps in reversed(prev_sample["gps"]):
                        if int(gps["state"].attributes["Satellite Count"]) >= minimum_satellite_count:
                            valid_gps = gps
                            valid_gps_type = "prev"
                            break

            # Using the media associated with the valid GPS, grab the closest frame to the
            # start of the sample
            if valid_gps is None:
                media_frame = None
            else:
                for media in self.prime_medias:
                    if media.id in valid_gps["state"].media:
                        media_start = self.media_start_times[media.id]["start_datetime"]
                        delta_seconds = (sample["start"] - media_start).total_seconds()
                        media_frame = int(delta_seconds * media.fps);

                        if media_frame < 0:
                            media_frame = 0
                        elif media_frame >= media.num_frames:
                            media_frame = media.num_frames - 1

                        break

            final_samples.append({
                "frame": media_frame,
                "start": sample["start"],
                "next_start": sample["next_start"],
                "raw_gps": sample["gps"],
                "valid_gps": valid_gps,
                "valid_gps_type": valid_gps_type})

        return final_samples

    def get_gps_states(self) -> list:
        return self.gps_states

    def get_prime_media_ids(self) -> list:
        return [media.id for media in self.prime_medias]

    def get_gps_entries(self) -> dict:
        """ GPS entries key'd by datetime """
        return self.gps_entries;