# -*- coding: utf-8 -*-
# Copyright (C) European Gravitational Observatory (EGO) (2022) and
# Laser Interferometer Gravitational-Wave Observatory (LIGO) (2022)
#
# Author list: Rhys Poulton <poulton@ego-gw.it>
#              Brockill <brockill@uwm.edu>
#
# This file is part of igwn-lldd-common.
#
# igwn-lldd-common is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# igwn-lldd-common is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with igwn-lldd-common.  If not, see <http://www.gnu.org/licenses/>.

import sys
import logging
import time
import datetime
import gpstime
from math import modf
from .framelen import frame_length
from .messageparser import (
    extract_frame_buffer_from_funnel,
    MessageFunnelConsumer,
)
from .statustopic import StatusUpdater
from .utils import (
    check_crc,
)

logger = logging.getLogger()


class FrameKafkaConsumer:

    class CRCChecker:
        NONE = 0
        GDS = 1

    def __init__(self, args, tp_info):

        if args.load_kafka_python:
            global kafka
            import kafka
        else:
            global confluent_kafka
            import confluent_kafka

        bootstrap_servers = args.bootstrap_servers.split(",")
        if args.load_kafka_python:
            logger.info(
                "kafka-python version: [%s]"
                % (sys.modules["kafka"].__version__)
            )
        else:
            logger.info(
                "confluent_kafka version: [%s]"
                % (sys.modules["confluent_kafka"].__version__)
            )
        logger.info(
            "Reading from boostrap_servers: [%s]"
            % (",".join(bootstrap_servers))
        )

        ############################################################
        # Set up communications with Kafka
        ############################################################

        #
        # Throughput workaround followed by bug workaround
        #
        # Workaround:
        #  As can be seen in
        # https://github.com/dpkp/kafka-python/issues/1412 and
        # https://kafka-python.readthedocs.io/en/master/
        # install.html#optional-crc32c-install
        # there are throughput issues unless we either "pip install crc32c"
        # or we set api_version to be 0.10.1. For the moment, we have chosen
        # the latter as it doesn't require extra libraries to be installed
        # on the systems.
        #
        # But this leads to a bug being poked...
        # For some reason, on SL7 (not Debian) when running with
        # ['api_version']='0.10.1'
        # the initial connection consumer = KafkaConsumer (...)
        # immediately returns successfully whether or not the
        # bootstrap server exists. We only see the error later when
        # consumer.poll (...) "hangs" (just sits there).
        #
        # With a temporary workaround:
        #  To temporarily work around this bug, we use sigalrm to
        # make sure that consumer.poll (...) does not hang. It
        # shouldn't, since we have a timeout of 1 second, and if
        # it does we assume things have gone horribly wrong and we exit.
        consumer_args = {}

        #
        # consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers)
        # Apparently need to specify a group_id even if not using assign(),
        # despite what the book on p.92 says.

        self.load_kafka_python = args.load_kafka_python
        self.exit_if_missing_topics = args.exit_if_missing_topics
        self.poll_timeout = args.poll_timeout
        self.poll_max_records = args.poll_max_records
        self.fast_forward = args.fast_forward
        self.verbose = args.verbose

        # Keep a list of paused topics. Topics are paused when we are
        # fast forwarding and waiting for old data to
        # stream in
        self.paused_topics = {}

        if args.ssl is False:
            logger.info("Not using SSL")
            if args.group_id:
                logger.info(f"Using group.id=[{args.group_id}]")
                if args.load_kafka_python:
                    self.consumer = kafka.KafkaConsumer(
                        bootstrap_servers=bootstrap_servers,
                        group_id=args.group_id,
                        **consumer_args,
                    )
                else:
                    self.consumer = confluent_kafka.Consumer(
                        {
                            "bootstrap.servers": ",".join(bootstrap_servers),
                            "group.id": args.group_id,
                            "auto.offset.reset": "latest",
                        }
                    )
            else:
                logger.info("No group.id")
                if args.load_kafka_python:
                    self.consumer = kafka.KafkaConsumer(
                        bootstrap_servers=bootstrap_servers, **consumer_args
                    )
                else:
                    #
                    self.consumer = confluent_kafka.Consumer(
                        {
                            "bootstrap.servers": ",".join(bootstrap_servers),
                            "group.id": "my_unmanaged_group",
                            "auto.offset.reset": "latest",
                        }
                    )

        # See:
        # http://maximilianchrist.com/python/databases/2016/08/13/
        # connect-to-apache-kafka-from-python-using-ssl.html
        # https://www.cloudkarafka.com/blog/2016-12-13-part2-3-
        # apache-kafka-for-beginners_example-and-sample-code-python.html
        if args.ssl is True:
            logger.info("Using SSL")
            if args.group_id:
                logger.info("Using group.id=[", args.group_id, "]")
                self.consumer = kafka.KafkaConsumer(
                    bootstrap_servers=bootstrap_servers,
                    group_id=args.group_id,
                    security_protocol="SSL",
                    ssl_cafile=args.ssl_cafile,
                    ssl_check_hostname=False,
                    ssl_password=args.ssl_password,
                    ssl_certfile=args.ssl_certfile,
                    ssl_keyfile=args.ssl_keyfile,
                    **consumer_args,
                )
            else:
                logger.info("No group.id")
                self.consumer = kafka.KafkaConsumer(
                    bootstrap_servers=bootstrap_servers,
                    security_protocol="SSL",
                    ssl_cafile=args.ssl_cafile,
                    ssl_check_hostname=False,
                    ssl_password=args.ssl_password,
                    ssl_certfile=args.ssl_certfile,
                    ssl_keyfile=args.ssl_keyfile,
                    **consumer_args,
                )

        ############################################################
        # Assign topics
        ############################################################
        # Use assign() instead of subscribe()
        # See e.g. p.92 of book
        if self.load_kafka_python:
            for topic in tp_info:
                topic_partitions = self.consumer.partitions_for_topic(topic)
                if self.exit_if_missing_topics:
                    if 0 not in topic_partitions:
                        logger.error(
                            "Could not find partition 0 of topic [%s].", topic
                        )

        logger.info("Assigning multi-topics")
        if self.load_kafka_python:
            self.consumer.assign(
                [kafka.TopicPartition(topic, 0) for topic in tp_info]
            )
            logger.info("Seek to end for multi-topics")
            # Asterisk to unpack:
            self.consumer.seek_to_end(
                *[kafka.TopicPartition(topic, 0) for topic in tp_info]
            )
        else:
            self.consumer.assign(
                [
                    confluent_kafka.TopicPartition(
                        topic, 0, confluent_kafka.OFFSET_END
                    )
                    for topic in tp_info
                ]
            )
            #
            # Seeking not needed for Confluent Kafka, as we have already
            # specified OFFSET_END when assigning above

        # Setup message funnel
        for topic in tp_info.keys():
            tp_info[topic]["last_time"] = -1
            tp_info[topic]["message_funnel"] = MessageFunnelConsumer()

        # Connect to broker for updating status
        if args.status_updates:
            self.status_updater = StatusUpdater(args)
        else:
            self.status_updater = None
            logger.info("Not updating status to Kafka")

    def check_paused_topics_and_resume(self):

        linux_now = time.time()

        for topic in list(self.paused_topics):
            (resume_time, acceptable_latency) = self.paused_topics[topic]

            logger.info(
                "Checking topic [%s] for resume. Still [%f] seconds to go..."
                % (topic, resume_time - linux_now)
            )
            if linux_now >= resume_time:
                logger.info(
                    "Resuming topic [%s] at [%f]..." % (topic, linux_now)
                )
                self.paused_topics.pop(topic, None)
                if self.load_kafka_python:
                    self.consumer.resume(*[kafka.TopicPartition(topic, 0)])
                else:
                    self.consumer.resume(
                        [confluent_kafka.TopicPartition(topic, 0)]
                    )

                need_seek_to_end = True
                if acceptable_latency > 0.0:
                    logger.info(
                        "Trying to seek to acceptable time for topic [%s] \
i.e. [%f] seconds in the past from now [%f] = [%f]..."
                        % (
                            topic,
                            acceptable_latency,
                            linux_now,
                            linux_now - acceptable_latency,
                        )
                    )

                    #
                    # Seek: works differently in kafka-python and Confluent
                    # (of course...) :P
                    if self.load_kafka_python:
                        #
                        # kafka-python
                        seek_dict = {}
                        seek_dict[kafka.TopicPartition(topic, 0)] = int(
                            (linux_now - acceptable_latency) * 1000.0
                        )
                        offsets = {}
                        try:
                            #
                            # offsets_for_times can raise a number of errors
                            # (ValueError,
                            # UnsupportedVersionError,
                            # KafkaTimeoutError)
                            # none of which are show stoppers
                            offsets = self.consumer.offsets_for_times(
                                seek_dict
                            )
                            for oft in offsets:
                                if offsets[oft] is not None:
                                    # seek can raise an AssertionError if the
                                    # offset isn't >=0 or if the partition
                                    # isn't currently assigned.
                                    self.consumer.seek(
                                        oft, (offsets[oft].offset)
                                    )
                                    need_seek_to_end = False
                        except (
                            ValueError,
                            kafka.errors.KafkaError,
                            kafka.errors.KafkaTimeoutError
                        ):
                            logger.info(
                                "Seeking to acceptable time for topic \
[%s] failed."
                                % (topic)
                            )
                    else:
                        # Confluent
                        offsets = {}
                        tp = confluent_kafka.TopicPartition(topic, 0)
                        tp.offset = int(
                            (linux_now - acceptable_latency) * 1000.0
                        )
                        seek_confluent = [tp]
                        try:
                            offsets = self.consumer.offsets_for_times(
                                seek_confluent
                            )
                            for oft in offsets:
                                self.consumer.seek(oft)
                                need_seek_to_end = False
                        except confluent_kafka.KafkaException:
                            logger.info(
                                "Seeking to acceptable time for topic [%s] \
failed."
                                % (topic)
                            )

                    if need_seek_to_end:
                        logger.info(
                            "Unable to seek to acceptable time for topic [%s]."
                            % (topic)
                        )
                    else:
                        logger.info(
                            "**Worked**: managed to seek to data with \
acceptable latency."
                        )

                if need_seek_to_end:
                    logger.info("Doing a seek_to_end for topic [%s]..." %
                                (topic))
                    #
                    # if seek_to_end raises an AssertionError, meaning
                    # "If any partition is not currently assigned, or if no
                    # partitions are assigned.", then there is a serious error,
                    # and allow the program to halt.
                    if self.load_kafka_python:
                        self.consumer.seek_to_end(
                            *[kafka.TopicPartition(topic, 0)]
                        )
                    else:
                        self.consumer.seek(
                            *[
                                confluent_kafka.TopicPartition(
                                    topic, 0, confluent_kafka.OFFSET_END
                                )
                            ]
                        )

                if self.status_updater:
                    tmp_payload_info = {}
                    tmp_payload_info["topic"] = topic
                    tmp_payload_info["linux_now"] = linux_now
                    self.status_updater.send_status_update(
                        "resume", tmp_payload_info
                    )

    #
    # Pause a topic. When a new pause request comes in, always keep the pause
    # which expires first, i.e. keep the smallest resume_time on record.
    def pause_topic(self, topic, resume_time, acceptable_latency):

        if topic in self.paused_topics:
            (old_resume_time, old_acceptable_latency) = self.paused_topics[
                topic
            ]
            if old_resume_time < resume_time:

                logger.info(
                    "Topic [%s] already in paused_topics with earlier \
resume_time. Ignoring."
                    % (topic)
                )

                return False

            logger.info(
                "Topic [%s] already in paused_topics. Replacing with earlier \
resume_time."
                % (topic)
            )

        self.paused_topics[topic] = (resume_time, acceptable_latency)

        return True

    def poll_consumer_for_topic(self):

        # first check to see if any paused topics which can be unpaused and
        # fast-forwarded
        self.check_paused_topics_and_resume()

        if self.load_kafka_python:
            #
            # kafka-python
            r_poll = self.consumer.poll(
                timeout_ms=self.poll_timeout, max_records=self.poll_max_records
            )

            #
            # No data?
            if r_poll == {}:
                if self.verbose:
                    logger.info("Tick...")

        else:
            #
            # Confluent

            #
            # We use librdkafka's consume() method instead of poll(). Note,
            # however, that there are some people who would prefer that
            # consume() be deprecated:
            # https://github.com/confluentinc/confluent-kafka-python/issues/580
            #
            # Additionally, I haven't been able to get num_messages to work
            # properly with any number other than num_messages=1 (the default).
            # When I set e.g. num_messages to 10000, then the consume() command
            # blocks until 10000 messages are available,mrather than returning
            # fewer messages once timeout has been hit.
            #
            # Q: why does setting num_messages force the consume() command to
            # wait until we have a *minimum* of num_messages? Shouldn't it just
            # return a *maximum* of num_messages?
            #
            # Also note: consume() and poll() just grab messages from
            # librdkafka's internal queue thread:
            # https://stackoverflow.com/questions/59369752/
            # how-to-make-consume-method-as-non-blocking-in-confluent-
            # kafka-for-dot-net
            #
            # This is the command I expected to use, but which blocks until
            # poll_max_records are available:
            # r_poll = consumer.consume(
            #    num_messages=poll_max_records,
            #    timeout=args.poll_timeout/1000.0
            # )
            r_poll = self.consumer.consume(timeout=self.poll_timeout / 1000.0)
            #
            # Silly workaround to allow us to parse messages from Confluent
            # Kafka as they are parsed in kafka-python using the same
            # "for... in" structures below.
            r_poll_all = r_poll
            r_poll = {}

            # Only populate the key if as message is present
            if len(r_poll_all) > 0:
                r_poll["all_messages"] = r_poll_all
            else:
                if self.verbose:
                    logger.info("Tick...")

        return r_poll

    def check_for_confluent_kafka_error(self, message):
        msg_err = message.error()
        if isinstance(msg_err, confluent_kafka.KafkaError):
            if msg_err.code() == confluent_kafka.KafkaError._PARTITION_EOF:
                if False:
                    logger.info("Just an EOF. Ignoring.")
                return 1
            else:
                logger.error(f"** KafkaError**. Reason: [{msg_err.str}]")
                return 2
        if msg_err is not None:
            logger.error(
                f"**Message is an error**. Code: [{msg_err.code()}]. Ignoring."
            )
            return 3
        return 0

    def parse_payload(self, payload, tp_info_topic, payload_info):

        (complete, frame_buffer, timestamp) = extract_frame_buffer_from_funnel(
            payload, tp_info_topic["message_funnel"], payload_info['topic']
        )

        payload_info["length_bytes"] = len(payload)
        payload_info["data_gps_timestamp"] = int(timestamp)
        datetime_now = datetime.datetime.utcnow()
        payload_info["linux_now"] = (
            datetime_now - datetime.datetime(1970, 1, 1)
        ).total_seconds()
        (time_now_frac, time_now_int) = modf(payload_info["linux_now"])

        payload_info["gps_now"] = gpstime.unix2gps(payload_info["linux_now"])
        payload_info["data_latency"] = (
            payload_info["gps_now"] - payload_info["data_gps_timestamp"]
        )
        payload_info["kafka_latency"] = (
            payload_info["linux_now"]
            - payload_info["prod_linux_timestamp"] / 1000.0
        )
        payload_info["last_time"] = tp_info_topic["last_time"]

        return complete, frame_buffer

    def check_status_of_topic(self, frame_buffer, tp_info_topic, payload_info):

        # is this message too old?
        if (
            tp_info_topic["max_latency"] > 0
            and payload_info["data_latency"] > tp_info_topic["max_latency"]
        ) or (
            tp_info_topic["max_kafka_latency"] > 0
            and payload_info["kafka_latency"]
            > tp_info_topic["max_kafka_latency"]
        ):
            if self.verbose:
                logger.info(
                    "TOO_LATE:Topic: [%s] %s %0.6f get %d %d OK %0.6f \
Kafka_latency: %0.6f"
                    % (
                        payload_info["topic"],
                        " ".join(tp_info_topic["extra_info_str"]),
                        payload_info["gps_now"],
                        payload_info["data_gps_timestamp"],
                        payload_info["length_bytes"],
                        payload_info["data_latency"],
                        payload_info["kafka_latency"],
                    )
                )
            if self.status_updater:
                self.status_updater.send_status_update("old", payload_info)

                # record this as last processed time
            tp_info_topic["last_time"] = payload_info["data_gps_timestamp"]
            #
            # should we try to fast forward?
            if self.fast_forward:
                #
                # Yes. Pause the topic for fast_forward_buffer to allow data to
                # roll in.
                if self.pause_topic(
                    payload_info["topic"],
                    payload_info["linux_now"]
                    + tp_info_topic["fast_forward_buffer"],
                    tp_info_topic["acceptable_latency"],
                ):

                    logger.info(
                        "Pausing topic [%s] for [%f] seconds before \
fast-forwarding to allow data to come in..."
                        % (
                            payload_info["topic"],
                            tp_info_topic["fast_forward_buffer"],
                        )
                    )
                    if self.load_kafka_python:
                        #
                        # NOTE (!): If max_records in
                        # r_poll = consumer.poll(
                        #     timeout_ms=poll_timeout,
                        #     max_records=poll_max_records
                        # )
                        # is not just 1, then there could be multiple messages
                        # in the queue, and they will come flooding in even if
                        # the topic is paused!
                        self.consumer.pause(
                            *[kafka.TopicPartition(payload_info["topic"], 0)]
                        )
                    else:
                        self.consumer.pause(
                            [
                                confluent_kafka.TopicPartition(
                                    payload_info["topic"], 0
                                )
                            ]
                        )
                    if self.status_updater:
                        payload_info["fast_forward_buffer"] = \
                            tp_info_topic["fast_forward_buffer"]
                        self.status_updater.send_status_update(
                            "fast_forward", payload_info
                        )
                else:
                    logger.info(
                        "Not pausing topic [%s]: topic already paused with \
earlier resume_time."
                        % (payload_info["topic"])
                    )
            return 4

        if self.verbose:
            logger.info(
                "Topic: [%s] %s %0.6f get %d %d OK %0.6f Kafka_latency: %0.6f"
                % (
                    payload_info["topic"],
                    " ".join(tp_info_topic["extra_info_str"]),
                    payload_info["gps_now"],
                    payload_info["data_gps_timestamp"],
                    payload_info["length_bytes"],
                    payload_info["data_latency"],
                    payload_info["kafka_latency"],
                )
            )
        if self.status_updater:
            self.status_updater.send_status_update("good", payload_info)

        # Check if the timestamp receive is just e.g. 4-seconds (or 1-second)
        # after the last timestamp
        if tp_info_topic["delta_t"] or tp_info_topic["delta_t_fallback"]:
            if tp_info_topic["delta_t"]:
                payload_info["frame_duration"] = tp_info_topic["delta_t"]
            if tp_info_topic["delta_t_fallback"]:
                (
                    frame_start_time,
                    frame_stop_time,
                    payload_info["frame_duration"],
                ) = frame_length(frame_buffer)
                logger.debug(
                    " [debug]: frame_start_time: [%f], frame_stop_time: [%f], \
frame_duration: [%f]"
                    % (
                        frame_start_time,
                        frame_stop_time,
                        payload_info["frame_duration"],
                    )
                )

            if payload_info["last_time"] == -1:
                tp_info_topic["last_time"] = payload_info["data_gps_timestamp"]
                return 0

            #
            # Lost data
            if (
                payload_info["last_time"] + payload_info["frame_duration"]
                < payload_info["data_gps_timestamp"]
            ):

                logger.info(
                    "Topic: [%s] %s Lost %d seconds between: [%d,%d)"
                    % (
                        payload_info["topic"],
                        " ".join(tp_info_topic["extra_info_str"]),
                        payload_info["data_gps_timestamp"]
                        - payload_info["last_time"],
                        payload_info["last_time"],
                        payload_info["data_gps_timestamp"],
                    )
                )

                if self.status_updater:
                    self.status_updater.send_status_update(
                        "missing", payload_info
                    )

            #
            # Replayed data
            if (
                payload_info["last_time"] + payload_info["frame_duration"]
                > payload_info["data_gps_timestamp"]
            ):
                logger.info(
                    "Topic: [%s] %s Replayed time between: [%d,%d)"
                    % (
                        payload_info["topic"],
                        " ".join(tp_info_topic["extra_info_str"]),
                        payload_info["last_time"],
                        payload_info["data_gps_timestamp"],
                    )
                )
                if self.status_updater:
                    self.status_updater.send_status_update(
                        "replay", payload_info
                    )

            tp_info_topic["last_time"] = payload_info["data_gps_timestamp"]

        return 0

    def extract_frame_buffer_from_message(self, message, tp_info,
                                          crc_checker=CRCChecker.NONE):

        # Dictionary containing information about the kafka payload
        payload_info = {}

        # is this message an errror?
        if not self.load_kafka_python:
            returncode = self.check_for_confluent_kafka_error(message)
            if returncode != 0:
                return "", payload_info

        # Extract the payload, topic and timestamp from the message:
        if self.load_kafka_python:
            payload = message.value
            payload_info["topic"] = message.topic
            payload_info["prod_linux_timestamp"] = message.timestamp
        else:
            payload = message.value()
            payload_info["topic"] = message.topic()
            payload_info["prod_linux_timestamp"] = message.timestamp()[1]

        tp_info_topic = tp_info[payload_info["topic"]]

        # See if there is any extra info to put into the payload_info
        if (tp_info_topic["extra_info"]):
            for key, value in tp_info_topic["extra_info"].items():
                payload_info[key] = value

        if payload[0:4] == b"PART":

            # Extract the frame from the petload
            complete, frame_buffer = self.parse_payload(
                payload, tp_info_topic, payload_info
            )

            if not complete:
                return "", payload_info

            # Check if CRC is okay
            if crc_checker == FrameKafkaConsumer.CRCChecker.GDS:
                # Can check validity of CRC routines by using e.g.
                # frame_buffer_bad=frame_buffer[0:499]+b'\x03'+frame_buffer[500:]
                returncode = check_crc(
                    tp_info[payload_info["topic"]]["lsmp_writer"],
                    payload_info["topic"],
                    frame_buffer,
                    payload_info["data_gps_timestamp"]
                )

                if returncode != 0:
                    return "", payload_info

            # Check the status of the topic, print to the log and send the
            # status topic of requested
            returncode = self.check_status_of_topic(
                frame_buffer, tp_info_topic, payload_info
            )

            if returncode != 0:
                return "", payload_info

            return frame_buffer, payload_info

        elif payload[0:4] == b"IGWD":
            logger.info(
                "Raw IGWD frame. Do not know the timestamp, setting as zero"
            )
            return "", payload_info

        else:
            logger.warn(
                "Unknown binary data. Normally, our binary data begins either \
with IGWD or PART. Ignoring this chunk of data"
            )
            return "", payload_info

    def close(self):

        # Close the status producer
        if self.status_updater:
            self.status_updater.close()

        # Close the consumer
        self.consumer.close()
