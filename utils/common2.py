import os
from pathlib import Path
from utils import common as cm
from utils import send_yagmail

# Validate expected Environment variables; if some variable are not present, abort execution
# setup environment variable sources:
# windows: https://www.youtube.com/watch?v=IolxqkL7cD8
# linux: https://www.youtube.com/watch?v=5iWhQWVXosU
def validate_available_envir_variables (mlog, m_cfg, env_cfg_groups = None, app_path_to_report = None):
    # env_cfg_groups should be a list of config groups of expected environment variables
    if not env_cfg_groups:
        env_cfg_groups = []
    if not isinstance(env_cfg_groups, list):
        env_cfg_groups = [env_cfg_groups]

    mlog.info('Start validating presence of required environment variables.')
    env_vars = []
    env_var_confs = m_cfg.get_value('Validate/environment_variables')  # get dictionary of envir variables lists
    if env_var_confs and isinstance(env_var_confs, dict):
        for env_gr in env_var_confs:  # loop groups of envir variables
            if env_gr in env_cfg_groups:
                # proceed here for the "default" group of envir variables
                env_vars = cm.extend_list_with_other_list(env_vars, env_var_confs[env_gr])
        # validate existence of the environment variables
        missing_env_vars = []
        for evar in env_vars:
            if not cm.validate_envir_variable(evar):
                missing_env_vars.append(evar)

        if missing_env_vars:
            # check if any environment variables were recorded as missing
            _str = 'The following environment variables were not found: {}. Aborting execution. ' \
                   'Make sure that the listed variables exist before next run.'.format(missing_env_vars)
            mlog.error(_str)

            # send notification email alerting about the error case
            email_subject = 'Error occurred during running file_monitoring tool'
            email_body = 'The following error caused interruption of execution of the application<br/>' \
                         + (str(app_path_to_report) if app_path_to_report else '')\
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
        else:
            mlog.info('All required environment variables were found.')
