from pathlib import PurePath
from common import ContainerTester
from runners import SnakemakeRunner
from checkers import SimpleChecker

def test_index_split_cram():

    data_path = PurePath("assets/index_split_cram/")
    tester = ContainerTester(SnakemakeRunner(), SimpleChecker(), data_path)
    tester.run()