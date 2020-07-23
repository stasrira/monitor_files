import os
import time
from datetime import datetime, timedelta
import traceback
from utils import ConfigData
from utils import Watcher
import shutil

class Monitor():
    def __init__(self, cfg_monitor_path, log_obj, error_obj = None):
        self.mtr_cfg_path = cfg_monitor_path
        self.log = log_obj
        self.error = error_obj #TODO: implement error handling
        self.mtr_cfg = ConfigData(cfg_monitor_path)
        if self.validate_config_file():
            self.loaded = True
        else:
            self.loaded = False

        # get config file values
        self.mtr_source = self.mtr_cfg.get_value('Location/source')
        self.mtr_destin = self.mtr_cfg.get_value('Location/destination')
        self.mtr_item = self.mtr_cfg.get_value('Monitoring/item')
        self.mtr_type = self.mtr_cfg.get_value('Monitoring/type')
        self.mtr_action = self.mtr_cfg.get_value('Monitoring/action')
        self.mtr_frequency = self.mtr_cfg.get_value('Monitoring/frequency')
        self.mtr_email = self.mtr_cfg.get_value('Monitoring/email_notification')
        self.mtr_email_cc = self.mtr_cfg.get_value('Monitoring/email_cc')
        self.mtr_sync_date = self.mtr_cfg.get_value('Last_sync/date_time')
        self.mtr_watch_value = self.mtr_cfg.get_value('Last_sync/watch_value')

    def validate_config_file(self):
        # TODO: add some rules to validate the current monitoring config file
        return True

    def start_monitor(self):
        # check if delay between monitoring events was fulfilled
        if self.mtr_sync_date and isinstance(self.mtr_sync_date, datetime) and self.mtr_frequency.isnumeric():
            next_sync_datetime = self.mtr_sync_date + timedelta(seconds=self.mtr_frequency)
        else:
            next_sync_datetime = None

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
            watcher = Watcher(self.mtr_source, custom_action, self.mtr_item, self.mtr_type)
            watcher.watch()  # start the watch going
        else:
            self.log.info('Monitoring delay of "{}" seconds has not expired since the last syncronization event on {}. '
                          .format(self.mtr_frequency if self.mtr_frequency else 'N/A',
                                  self.mtr_sync_date if self.mtr_sync_date else 'N/A'
                                  )
                          )

    def action_copy(self, file_time_stamp):
        self.log.info('Start copying "{}" to "{}"'.format(self.mtr_source, self.mtr_destin))
        try:
            shutil.copy(self.mtr_source, self.mtr_destin)
            self.log.info('Copying process completed successfuly.')

            # update stats in the config file
            # time.strftime("%Y%m%d_%H%M%S", time.localtime())
            self.mtr_cfg.set_value(time.localtime(), 'Last_sync/date_time')
            self.mtr_cfg.set_value(file_time_stamp, 'Last_sync/watch_value')

            if self.mtr_email:
                #TODO: implement sending email
                pass


        except Exception as ex:
            # report unexpected error to log file
            _str = 'Unexpected Error "{}" occurred during copying file "{}" to "{}"\n{} ' \
                .format(ex, self.mtr_source, self.mtr_destin, traceback.format_exc())
            self.log.error(_str)
            #TODO: report error here

