import os
import sys
from os import walk
import getpass
from pathlib import Path
import traceback
from utils import Monitor
from utils import ConfigData, common as cm, common2 as cm2, global_const as gc, send_yagmail #, send_email as email


# if executed by itself, do the following
if __name__ == '__main__':

    gc.CURRENT_PROCCESS_LOG_ID = 'monitor_file'
    # load main config file and get required values
    m_cfg = ConfigData(gc.MAIN_CONFIG_FILE)

    # setup application level logger
    cur_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    mlog, log_handler = cm.setup_logger(m_cfg, cur_dir, gc.CURRENT_PROCCESS_LOG_ID)
    monitor_path = m_cfg.get_value('Location/monitor_configs')

    # Verify that target directory (df_path) is accessible for the current user (under which the app is running)
    # Identify the user under which the app is running if the df_path is not accessible
    if not os.path.exists(monitor_path):
        _str = 'Directory "{}" does not exist or not accessible for the current user. Aborting execution. ' \
               'Expected user login: "{}", Effective user: "{}"'.format(monitor_path, os.getlogin(),getpass.getuser())
        mlog.error(_str)

        # send notification email alerting about the error case
        email_subject = 'Error occurred during running file_monitoring tool.'
        email_body = 'The following error caused interruption of execution of the application<br/>' \
                     + str(Path(os.path.abspath(__file__))) \
                     + '<br/><br/><font color="red">' \
                     + _str + '</font>'
        try:
            send_yagmail(
                emails_to=m_cfg.get_value('Email/sent_to_emails'),
                subject=email_subject,
                message=email_body
                # ,attachment_path = email_attchms_study
            )
        except Exception as ex:
            # report unexpected error during sending emails to a log file and continue
            _str = 'Unexpected Error "{}" occurred during an attempt to send email upon ' \
                   'finishing execution of file monitoring app.\n{}'.format(ex, traceback.format_exc())
            mlog.critical(_str)
        exit(1)

    # Validate expected environment variables; if some variable are not present, abort execution
    cm2.validate_available_envir_variables(mlog, m_cfg, ['box_monitoring'], str(Path(os.path.abspath(__file__))))

    try:

        email_msgs_study = []

        (_, _, monitor_files) = next(walk(monitor_path))

        mlog.info('The following monitor configs are to be processed (count = {}) in the monitor folder {}: {}'.format(len(monitor_files), monitor_path, monitor_files))

        for mnt_config in monitor_files:
            mlog.info('-------------------------------------------')
            mlog.info('Start processing monitor config file: "{}".'.format(mnt_config))
            try:
                mnt = Monitor(Path(monitor_path) / mnt_config, mlog)
                mnt.start_monitor()
            except Exception as ex:
                # report unexpected error to log file
                _str = 'Unexpected Error "{}" occurred during processing monitor config file: {}\n{} ' \
                    .format(ex, mnt_config, traceback.format_exc())
                mlog.error(_str)
            mlog.info('Finish processing monitor config file: "{}".'.format(mnt_config))
            # create a dictionary to feed into template for preparing an email body
            template_feeder = {
                'source_file_path': '{}/{}'.format(str(mnt.mtr_source_dir), str(mnt.mtr_source_file)),
                'source_identified': str(mnt.mtr_source_path),
                'source_file_name': Path(os.path.abspath(mnt.mtr_source_path)).name
                                    if mnt.mtr_source_path
                                    else 'N/A',
                'confg_file_name': str(mnt.mtr_cfg_path),
                'destination': mnt.mtr_destin,
                'action_completed': mnt.action_completed,
                'log_file': log_handler.baseFilename,
                'status_lst': mnt.status,
                'file_errors_present': mnt.error.errors_exist()
            }
            email_body_part = cm.populate_email_template('processed_monitor_files.html', template_feeder)
            email_msgs_study.append(email_body_part)

        mlog.info('-------------------------------------------')
        mlog.info('All monitor configs were processed (count = {}) in the monitor folder {}: {}'.format(
            len(monitor_files), monitor_path, monitor_files))

        email_subject = 'Monitoring files app'
        email_body = ('Number of monitored locatoins: {}. Below are details for each locatoin.'.format(len(monitor_files))
                      + '<br/>----------------------------------<br/>'
                      + '<br/>----------------------------------<br/>'.join(email_msgs_study)
                      )

        # print ('email_subject = {}'.format(email_subject))
        # print('email_body = {}'.format(email_body))

        # remove return characters from the body of the email, to keep just clean html code
        email_body = email_body.replace("\r", "")
        email_body = email_body.replace("\n", "")

        try:
            if m_cfg.get_value('Email/send_emails'):
                send_yagmail(
                    # TODO: add email addresses from a local config files
                    emails_to=m_cfg.get_value('Email/sent_to_emails'),
                    subject=email_subject,
                    message=email_body
                    # ,attachment_path = email_attchms_study
                )
        except Exception as ex:
            # report unexpected error during sending emails to a log file and continue
            _str = 'Unexpected Error "{}" occurred during an attempt to send email upon ' \
                   'finishing execution of file monitoring app.\n{}'.format(ex, traceback.format_exc())
            mlog.critical(_str)

    except Exception as ex:
        # report unexpected error to log file
        _str = 'Unexpected Error "{}" occurred during processing file: {}\n{} '\
            .format(ex, os.path.abspath(__file__), traceback.format_exc())
        mlog.critical(_str)
        raise

    sys.exit()