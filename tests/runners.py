import os
import logging
import docker
from tests.config import test_tag, test_name, yagna_datadir

LOGGER = logging.getLogger(__name__)
client = docker.from_env()

class SnakemakeRunner:

    def __init__(self):
        self.cons = client.containers
        self.target_string = ''
        self.vols = []
        self.arb_com = []

    def run(self):
    # Run the test job.
        logs = self.cons.run(
            test_tag,
            command=[
                "-m",
                "specific",
                "-o",
                self.target_string,
                *self.arb_com
            ],
            name=test_name,
            volumes=self.vols
            ).decode('utf-8')

        return logs


class GothRequestorRunner():

    def __init__(self):
        self.cons = client.containers
        self.vols = []

        assert os.environ.get('YAGNA_APPKEY') is not None, 'No appkey set'

    def run(self):
        # logs = self.cons.run(
        container = self.cons.run(
            test_tag,
            entrypoint="python",
            command=f'/data/workflow/scripts/requestor.py --subnet goth',
            name=test_name,
            environment=[
                f"YAGNA_APPKEY={os.environ['YAGNA_APPKEY']}",
                f"YAGNA_API_URL={os.environ['YAGNA_API_URL']}",
                f"GSB_URL={os.environ['GSB_URL']}",
                ],
            network_mode="host",
            volumes=self.vols,
            detach=True
            )#.decode('utf-8')
        output = container.attach(stdout=True, stream=True, logs=True)
        for line in output:
            print(line)

        # return logs
    
class DevnetRequestorRunner():

    def __init__(self):
        self.cons = client.containers
        self.vols = []
    
    def run(self):
        # logs = client.containers.run(
        container = client.containers.run(
            test_tag,
            command=[
                "-m",
                "req_only", # Default in /data/config/config.yml is devnet-beta
                "-y",
                "on"
            ],
            name=test_name,
            volumes=[
                *self.vols,
                f'{str(yagna_datadir)}:/home/requestor/.local/share/yagna',
                ],
            detach=True 
            )#.decode('utf-8')
        output = container.attach(stdout=True, stream=True, logs=True)
        for line in output:
            print(line)
        # return logs
