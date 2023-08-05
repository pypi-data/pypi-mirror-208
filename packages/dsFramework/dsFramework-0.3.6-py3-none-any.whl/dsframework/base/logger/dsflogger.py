import logging
import json
import os
import datetime
from pythonjsonlogger import jsonlogger


project_id = 'dozi-stg-ds-apps-1'
topic_id = 'log-export-to-bq'

is_gae = "SPRING_PROFILES_ACTIVE" in os.environ
is_production = ("SPRING_PROFILES_ACTIVE" in os.environ and os.environ["SPRING_PROFILES_ACTIVE"] == 'production') \
                or ("ANY_GKE_ENV_VAR" in os.environ and os.environ["ANY_GKE_ENV_VAR"] == 'production')
if is_gae:
    if is_production:
        project_id = 'dozi-prd-ds-apps-1'
else:
    project_id = os.environ.get("DS_APPS_PROJECT_ID", "dozi-stg-ds-apps-1")
# use only for sending the logs and have the ability to get it in BQ and DSP - must be same name as project folder
curr_project_project_id = os.environ.get("PROJECT_ID", "not_defined")

project_name = os.environ.get("SERVICE_NAME", "not_defined")
resource = os.environ.get("RESOURCE", "not_defined")
run_env = os.environ.get("RUN_ENV", "not_defined")
resource_type = resource + '-' + run_env + '-' + project_name if "RESOURCE" in os.environ else 'not_defined'


class DSFLogger(logging.getLoggerClass()):

    level = logging.INFO
    enable_push = False

    def __init__(self,
                 msg_format='INFO',
                 json_formatter=True,
                 json_formatter_format='%(levelname) %(asctime) %(message)',
                 enable_push=False,
                 wait=False
                 ):
        super(DSFLogger, self).__init__(name='DSFLogger')

        self.enable_push = enable_push

        if enable_push and not is_gae:
            try:
                # todo: temporary workaround until we get permission to the Pub/Sub from Jenkins
                # pip install google-cloud-pubsub
                from google.cloud import pubsub_v1
                from concurrent.futures import ThreadPoolExecutor, TimeoutError
                self.publisher = pubsub_v1.PublisherClient()
                self.executor = ThreadPoolExecutor(max_workers=10)
                self.wait = wait
            except Exception as ex:
                print(f'Exception initiating pubsub publisher: {ex}')
                self.publisher = None
                self.executor = None
                self.wait = None

        formatter = jsonlogger.JsonFormatter(json_formatter_format)

        try:
            level_name = logging.getLevelName(msg_format)
            if type(level_name) == int:
                self.level = level_name
        except Exception as e:
            pass

        self.setLevel(self.level)

        if not self.handlers and json_formatter:
            self.propagate = False
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.addHandler(handler)
        else:
            default_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s', None, '%')
            handler = logging.StreamHandler()
            handler.setFormatter(default_formatter)
            self.addHandler(handler)

        self.info(f'INFO logger started..., pubsub enabled: {enable_push}.')

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.
        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.
        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        self.push_to_pub_sub(self.enable_push, str(msg), 'stdout', **kwargs)
        super().info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.
        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.
        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        super().debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.
        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.
        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        super().warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.
        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.
        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        self.push_to_pub_sub(self.enable_push, str(msg), 'stderr', **kwargs)
        super().error(msg, *args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.
        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.
        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        super().critical(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.
        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.
        logger.log(level, "We have a %s", "mysterious problem", exc_info=1)
        """
        super().log(level, msg, *args, **kwargs)

    def submit_func(self, publisher, topic_path, data):
        future = publisher.publish(topic_path, data)

        if self.wait:
            future.result(timeout=60)

    def push_to_pub_sub(self, enable_push: bool, msg: str, log_type='stdout', **kwargs):
        if enable_push and project_id and topic_id and not is_gae and self.publisher:
            extra_input = ''
            output = ''
            from_host = ''
            from_service_account = ''
            pipeline_exec_time = ''
            predictable_object_count = ''
            timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            if 'extra' in kwargs:
                if 'input' in kwargs['extra']:
                    extra_input = kwargs['extra']['input']
                if 'output' in kwargs['extra']:
                    output = kwargs['extra']['output']
                if 'from_host' in kwargs['extra']:
                    from_host = kwargs['extra']['from_host']
                if 'from_service_account' in kwargs['extra']:
                    from_service_account = kwargs['extra']['from_service_account']
                if 'pipeline_exec_time' in kwargs['extra']:
                    pipeline_exec_time = kwargs['extra']['pipeline_exec_time']
                if 'predictable_object_count' in kwargs['extra']:
                    predictable_object_count = kwargs['extra']['predictable_object_count']

            bg_log_type = ''
            if 'stdout' in log_type:
                bg_log_type = 'INFO'
            elif 'stderr' in log_type:
                bg_log_type = 'ERROR'
            model_version = ''
            if len(output) > 0:
                model_version = output[0]['info']['model_version']
            log_entry = {
                "type": bg_log_type,
                "insert_id": '',
                "request_input": str(extra_input),
                "request_message": msg.strip(),
                "request_output": str(output),
                "project_id": curr_project_project_id,
                "project_name": project_name,
                "version": model_version,
                "resource_type": resource_type,
                "timestamp": timestamp,
                "from_host": from_host,
                "from_service_account": from_service_account,
                "pipeline_exec_time": pipeline_exec_time,
                "predictable_object_count": str(predictable_object_count)
            }
            try:
                topic_path = self.publisher.topic_path(project_id, topic_id)
                self.executor.submit(self.submit_func, self.publisher, topic_path,
                                     json.dumps(log_entry).encode("utf-8"))

            except TimeoutError as te:
                self.enable_push = False
                self.error(f'Error pub/sub timeout, make sure your are logged to gcloud, exception {te}')
                self.enable_push = True
            except Exception as ex:
                self.enable_push = False
                self.error(f'Error pushing to pub/sub, exception {ex}')
                self.enable_push = True


logger = DSFLogger(msg_format='INFO', json_formatter=True, enable_push=True)


# if __name__ == '__main__':
#
#     dsfLogger = DSFLogger(msg_format='DEBUG', json_formatter=True, enable_push=True, wait=True)
#
#     for i in range(1, 11):
#         dsfLogger.info(f'Info test message ,{i},', extra={'test': f'test ,{i},'})
#
#     dsfLogger.debug("Debug test message.")
#     dsfLogger.error("Error test message 7.", extra={'more': 'additional information'})
