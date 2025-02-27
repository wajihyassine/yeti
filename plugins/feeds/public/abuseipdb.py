import logging
from datetime import timedelta, datetime
from typing import ClassVar
from core.schemas.observables import ipv4
from core.schemas import task
from core import taskmanager


from core.config.config import yeti_config


class AbuseIPDB(task.FeedTask):
    _SOURCE: ClassVar[
        "str"
    ] = "https://api.abuseipdb.com/api/v2/blacklist?&key=%s&plaintext&limit=10000"
    _defaults = {
        "frequency": timedelta(hours=5),
        "name": "AbuseIPDB",
        "description": "Black List IP generated by AbuseIPDB",
    }

    def run(self):
        api_key = yeti_config.get("abuseIPDB", "key")

        if not api_key:
            raise Exception("Your abuseIPDB API key is not set in the yeti.conf file")

        # change the limit rate if you subscribe to a paid plan
        response = self._make_request(self._SOURCE % api_key, verify=True)
        if response:
            data = response.text

            for line in data.split("\n"):
                self.analyze(line)

    def analyze(self, line):
        line = line.strip()

        ip_value = line

        context = {"source": self.name, "date_added": datetime.utcnow()}
        ipv4_obs = ipv4.IPv4(value=ip_value).save()

        logging.debug(f"Adding context to {ip_value}")
        ipv4_obs.add_context(self.name, context)
        ipv4_obs.tag(["blocklist"])


taskmanager.TaskManager.register_task(AbuseIPDB)
