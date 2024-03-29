from flytekit import workflow
from run.tasks.mapping import split_cram
from run.tasks.utils import get_file
from run.tests.helpers import compare_files
from run import config

@workflow
def test_split_cram_wf():
    al = get_file(filepath='s3://my-s3-bucket/test-assets/HG04149_sub.cram')
    idx = get_file(filepath='s3://my-s3-bucket/test-assets/HG04149_sub.cram.crai')
    reg_al_actual = split_cram(al=al, idx=idx, sample='HG04149_sub', reg='chr21', ref_loc=config['reference_location'])
    reg_al_expected = get_file(filepath='s3://my-s3-bucket/test-assets/HG04149_sub_chr21.cram')
    compare_files(actual=reg_al_actual, expected=reg_al_expected, checker='cram')
