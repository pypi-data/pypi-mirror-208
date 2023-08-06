import datetime
import logging
import os
import time

from .Config.Config import Config
from .Notifications.Telegram import Telegram


class HealthCheck:
    """
    HealthCheck class
    """
    is_connected_client_list = {}
    client_list = {}
    interfaces = []
    timeout = 1
    frequency_check = 5
    telegram = None
    logger = None

    def __init__(self, settings_file="", log_level=30):
        """
        Construct HealthCheck Object
        :param settings_file: Path to the setting file
        :param log_level: verbosity log level
        :return:
        """
        logging.basicConfig(format='[%(levelname)s] %(asctime)s: %(message)s', level=os.environ.get('VERBOSITY', log_level))
        self.logger = logging.getLogger(__name__)
        if not settings_file:
            settings_file = config_path=os.path.join(os.path.dirname(__file__), "../settings.yml")
        settings = Config.load_yaml_config(config_path=settings_file)
        self.timeout = settings['settings']["timeout"]
        self.frequency_check = settings["settings"]["frequency_check"]
        self.client_list = {v: k for k, v in settings["settings"]["clients"].items()}
        for client in self.client_list:
            self.is_connected_client_list[self.client_list[client]] = False
        self.telegram = Telegram(settings_file, self.logger)
        self.interfaces = settings['settings']['interfaces']
        # Debug content vars
        self.logger.debug("client_list = {client_list}\n"
                          "id_connected_client_list = {is_connected_client_list}\n"
                          "interface_list = {interface_list}\n"
                          "timeout = {timeout}\n"
                          "frequency_check = {frequency_check}".format(
                            client_list=self.client_list,
                            is_connected_client_list=self.is_connected_client_list,
                            interface_list=self.interfaces,
                            timeout=self.timeout,
                            frequency_check=self.frequency_check))

    def check(self):
        """
        Check method
        :return:
        """

        while True:
            time.sleep(self.frequency_check)
            for current_interface in self.interfaces:
                result = os.popen("wg show {interface} dump | tail -n +2".format(interface=current_interface)).readlines()

                for line in result:
                    result_line_list = line.split("\t")
                    if result_line_list[3] not in self.client_list:
                        continue
                    current_client_name = self.client_list[result_line_list[3]]
                    self.logger.info("current client check : {current_client_name}".format(
                        current_client_name=current_client_name)
                    )
                    now = datetime.datetime.now()
                    last_seen = datetime.datetime.fromtimestamp(int(result_line_list[4]))
                    d1_ts = time.mktime(now.timetuple())
                    d2_ts = time.mktime(last_seen.timetuple())
                    minutes_diff = (d1_ts - d2_ts) / 60
                    self.logger.info("Last refreshed handshake : {last_seen}\nLong ago : {diff}".format(last_seen=last_seen, diff=minutes_diff))
                    if minutes_diff > self.timeout and self.is_connected_client_list[current_client_name]:
                        self.is_connected_client_list[current_client_name] = False
                        self.telegram.notify_disconnected(client_name=current_client_name)
                    elif minutes_diff < self.timeout and not self.is_connected_client_list[current_client_name]:
                        self.is_connected_client_list[current_client_name] = True
                        self.telegram.notify_connected(client_name=current_client_name)
