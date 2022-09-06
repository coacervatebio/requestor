from pathlib import Path, PurePath
from common import ContainerTester, allowed_pattern
from runners import SnakemakeRunner
from checkers import VcfChecker

def test_genotype():

    data_path = PurePath("assets/genotype/")

    tmpdir = Path("/home/vagrant/tmp_guest")
    tester = ContainerTester(SnakemakeRunner(), VcfChecker(), data_path, tmpdir=tmpdir)
    tester.track_unexpected = False

    tester.target_files = filter(allowed_pattern, tester.target_files)

    tester.run()