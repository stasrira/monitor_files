import os
import sys
import time
from pathlib import Path
import traceback
import shutil
from utils import Watcher

# Call this function each time a change happens
def custom_action(text):
    print(text)
    try:
        shutil.copy(watch_file, target_copy_to_file)
    except Exception as ex:
        # report unexpected error to log file
        _str = 'Unexpected Error "{}" occurred during processing file: {}\n{} '\
            .format(ex, os.path.abspath(__file__), traceback.format_exc())
        print(_str)
    print('Copying operation completed.')

watch_file = Path('D:\MounSinai\Darpa\Programming\monitor_files\data_file_examples\source\LAB24_SQL_test1.xlsx')
# target_copy_to_file = Path('D:\MounSinai\Darpa\Programming\monitor_files\data_file_examples\\target')
target_copy_to_file = Path('D:\MounSinai\Darpa\Programming\monitor_files\data_file_examples\\target\LAB24_SQL_test_{}.xlsx'.format(time.strftime("%Y%m%d_%H%M%S", time.localtime())))

# watcher = Watcher(watch_file)  # simple
watcher = Watcher(watch_file, custom_action, text='yes, changed')  # also call custom action function
watcher.watch()  # start the watch going