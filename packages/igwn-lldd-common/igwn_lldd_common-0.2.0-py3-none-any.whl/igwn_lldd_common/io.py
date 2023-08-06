import os
import logging
import shutil

logger = logging.getLogger()

try:
    from watchdog.events import PatternMatchingEventHandler

    class FrameFileEventHandler(PatternMatchingEventHandler):
        """docstring for ClassName"""

        def __init__(self, queue):
            super().__init__(patterns=["*.gwf", "*.hdf5", "*.h5"])
            self.queue = queue

        def on_created(self, event):

            if event.is_directory:
                return

            self.queue.put(event.src_path)

except ImportError:
    import threading
    from inotify_simple import INotify, flags

    # Thread to watch over watch_dir
    def monitor_dir_inotify(queue, watch_dir):

        # create a watcher thread watching for write or moved events
        i = INotify()
        i.add_watch(watch_dir, flags.CLOSE_WRITE | flags.MOVED_TO)

        # Get the current thread
        t = threading.currentThread()

        # Check if this thread should stop
        while not t.stop:

            # Loop over the events and check when a file has been created
            for event in i.read(timeout=1):

                # directory was removed, so the corresponding watch was
                # also removed
                if flags.IGNORED in flags.from_mask(event.mask):
                    break

                # ignore temporary files
                filename = event.name
                extension = os.path.splitext(filename)[1]
                if extension != ".gwf":
                    continue

                # Add the filename to the queue
                queue.put(os.path.join(watch_dir, filename))

        # Remove the watch
        i.rm_watch(watch_dir)


def write_frame(file_name, frame_data, fl_ringn, file_name_dq, tmpdir=None):
    # determine temporary filename/directory
    if tmpdir:
        file = os.path.basename(file_name)
    else:
        tmpdir, file = os.path.split(file_name)
    tmp_file_name = os.path.join(tmpdir, f".{file}.tmp")

    # write frame to disk
    # NOTE: this is atomic if on the same filesystem
    with open(tmp_file_name, "wb") as f:
        f.write(frame_data)
        # ensure all data is on disk
        f.flush()
        os.fsync(f.fileno())
    shutil.move(tmp_file_name, file_name)

    #
    # ring of frame_log files?
    if fl_ringn:
        #
        # name queue full?
        if len(file_name_dq) == fl_ringn:
            old_file = file_name_dq.popleft()
            try:
                os.unlink(old_file)
            except OSError:
                logger.error(
                    f"Error: could not delete file [{old_file}]"
                )

        #
        # add this file to queue
        file_name_dq.append(file_name)
