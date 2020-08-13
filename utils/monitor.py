import os
from pathlib import Path
import time
from datetime import datetime, timedelta
import traceback
from utils import ConfigData, Watcher, common as cm, global_const as gc
# from utils import Watcher
import shutil

class Monitor():
    def __init__(self, cfg_monitor_path, log_obj, error_obj = None):
        self.mtr_cfg_path = cfg_monitor_path
        self.log = log_obj
        self.error = error_obj  #TODO: implement error handling
        self.mtr_cfg = ConfigData(cfg_monitor_path)
        if self.validate_config_file():
            self.loaded = True
        else:
            self.loaded = False
        cur_cfg_dir = os.path.dirname(cfg_monitor_path)
        cur_cfg_file_name = Path(os.path.abspath(cfg_monitor_path)).name
        stamp_dir = Path(str(cur_cfg_dir) + '/' + gc.STAMPS_FILES_FOLDER_NAME)
        if not os.path.exists(stamp_dir):
            os.mkdir(stamp_dir)
        stamp_file = Path(str(stamp_dir) + '/' + cur_cfg_file_name.replace('.yaml', '_stamp.yaml'))
        self.verify_config_stamp_file(stamp_file)
        self.mtr_cfg_stamp = ConfigData(stamp_file)

        if self.loaded:
            # get config file values
            self.mtr_source_dir = self.mtr_cfg.get_value('Location/source_dir')
            self.mtr_source_file = self.mtr_cfg.get_value('Location/source_file')
            found_file = cm.find_file_in_dir(self.mtr_source_dir, self.mtr_source_file)
            if found_file:
                self.mtr_source = found_file[0]
                self.mtr_source_path = Path(self.mtr_source_dir) / self.mtr_source
            else:
                self.mtr_source = None
                self.mtr_source_path = None
            self.mtr_destin = self.mtr_cfg.get_value('Location/destination')
            self.mtr_item = self.mtr_cfg.get_value('Monitoring/item')
            self.mtr_type = self.mtr_cfg.get_value('Monitoring/type')
            self.mtr_action = self.mtr_cfg.get_value('Monitoring/action')
            self.mtr_frequency = self.mtr_cfg.get_value('Monitoring/frequency')
            self.mtr_email = self.mtr_cfg.get_value('Monitoring/email_notification')
            self.mtr_email_cc = self.mtr_cfg.get_value('Monitoring/email_cc')
            # load stamp info from stamp config file
            self.mtr_sync_date = self.mtr_cfg_stamp.get_value('Last_sync/date_time')
            self.mtr_watch_value = self.mtr_cfg_stamp.get_value('Last_sync/watch_value')

    def verify_config_stamp_file(self, file_path):
        if not cm.file_exists(file_path):
            # if file is not present, create it
            f = open(file_path, "w+")
            f.close


    def validate_config_file(self):
        # TODO: add some rules to validate the current monitoring config file
        return True

    def start_monitor(self):

        if self.mtr_source_path:
            # check if delay between monitoring events was fulfilled
            if self.mtr_sync_date and isinstance(self.mtr_sync_date, datetime) and self.mtr_frequency.isnumeric():
                next_sync_datetime = self.mtr_sync_date + timedelta(seconds=self.mtr_frequency)
            else:
                next_sync_datetime = None  # datetime.now() - + timedelta(seconds=1)

            if not next_sync_datetime or next_sync_datetime < datetime.now():
                self.log.info('Monitoring delay of "{}" seconds has expired since the last syncronization event on {}. '
                              'Proceeding to monitor "{}" file'
                              .format(self.mtr_frequency if self.mtr_frequency else 'N/A',
                                      self.mtr_sync_date if self.mtr_sync_date else 'N/A',
                                      self.mtr_source
                                      )
                              )
                custom_action = self.action_copy # set default value
                if self.mtr_action == 'copy':
                    custom_action = self.action_copy
                watcher = Watcher(self.mtr_source_path, custom_action, self.mtr_item, self.mtr_type)
                watcher.watch()  # start the watch going
            else:
                self.log.info('Monitoring delay of "{}" seconds has not expired since the last syncronization event on {}. '
                              .format(self.mtr_frequency if self.mtr_frequency else 'N/A',
                                      self.mtr_sync_date if self.mtr_sync_date else 'N/A'
                                      )
                              )
        else:
            self.log.warning('Source file "{}" was not found in the source directory "{}". '
                          .format(self.mtr_source_file, self.mtr_source_dir))

    def action_copy(self, file_time_stamp):
        self.log.info('Start copying "{}" to "{}"'.format(self.mtr_source, self.mtr_destin))
        try:
            shutil.copy(self.mtr_source_path, self.mtr_destin)
            self.log.info('Copying process completed successfuly.')

            # update stats in the config file
            # time.strftime("%Y%m%d_%H%M%S", time.localtime())
            self.mtr_cfg_stamp.set_value(time.strftime("%Y%m%d_%H%M%S", time.localtime()), 'Last_sync/date_time')
            self.mtr_cfg_stamp.set_value(file_time_stamp, 'Last_sync/watch_value')

            if self.mtr_email:
                #TODO: implement sending email
                pass

        except Exception as ex:
            # report unexpected error to log file
            _str = 'Unexpected Error "{}" occurred during copying file "{}" to "{}"\n{} ' \
                .format(ex, self.mtr_source, self.mtr_destin, traceback.format_exc())
            self.log.error(_str)
            #TODO: report error here

