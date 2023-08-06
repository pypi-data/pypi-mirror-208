from time import sleep

import requests
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class NesOperator(BaseOperator):
    template_fields = ("input_nb", "parameters")

    @apply_defaults
    def __init__(
        self,
        input_nb: str,
        parameters: dict = None,
        runtime: str = None,
        profile: str = None,
        host_network: bool = None,
        poll_interval: int = 60,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.input_nb = input_nb
        self.parameters = parameters or {}
        self.run_id = None
        self.runtime = runtime
        self.profile = profile
        self.host_network = host_network

        self.nes = "http://nes.sktai.io/v1/runs"
        self.poll_interval = poll_interval

    def get_status(self, id):
        res = requests.get(f"{self.nes}/{id}")
        res.raise_for_status()
        status = res.json()["status"]
        return status

    def execute(self, context):
        data = {"input_url": self.input_nb, "parameters": self.parameters}
        if self.runtime:
            data["runtime"] = self.runtime

        if self.profile:
            data["profile"] = self.profile

        if self.host_network is not None:
            data["host_network"] = self.host_network

        res = requests.post(self.nes, json=data)
        print(f"Job submitted with: {data}")
        res.raise_for_status()

        r = res.json()
        id, output = r["id"], r["output_url"]
        self.run_id = id
        print(
            f"""--------------------------------------------------------------------------------\n\n{output}\n\n--------------------------------------------------------------------------------"""
        )

        while (status := self.get_status(id)) != "Succeeded":
            if status in ["Failed", "Error"]:
                raise AirflowException(f'Job {id} exited with "{status}"')
            else:
                print(f'Polling job status... current status: "{status}"')
                sleep(self.poll_interval)

        print(f'Job {id} successfully finished with "{status}"')
        return True

    def on_kill(self):
        while True:
            res = requests.delete(f"{self.nes}/{self.run_id}")
            if res.status_code == 404:
                break
            status = res.json()["status"]
            print(f'Deleting job... current status: "{status}"')
            sleep(self.poll_interval)
