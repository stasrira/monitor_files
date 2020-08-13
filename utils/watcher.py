import os
import traceback
import sys
import time

class Watcher(object):
    running = True
    refresh_delay_secs = 60

    # Constructor
    def __init__(self, watch_file, call_func_on_change=None, *args, **kwargs):
        self._cached_stamp = 0
        self.filename = watch_file
        self.call_func_on_change = call_func_on_change
        self.args = args
        self.kwargs = kwargs

    # Look for changes
    def look(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            # File has changed, so do something...
            # print('File changed')
            # TODO: add log here
            if self.call_func_on_change is not None:
                self.call_func_on_change(self._cached_stamp)
            self.running = False

    # Keep watching in a loop
    def watch(self):
        # while self.running:
        try:
            # Look for changes
            # time.sleep(self.refresh_delay_secs)
            self.look()
        except KeyboardInterrupt:
            print('\nDone')
            # break
        except FileNotFoundError:
            # Action on file not found
            # TODO: Add log info about not found file
            # self.running = False
            pass
        # except:
        #    print('Unhandled error: %s' % sys.exc_info()[0])
        except Exception as ex:
            # report unexpected error to log file
            _str = 'Unexpected Error "{}" occurred during watching the file: {}\n{} ' \
                .format(ex, self.filename, traceback.format_exc())
            print (_str)
            # mlog.critical(_str)
            raise
