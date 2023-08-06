# -*- coding: utf-8 -*-
# Copyright (C) European Gravitational Observatory (2022)
#
# Author: Rhys Poulton <poulton@ego-gw.it>
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

# Code for getting the name of this host/node
import socket
import json
import logging

logger = logging.getLogger(__name__)


class StatusUpdater:
    def __init__(self, args):

        self.load_kafka_python = args.load_kafka_python

        if args.load_kafka_python:
            from kafka import KafkaProducer
            from kafka.errors import KafkaError
        else:
            from confluent_kafka import Producer, KafkaException

        if args.status_bootstrap:
            status_bootstrap = args.status_bootstrap.split(",")
        else:
            status_bootstrap = args.bootstrap_servers.split(",")

        if args.status_topic:
            self.status_topic = args.status_topic
        else:
            self.status_topic = "status-" + args.topic

        max_tries = 10
        tries = max_tries
        prod_connected = False
        update_prod_args = {}
        while not prod_connected and tries > 0:
            if self.load_kafka_python:
                try:
                    self.status_producer = KafkaProducer(
                        bootstrap_servers=status_bootstrap, **update_prod_args
                    )
                except KafkaError:
                    pass
                else:
                    prod_connected = True
            else:
                try:
                    self.status_producer = Producer(
                        {"bootstrap.servers": ",".join(status_bootstrap)}
                    )
                except KafkaException:
                    pass
                else:
                    prod_connected = True

            tries = tries - 1
            if tries == 0:
                logger.warn(
                    "Unable to create status producer after %d attempts a \
tp connect to [%s]\n"
                    % (max_tries, status_bootstrap)
                )

        logger.info(
            "Updating status to [%s] under topic [%s]\n"
            % (status_bootstrap, self.status_topic)
        )

        # information to pass to status dict
        if not args.status_nodename:
            self.node = socket.gethostname()
        else:
            self.node = args.status_nodename

    def send_status_update(self, status, payload_info):

        status_dict = payload_info.copy()
        status_dict["status"] = status
        status_dict["node"] = self.node

        if status == "old":
            status_dict["lost_duration"] = (
                status_dict["data_gps_timestamp"] - status_dict["last_time"]
            )
        elif status == "fast_forward":
            status_dict["fast_forward_to_timestamp"] = (
                status_dict["linux_now"] + status_dict["fast_forward_buffer"]
            )
            status_dict["lost_duration"] = (
                status_dict["data_gps_timestamp"] - status_dict["last_time"]
            )
        elif status == "missing":
            status_dict["lost_duration"] = (
                status_dict["data_gps_timestamp"] - status_dict["last_time"]
            )
        elif status == "replay":
            status_dict["lost_duration"] = (
                status_dict["data_gps_timestamp"] - status_dict["last_time"]
            )
            status_dict["replay_duration"] = (
                status_dict["last_time"]
                + status_dict["frame_duration"]
                - status_dict["data_gps_timestamp"]
            )

        status = json.dumps(status_dict).encode("utf-8")
        if self.load_kafka_python:
            self.status_producer.send(
                self.status_topic,
                status,
            )
        else:
            self.status_producer.produce(
                self.status_topic,
                status,
            )

        # Add flush to status producer
        self.status_producer.flush()

    def close(self):

        # flush any unsent messages
        self.status_producer.flush()

        # Close the status producer if using kafka python
        if self.load_kafka_python:
            self.status_producer.close()
