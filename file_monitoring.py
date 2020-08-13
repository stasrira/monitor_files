import os
import sys
import time
from os import walk
import getpass
from pathlib import Path
import traceback
import shutil
from utils import Monitor
from utils import ConfigData, common as cm, global_const as gc, send_email as email

# if executed by itself, do the following
if __name__ == '__main__':

    gc.CURRENT_PROCCESS_LOG_ID = 'monitor_file'
    # load main config file and get required values
    m_cfg = ConfigData(gc.MAIN_CONFIG_FILE)

    # m_cfg.set_value('Test123', 'Test/Stas1/Stas2')

    # setup application level logger
    cur_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    mlog = cm.setup_logger(m_cfg, cur_dir, gc.CURRENT_PROCCESS_LOG_ID)
    monitor_path = m_cfg.get_value('Location/monitor_configs')

    # Verify that target directory (df_path) is accessible for the current user (under which the app is running)
    # Identify the user under which the app is running if the df_path is not accessible
    if not os.path.exists(monitor_path):
        mlog.error('Directory "{}" does not exist or not accessible for the current user. Aborting execution. '
                   'Expected user login: "{}", Effective user: "{}"  '.format(monitor_path, os.getlogin(),
                                                                              getpass.getuser()))
        exit(1)

    try:

        (_, _, monitor_files) = next(walk(monitor_path))
        # print('Study dirs: {}'.format(dirstudies))

        mlog.info('The following monitor request(s) are to be processed (count = {}): {}'.format(len(monitor_files), monitor_files))

        for mnt_config in monitor_files:
            mnt = Monitor(Path(monitor_path) / mnt_config, mlog, None)  #TODO: pass error object instead of None
            mnt.start_monitor()

    except Exception as ex:
        # report unexpected error to log file
        _str = 'Unexpected Error "{}" occurred during processing file: {}\n{} '\
            .format(ex, os.path.abspath(__file__), traceback.format_exc())
        mlog.critical(_str)
        raise

    sys.exit()