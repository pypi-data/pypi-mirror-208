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
import collections
import gpstime
from math import modf
from .messageparser import MessageFunnelProducer
from .statustopic import StatusUpdater

logger = logging.getLogger()


class FrameKafkaProducer:
    def __init__(self, args):

        self.part_id = 0
        self.split_bytes = args.split_bytes
        self.verbose = args.verbose
        self.load_kafka_python = args.load_kafka_python
        self.delta_t = args.delta_t
        self.min_interval = args.min_interval
        self.last_time_before_send_unix = -1
        self.time_before_send_unix = -1
        self.last_timestamp = -1
        self.time_before_flush_unix = -1
        self.time_after_flush_unix = -1
        self.time_after_flush_gps = -1
        self.time_during_send_flush = -1
        self.send_stats = collections.deque([], 100)
        self.data_n = 0
        self.data_rate = 0
        self.topic = args.topic
        if hasattr(args, "partition"):
            self.partition = args.partition
        else:
            self.partition = None

        if args.load_kafka_python:
            global kafka
            import kafka
        else:
            global confluent_kafka
            import confluent_kafka

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

        prod_args = {}
        if args.acks:
            prod_args["acks"] = args.acks
        if args.batch_size:
            prod_args["batch_size"] = args.batch_size
        if args.buffer_memory:
            prod_args["buffer_memory"] = args.buffer_memory
        if args.linger_ms:
            prod_args["linger_ms"] = args.linger_ms

        # https://stackoverflow.com/questions/337688/
        # dynamic-keyword-arguments-in-python
        # https://stackoverflow.com/questions/36901/
        # what-does-double-star-asterisk-and-star-asterisk-do-for-parameters

        bootstrap_servers = args.bootstrap_servers.split(",")
        if args.load_kafka_python:
            self.producer = kafka.KafkaProducer(
                bootstrap_servers=bootstrap_servers, **prod_args
            )
        else:
            self.producer = confluent_kafka.Producer(
                {"bootstrap.servers": ",".join(bootstrap_servers)}
            )

        self.messagefunnelproducer = MessageFunnelProducer()

        # Connect to broker for updating status
        if args.status_updates:
            self.status_updater = StatusUpdater(args)
        else:
            self.status_updater = None
            logger.info("Not updating status to Kafka")

    def send_frame(self, data, timestamp):

        time_after_read_unix = time.time()
        if self.verbose:
            logger.info(
                "[*] Received a new frame: [%s] timestamp: %d, time: %0.6f"
                % (self.topic, timestamp, time_after_read_unix)
            )

        # Create payloads of 100KB each
        payloads = self.messagefunnelproducer.create_payloads(
            data, timestamp, self.split_bytes
        )

        # the time between the last time we were at this point and this time
        # around should be at least min_interval seconds
        time_before_sleep_unix = time.time()

        if self.last_time_before_send_unix != -1:
            if self.verbose:
                logger.info(
                    "  [+] at this point diff_send:%0.6f"
                    % (
                        time_before_sleep_unix
                        - self.last_time_before_send_unix
                    )
                )

        # if not at least min_interval seconds, then sleep until we have
        # completed min_interval seconds
        if (
            self.last_time_before_send_unix != -1
            and self.min_interval > 0
            and time_before_sleep_unix - self.last_time_before_send_unix
            < self.min_interval
        ):
            time_since_last = (
                time_before_sleep_unix - self.last_self.time_before_send_unix
            )
            amount_to_sleep = self.min_interval - time_since_last
            logger.info(
                "  [+] sleep: current time is %0.6f, previous frame sent at \
%0.6f. Sleeping %0.6f seconds since only %0.6f seconds since last frame."
                % (
                    time_before_sleep_unix,
                    self.last_time_before_send_unix,
                    amount_to_sleep,
                    time_since_last,
                )
            )
            time.sleep(amount_to_sleep)

            time_after_sleep_unix = time.time()
            if self.last_time_before_send_unix != -1:
                if self.verbose:
                    logger.info(
                        "    [-] after sleeping, new diff_send:%0.6f"
                        % (
                            time_after_sleep_unix
                            - self.last_self.time_before_send_unix
                        )
                    )

        self.time_before_send_unix = time.time()

        # Produce the kafka message for the topic
        for payload in payloads:
            if self.load_kafka_python:
                self.producer.send(self.topic, payload)
            else:
                self.producer.produce(self.topic, payload)

        # save the last time after flush
        last_time_after_flush_unix = self.time_after_flush_unix

        # flush *after* all of the split pieces have been queued
        self.time_before_flush_unix = time.time()

        # now actually flush. This can take quite a while, depending on the
        # number of messages
        # and their size.
        self.producer.flush()

        # get the time now in a datetime structure for use in converting to
        # gps seconds below
        time_after_flush_datetime = datetime.datetime.utcnow()

        # get the same time as above, but now in the normal unix time.
        # Note, we could have just used
        # self.time_after_flush_unix=time.time(), but this would be
        # slightly later. So we convert the above instead.
        self.time_after_flush_unix = (
            time_after_flush_datetime - datetime.datetime(1970, 1, 1)
        ).total_seconds()

        # now get the same time as above, but in gps
        # Note that we wanted to use the next statement, but there seems to be
        # a bug, as it is off by 4 seconds:
        # self.time_after_flush_gps=gpstime.GpsSecondsFromPyUTC(
        #     int_self.time_after_flush_unix)
        #     + frac_self.time_after_flush_unix
        # one of the fun things about this is that UTCToGPS only
        # works on integers. So we save the fractional
        # part and then add it to the final result. :P
        (frac_time_after_flush_unix, int_time_after_flush_unix) = modf(
            self.time_after_flush_unix
        )
        self.time_after_flush_gps = (
            gpstime.unix2gps(self.time_after_flush_unix)
            + frac_time_after_flush_unix
        )

        # the amount of time spent sending andn flushing
        self.time_during_send_flush = (
            self.time_after_flush_unix - self.time_before_send_unix
        )

        # calculate the data rate
        self.send_stats.append(
            [
                self.time_after_flush_unix,
                len(data),
                self.time_during_send_flush,
            ]
        )
        data_bytes = 0
        self.data_n = 0
        data_time = 0
        for elem in self.send_stats:
            # only look at last 30 seconds
            if self.time_after_flush_unix - elem[0] < 30.0:
                self.data_n += 1
                data_bytes += elem[1]
                data_time += elem[2]
        if data_time != 0:
            self.data_rate = (data_bytes / data_time) / 1000000.0
        else:
            self.data_rate = -1.0

        # Print our the status
        if self.verbose:
            if self.partition is not None:
                logger.info(
                    "  [+] flushed: [%s] Partition: [%s] gps:%0.6f put %d %d \
OK latency:%0.6f unix:%0.6f send:%0.6f flush:%0.6f send+flush:%0.6f \
avg_rate_30s_MBs:%0.3f self.data_n:%d"
                    % (
                        self.topic,
                        self.partition,
                        self.time_after_flush_gps,
                        timestamp,
                        len(data),
                        self.time_after_flush_gps - timestamp,
                        self.time_after_flush_unix,
                        self.time_before_flush_unix
                        - self.time_before_send_unix,
                        self.time_after_flush_unix
                        - self.time_before_flush_unix,
                        self.time_during_send_flush,
                        self.data_rate,
                        self.data_n,
                    )
                )
            else:
                logger.info(
                    "  [+] flushed: [%s] gps:%0.6f put %d %d OK latency:%0.6f \
unix:%0.6f send:%0.6f flush:%0.6f send+flush:%0.6f \
avg_rate_30s_MBs:%0.3f self.data_n:%d"
                    % (
                        self.topic,
                        self.time_after_flush_gps,
                        timestamp,
                        len(data),
                        self.time_after_flush_gps - timestamp,
                        self.time_after_flush_unix,
                        self.time_before_flush_unix
                        - self.time_before_send_unix,
                        self.time_after_flush_unix
                        - self.time_before_flush_unix,
                        self.time_during_send_flush,
                        self.data_rate,
                        self.data_n,
                    )
                )

            if (
                self.time_after_flush_unix != -1
                and last_time_after_flush_unix != -1
            ):
                logger.info(
                    "    [-] diff_flush:%0.6f"
                    % (self.time_after_flush_unix - last_time_after_flush_unix)
                )

        if (
            self.delta_t > 0
            and self.last_timestamp != -1
            and self.last_timestamp + self.delta_t != timestamp
        ):
            logger.info(
                "Error: missing %d seconds of data. Last timestamp was %d and \
current timestamp is %d. We expect frames to come in every %d seconds."
                % (
                    timestamp - self.last_timestamp - self.delta_t,
                    self.last_timestamp,
                    timestamp,
                    self.delta_t,
                )
            )

        # Send the status topic
        if self.status_updater:
            status_dict = {}
            status_dict["status"] = "good"
            status_dict["topic"] = self.topic
            if self.partition is not None:
                status_dict["partition"] = self.partition
            status_dict["gps_now"] = self.time_after_flush_gps
            status_dict["linux_now"] = self.time_after_flush_unix
            status_dict["data_gps_timestamp"] = timestamp
            status_dict["length_bytes"] = len(data)
            # how late the data is at this point
            status_dict["prod_gps_latency"] = (
                self.time_after_flush_gps - timestamp
            )

            self.status_updater.send_status_update("good", status_dict)

        # Set the last time a frame was produced to be the time the frame was
        # *sent* (not flushed) to Kafka, *not* the time now, i.e. we do *not*
        # use self.time_after_flush_unix. After all, it is the time between
        # sending the frames which we expect to be e.g. 1 second and it could
        # be that the .flush() and .send() calls above take a non-trivial
        # amount of time to complete.
        self.last_time_before_send_unix = self.time_before_send_unix
        self.last_timestamp = timestamp

    def close(self):

        # flush any unsent messages
        self.producer.flush()

        # Close the status producer
        if self.status_updater:
            self.status_updater.close()

        # Close the producer if using kafka python
        if self.load_kafka_python:
            self.producer.close()
