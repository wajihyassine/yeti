import logging
from datetime import timedelta
from typing import ClassVar
from core.schemas.observables import ipv4
from core.schemas import task
from core import taskmanager
import pandas as pd
from io import StringIO


class AlienVaultIPReputation(task.FeedTask):
    _SOURCE: ClassVar["str"] = "http://reputation.alienvault.com/reputation.data"
    _defaults = {
        "frequency": timedelta(hours=4),
        "name": "AlienVaultIPReputation",
        "description": "Reputation IP generated by Alienvault",
    }
    _NAMES = [
        "IP",
        "number_1",
        "number_2",
        "Tag",
        "Country",
        "City",
        "Coord",
        "number_3",
    ]

    def run(self):
        response = self._make_request(self._SOURCE, verify=True)
        if response:
            data = response.text

            df = pd.read_csv(
                StringIO(data),
                delimiter="#",
                names=self._NAMES,
            )

            for _, item in df.iterrows():
                self.analyze(item)

    def analyze(self, item):
        context = dict(source=self.name)

        ip_str = item["IP"]
        category = item["Tag"]
        country = item["Country"]

        ip_obs = ipv4.IPv4(value=ip_str).save()

        context["country"] = country
        context["threat"] = category
        context["reliability"] = item["number_1"]
        context["risk"] = item["number_2"]

        ip_obs.tag([category])
        ip_obs.add_context(self.name, context)


taskmanager.TaskManager.register_task(AlienVaultIPReputation)
