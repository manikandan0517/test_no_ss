import os
import socket
import logging
from datadog_api_client.v2 import ApiClient, ApiException, Configuration
from datadog_api_client.v2.api import logs_api
from datadog_api_client.v2.models import HTTPLog, HTTPLogItem

class DDHandler(logging.StreamHandler):
    def __init__(self, configuration, service_name, ddsource):
        super().__init__()
        self.configuration = configuration
        self.service_name = service_name
        self.ddsource = ddsource
        self.hostname = socket.gethostname()  

    def emit(self, record):
        msg = self.format(record)
        with ApiClient(self.configuration) as api_client:
            api_instance = logs_api.LogsApi(api_client)
            body = HTTPLog([
                HTTPLogItem(
                    ddsource=self.ddsource,
                    ddtags=f"env:{os.getenv('ENV', 'DEV')}",
                    message=msg,
                    service=self.service_name,
                    hostname=self.hostname  # Add hostname to the log
                )
            ])
            try:
                api_instance.submit_log(body)
            except ApiException as e:
                print(f"Error sending log: {e}")

class Logger:
    def __init__(self, service_name, ddsource):
        self.configuration = Configuration()
        self.logger = logging.getLogger("datadog_logger")
        self.logger.setLevel(logging.INFO)
        dd_handler = DDHandler(self.configuration, service_name, ddsource)
        dd_handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(dd_handler)
        

    def log(self, message, level="info"):
        if level == "error":
            self.logger.error(message)
        else:
            self.logger.info(message)
            

if __name__ == "__main__":
    os.environ["DD_API_KEY"] = ""
    os.environ["DD_SITE"] = "us5.datadoghq.com"
    os.environ["ENV"] = "DEV"

    logger = Logger(service_name="my-service", ddsource="python")
    logger.log("data logs")
