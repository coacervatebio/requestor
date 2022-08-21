import os
import rootpath
from pathlib import Path

# TODO: Check app keys etc are set in env

test_tag = 'coacervate_requestor:test'
test_sample = 'HG03633'
rpath = Path(rootpath.detect())
yagna_datadir = Path('/home/vagrant/yagna_datadir/')

# Create mount points for input and output to pass to container
almt_dir = Path.joinpath(rpath, 'tests', 'requestor', 'assets', 'alignments')
tmp_out_dir = Path.joinpath(rpath, 'tests', 'requestor', 'assets', 'tmp_output')


# Get names of input samples dynamically
per_chr_samples = []
expected_hc_out = []
for reg_dir in almt_dir.glob('chr*'):
    for almt in reg_dir.glob('*cram'):
        sample = almt.with_suffix('').name
        per_chr_samples.append(sample)
        expected_hc_out.append(tmp_out_dir.joinpath(reg_dir.name, f"{sample}.g.vcf.gz"))
        expected_hc_out.append(tmp_out_dir.joinpath(reg_dir.name, f"{sample}.g.vcf.gz.tbi"))