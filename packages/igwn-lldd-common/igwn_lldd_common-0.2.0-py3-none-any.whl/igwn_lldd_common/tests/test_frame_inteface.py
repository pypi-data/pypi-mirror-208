import multiprocessing as mp
import os
from igwn_lldd_common.frame2kafka import main as frame2kafka
from igwn_lldd_common.kafka2frame import main as kafka2frame
from pathlib import Path
import tempfile
import shutil
import time
import filecmp
import logging
import pytest

logging.basicConfig(level=logging.DEBUG)

KAFKA_TOPIC = "TestTopic"
TEST_DATA_DIR = Path(__file__).parent / 'data'
TEST_GWF_FILES = [
    'Z-igwn_lldd_common_test-1000000000-1.gwf',
    'Z-igwn_lldd_common_test-1000000001-1.gwf',
    'Z-igwn_lldd_common_test-1000000002-1.gwf'
]
PRODUCER_RUNTIME = 5
OBSERVATORY = "Z"


@pytest.mark.skipif(
    os.getenv("KAFKA_BROKER") is None,
    reason="There is not a active Kafka Broker"
)
def test_frame2kafka():

    # Enable the coverage info to be collected from multiprocessing process
    try:
        from pytest_cov.embed import cleanup_on_sigterm
    except ImportError:
        pass
    else:
        cleanup_on_sigterm()

    with tempfile.TemporaryDirectory() as indirname:
        with tempfile.TemporaryDirectory() as outdirname:

            consumer_args = [
                "--bootstrap-servers", os.getenv("KAFKA_BROKER"),
                "--frame-dir", outdirname,
                "--obs", OBSERVATORY,
                "--add-topic-partition", f"/topic={KAFKA_TOPIC}/delta-t=1/",
                "--debug", "1",
                "--max-runtime", "30",
                "--load-kafka-python"
            ]

            # Setup the consumer using the frame2kafka script
            consumer = mp.Process(target=kafka2frame, args=(consumer_args,))

            # Start the consumer
            consumer.start()

            time.sleep(5)

            producer_args = [
                "--bootstrap-servers", os.getenv("KAFKA_BROKER"),
                "--frame-directory", indirname,
                "--topic", KAFKA_TOPIC,
                "--verbose", "True",
                "--max-runtime", "20",
                "--load-kafka-python"
            ]

            # Setup the producer using the frame2kafka script
            producer = mp.Process(target=frame2kafka, args=(producer_args,))

            # Start the producer
            producer.start()

            # Allow the producer to startup before writing frames
            time.sleep(5)

            # Loop over each of the test files reading them and
            # writing them to the tmp directory so they can be picked
            # up by the frame2kafka process
            for ifile in TEST_GWF_FILES:

                # Copy the file to the dest directory so it can be picked
                # up by the producer
                inputfile = TEST_DATA_DIR / ifile
                destfile = os.path.join(indirname, ifile)

                # Copy the file
                shutil.copyfile(inputfile, destfile)

                # Wait 1 second so the file comes in every 1 second
                time.sleep(1)

            # Wait for the producer to stop
            producer.join()

            # Wait for the consumer to stop
            consumer.join()

            print(os.listdir(indirname))
            print(os.listdir(outdirname))

            for ifile in TEST_GWF_FILES:

                # Set the filenames to check the file contents
                infile = os.path.join(indirname, ifile)
                ofile = ifile.replace(
                    "Z-igwn_lldd_common_test",
                    f"{OBSERVATORY}-{KAFKA_TOPIC}"
                )
                outfile = os.path.join(outdirname, ofile)

                # Check that the infile and outfile
                assert os.path.exists(infile), f"The copy of {infile} failed"
                assert os.path.exists(outfile), "The consumer did not " \
                    f"write {outfile}"

                # Compare the contents of the generated files
                assert filecmp.cmp(infile, outfile), "The contents for " \
                    f"the {infile} and {outfile} do not match"
