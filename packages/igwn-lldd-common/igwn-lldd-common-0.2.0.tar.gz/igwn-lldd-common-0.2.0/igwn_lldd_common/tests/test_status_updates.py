from igwn_lldd_common.statustopic import StatusUpdater
import confluent_kafka
import kafka
import os
import pytest
import json
import time


CONFLUENT_TOPIC = "TestStatusConfluent"
KAFKA_TOPIC = "TestStatusKafka"


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


@pytest.mark.skipif(
    os.getenv("KAFKA_BROKER") is None,
    reason="There is not a active Kafka Broker"
)
def test_status_updater_confluent_kafka():

    # Generate a attribute dictionary
    args = AttrDict()
    args.load_kafka_python = False
    args.status_bootstrap = os.getenv("KAFKA_BROKER")
    args.status_topic = CONFLUENT_TOPIC
    args.status_nodename = None

    # Initialise the status updated
    statusupdater = StatusUpdater(args)

    # Create dummy data to send
    test_info = {"one": 1, "two": 2}

    # Send the status update
    statusupdater.send_status_update("test", test_info)

    # Close the status updater producer
    statusupdater.close()


@pytest.mark.skipif(
    os.getenv("KAFKA_BROKER") is None,
    reason="There is not a active Kafka Broker"
)
def test_consume_status_confluent_kafka():

    # Setup the consumer
    consumer = confluent_kafka.Consumer(
        {
            "bootstrap.servers": os.getenv("KAFKA_BROKER"),
            "group.id": "my_unmanaged_group",
            "auto.offset.reset": "latest",
        }
    )

    # Assign to the beginning of the topic
    consumer.assign(
        [
            confluent_kafka.TopicPartition(
                CONFLUENT_TOPIC, 0, confluent_kafka.OFFSET_BEGINNING
            )
        ]
    )

    # Poll consumer for topic and wait maxium 10 seconds
    r_poll = consumer.consume(timeout=10)

    # Check if recieved the message
    assert len(r_poll) > 0, "No Kafka message found"

    # Extract payload from r_poll
    message = r_poll[0]

    # Check for any errors and exit if there are
    if message.error():
        pytest.exit(message.error())

    # Extract the message payload and topic
    payload = message.value()
    topic = message.topic()

    # Double check the correct topic was consumed
    assert topic == CONFLUENT_TOPIC, "Error: wrong topic was consumed"

    # Check to see if the payload is empty
    assert len(payload) != 0, "Payload is empty"

    # Decode the payload
    status = json.loads(payload)

    # Check the values in the message
    if "status" in status.keys():
        assert status["status"] == "test", \
            "The status is incorrect in the message"
    else:
        pytest.exit("The 'status' key was not in the status message")

    # Check the values in the message
    if "one" in status.keys():
        assert status["one"] == 1, \
            "The entry for the one key is incorrect in the message"
    else:
        pytest.exit("The 'one' key was not in the status message")

    # Check the values in the message
    if "two" in status.keys():
        assert status["two"] == 2, \
            "The entry for the two key is incorrect in the message"
    else:
        pytest.exit("The 'two' key was not in the status message")


@pytest.mark.skipif(
    os.getenv("KAFKA_BROKER") is None,
    reason="There is not a active Kafka Broker"
)
def test_status_updater_kafka_python():

    # Generate a attribute dictionary
    args = AttrDict()
    args.load_kafka_python = True
    args.status_bootstrap = os.getenv("KAFKA_BROKER")
    args.status_topic = KAFKA_TOPIC
    args.status_nodename = None

    # Initialise the status updated
    statusupdater = StatusUpdater(args)

    # Create dummy data to send
    test_info = {"one": 1, "two": 2}

    # Send the status update
    statusupdater.send_status_update("test", test_info)

    # Close the status updater producer
    statusupdater.close()


@pytest.mark.skipif(
    os.getenv("KAFKA_BROKER") is None,
    reason="There is not a active Kafka Broker"
)
def test_consume_status_kafka_python():

    # Setup the consumer
    consumer = kafka.KafkaConsumer(
        bootstrap_servers=os.getenv("KAFKA_BROKER")
    )

    # Get the topic partitions
    topic_partitions = consumer.partitions_for_topic(KAFKA_TOPIC)

    # Check if the 0th partition is in the topic
    if 0 not in topic_partitions:
        pytest.exit(f"Could not find partition 0 of topic {KAFKA_TOPIC}")

    # Get the topic partition
    topic_partition = kafka.TopicPartition(KAFKA_TOPIC, 0)

    # Assign to the beginning of the topic
    consumer.assign([topic_partition])

    # Seek to the beginning of the topic:
    consumer.seek_to_beginning(topic_partition)

    # Poll consumer for topic and wait maxium 10 seconds
    r_poll = consumer.poll(timeout_ms=10000)

    # Check if recieved the message
    assert len(r_poll) > 0, "No Kafka message found"

    # Get the first message in the r_poll
    first_key = list(r_poll.keys())[0]

    # Get the first record
    record = r_poll[first_key]

    # Check if recieved the message
    assert len(record) > 0, "No Kafka record found"

    # Extract payload from r_poll
    message = record[0]

    # Extract the message payload and topic
    payload = message.value
    topic = message.topic

    # Double check the correct topic was consumed
    assert topic == KAFKA_TOPIC, "Error: wrong topic was consumed"

    # Decode the payload
    status = json.loads(payload)

    # Check the values in the message
    if "status" in status.keys():
        assert status["status"] == "test", \
            "The status is incorrect in the message"
    else:
        pytest.exit("The 'status' key was not in the status message")

    # Check the values in the message
    if "one" in status.keys():
        assert status["one"] == 1, \
            "The entry for the one key is incorrect in the message"
    else:
        pytest.exit("The 'one' key was not in the status message")

    # Check the values in the message
    if "two" in status.keys():
        assert status["two"] == 2, \
            "The entry for the two key is incorrect in the message"
    else:
        pytest.exit("The 'two' key was not in the status message")


@pytest.mark.skipif(
    os.getenv("KAFKA_BROKER") is None,
    reason="There is not a active Kafka Broker"
)
def test_status_topic_types():

    # Generate a attribute dictionary
    args = AttrDict()
    args.load_kafka_python = True
    args.status_bootstrap = os.getenv("KAFKA_BROKER")
    args.status_topic = KAFKA_TOPIC
    args.status_nodename = None

    # Get the current time
    linux_time = time.time()

    # Initialise the status updated
    statusupdater = StatusUpdater(args)

    # Send resume status

    # Create resume data
    test_info = {
        "topic": "TEST_TOPIC",
        "linux_now": linux_time,
        "data_gps_timestamp": 1000000000,
        "last_time": 999999999,
        "frame_duration": 1
    }

    # Send the status update
    statusupdater.send_status_update("resume", test_info)

    # Send olds status

    # Create old data
    test_info["lost_duration"] = 3

    # Send the status update
    statusupdater.send_status_update("old", test_info)

    # Send fast_forward status

    # Create fast_foward data
    test_info["fast_forward_to_timestamp"] = linux_time + 5.0

    # Send the status update
    statusupdater.send_status_update("fast_foward", test_info)

    # Send missing status

    # Send the status update
    statusupdater.send_status_update("missing", test_info)

    # Send missing status

    # Create replay data
    test_info["replay_duration"] = 48

    # Send the status update
    statusupdater.send_status_update("replay", test_info)

    # Close the status updater producer
    statusupdater.close()
