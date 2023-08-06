import pytest
import os
import time
from concurrent.futures import ThreadPoolExecutor
from confluent_kafka.admin import AdminClient, NewTopic
from pathlib import Path
from igwn_lldd_common.framekafkaproducer import FrameKafkaProducer
from igwn_lldd_common.framekafkaconsumer import FrameKafkaConsumer
from igwn_lldd_common.utils import parse_topics

# Some useful constants
CONSUMER_TIMEOUT = 60
CONFLUENT_KAFKA_TOPIC = "TestFrameConfluent"
CONFLUENT_KAFKA_STATUS_TOPIC = "TestStatusConfluentSingle"
KAFKA_PYTHON_TOPIC = "TestFrameKafka"
KAFKA_PYTHON_STATUS_TOPIC = "TestStatusKafkaSingle"
TEST_DATA_DIR = Path(__file__).parent / 'data'
TEST_GWF_FILE = TEST_DATA_DIR / 'Z-igwn_lldd_common_test-1000000000-1.gwf'

# Read the data from the frame file
with open(TEST_GWF_FILE, "rb") as f:
    FRAME_DATA = f.read()


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def frame_kafka_consumer_kafka_python():

    # Specify the args to setup the producer
    args = AttrDict()
    args.debug = 0
    args.debug_wait = 0.0
    args.bootstrap_servers = os.getenv("KAFKA_BROKER")
    args.add_topic_partition = [f"/topic={KAFKA_PYTHON_TOPIC}/delta-t=1/"]
    args.exit_if_missing_topics = False
    args.ssl = False
    args.group_id = None
    args.fast_forward = True
    args.poll_timeout = 1000
    args.poll_max_records = 1
    args.verbose = True
    args.status_updates = True
    args.status_topic = KAFKA_PYTHON_STATUS_TOPIC
    args.status_bootstrap = None
    args.status_nodename = None
    args.load_kafka_python = True

    # Get the topics from the topic partition
    tp_info = parse_topics(args.add_topic_partition)

    # Setup the frame kafka consumer
    framekafkaconsumer = FrameKafkaConsumer(args, tp_info)

    # Mark the last time a frame should of been recieved
    tp_info[KAFKA_PYTHON_TOPIC]["last_time"] = 999999999

    # Start the timer
    start = time.time()

    # Set a empty frame buffer to track if frame has been recieved
    frame_buffer = ""

    # Loop until all messaged have been recieved and the
    # frame is complete or is timed out
    while not frame_buffer:

        # Run consumer.poll()
        r_poll = framekafkaconsumer.poll_consumer_for_topic()

        # Check if the recieve has taken too long
        if time.time() - start > CONSUMER_TIMEOUT:
            framekafkaconsumer.close()
            raise SystemExit("It has taken too long to recieve the frame")

        # Check if the poll contains messages
        if len(r_poll) == 0:
            continue

        # parse the messages
        for topic_partition in r_poll:
            for message in r_poll[topic_partition]:

                # Get the frame buffer from the kafka messgae
                (
                    frame_buffer,
                    payload_info,
                ) = framekafkaconsumer.extract_frame_buffer_from_message(
                    message, tp_info
                )

    # Check what was recieved is the same as what was sent
    assert frame_buffer == FRAME_DATA, \
        "The recieved frame is not the same as the sent frame"

    # Close the consumer
    framekafkaconsumer.close()


@pytest.mark.skipif(
    os.getenv("KAFKA_BROKER") is None,
    reason="There is not a active Kafka Broker"
)
def test_kafka_python_single():

    # Create an executor to run the consumer
    executor = ThreadPoolExecutor(max_workers=1)

    # Submit the consumer in the executor
    future = executor.submit(frame_kafka_consumer_kafka_python)

    # Wait 5 seconds for the consumer to startup
    time.sleep(5)

    # Specify the args to setup the producer
    args = AttrDict()
    args.debug = 0
    args.bootstrap_servers = os.getenv("KAFKA_BROKER")
    args.verbose = True
    args.split_bytes = 1000
    args.topic = KAFKA_PYTHON_TOPIC
    args.crc_check = False
    args.batch_size = 16384
    args.buffer_memory = 33554432
    args.linger_ms = 0
    args.acks = 1
    args.min_interval = -1
    args.status_updates = True
    args.status_topic = KAFKA_PYTHON_STATUS_TOPIC
    args.status_bootstrap = None
    args.status_nodename = None
    args.delta_t = 1
    args.load_kafka_python = True

    # Setup the fame kafka producer using the arguments
    framekafkaproducer = FrameKafkaProducer(args)

    # Set the timestamp
    timestamp = 1000000000

    # Attempt to send the frame
    framekafkaproducer.send_frame(FRAME_DATA, timestamp)

    # Close the frame kafka producer
    framekafkaproducer.close()

    # Wait for the consumer to finish and get the result
    result = future.result()

    # Check if the consumer exited normally
    if result is not None:
        raise SystemExit("The consumer exited abnormally")

    # Shutdown the executor
    executor.shutdown()


def frame_kafka_consumer_confluent_kafka():

    # Specify the args to setup the producer
    args = AttrDict()
    args.debug = 0
    args.debug_wait = 0.0
    args.bootstrap_servers = os.getenv("KAFKA_BROKER")
    args.add_topic_partition = [f"/topic={CONFLUENT_KAFKA_TOPIC}/delta-t=1/"]
    args.exit_if_missing_topics = False
    args.ssl = False
    args.group_id = None
    args.fast_forward = True
    args.poll_timeout = 1000
    args.poll_max_records = 1
    args.verbose = True
    args.status_updates = True
    args.status_topic = KAFKA_PYTHON_STATUS_TOPIC
    args.status_bootstrap = None
    args.status_nodename = None
    args.load_kafka_python = False

    # Get the topics from the topic partition
    tp_info = parse_topics(args.add_topic_partition)

    # Setup the frame kafka consumer
    framekafkaconsumer = FrameKafkaConsumer(args, tp_info)

    # Mark the last time a frame should of been recieved
    tp_info[CONFLUENT_KAFKA_TOPIC]["last_time"] = 999999999

    # Start the timer
    start = time.time()

    # Set a empty frame buffer to track if frame has been recieved
    frame_buffer = ""

    # Loop until all messaged have been recieved and the
    # frame is complete or is timed out
    while not frame_buffer:

        # Run consumer.poll()
        r_poll = framekafkaconsumer.poll_consumer_for_topic()

        # Check if the recieve has taken too long
        if time.time() - start > CONSUMER_TIMEOUT:
            framekafkaconsumer.close()
            raise SystemExit("It has taken too long to recieve the frame")

        # Check if the poll contains messages
        if len(r_poll) == 0:
            continue

        # parse the messages
        for topic_partition in r_poll:
            for message in r_poll[topic_partition]:

                # Get the frame buffer from the kafka messgae
                (
                    frame_buffer,
                    payload_info,
                ) = framekafkaconsumer.extract_frame_buffer_from_message(
                    message, tp_info
                )

    # Check what was recieved is the same as what was sent
    assert frame_buffer == FRAME_DATA, \
        "The recieved frame is not the same as the sent frame"

    # Close the consumer
    framekafkaconsumer.close()


@pytest.mark.skipif(
    os.getenv("KAFKA_BROKER") is None,
    reason="There is not a active Kafka Broker"
)
def test_confluent_kafka_single():

    # For confluent kafka first we need to create the topic before
    # producing messages to the topic otherwise the kafka topic
    # will not be created properly and seems to hang
    admin_client = AdminClient({
        "bootstrap.servers": os.getenv("KAFKA_BROKER")
    })

    # Initialize a new topic
    topic = NewTopic(CONFLUENT_KAFKA_TOPIC, 1, 1)

    # Create the topic in the broker
    admin_client.create_topics([topic])

    # Create an executor to run the consumer
    executor = ThreadPoolExecutor(max_workers=1)

    # Submit the consumer in the executor
    future = executor.submit(frame_kafka_consumer_confluent_kafka)

    # Wait 5 seconds for the consumer to startup
    time.sleep(5)

    # Specify the args to setup the producer
    args = AttrDict()
    args.debug = 0
    args.bootstrap_servers = os.getenv("KAFKA_BROKER")
    args.verbose = True
    args.split_bytes = 1000
    args.topic = CONFLUENT_KAFKA_TOPIC
    args.crc_check = False
    args.batch_size = 16384
    args.buffer_memory = 33554432
    args.linger_ms = 0
    args.acks = 1
    args.min_interval = -1
    args.status_updates = True
    args.status_topic = KAFKA_PYTHON_STATUS_TOPIC
    args.status_bootstrap = None
    args.status_nodename = None
    args.delta_t = 1
    args.load_kafka_python = False

    # Setup the fame kafka producer using the arguments
    framekafkaproducer = FrameKafkaProducer(args)

    # Set the timestamp
    timestamp = 1000000000

    # Attempt to send the frame
    framekafkaproducer.send_frame(FRAME_DATA, timestamp)

    # Close the frame kafka producer
    framekafkaproducer.close()

    # Wait for the consumer to finish and get the result
    result = future.result()

    # Check if the consumer exited normally
    if result is not None:
        raise SystemExit("The consumer exited abnormally")

    # Shutdown the executor
    executor.shutdown()
