import os
from typing import List
from flytekit import workflow, dynamic, LaunchPlan
from flytekit.types.file import FlyteFile
from flytekit.types.directory import FlyteDirectory
from flytekitplugins.pod import Pod
from run.tasks.mapping import index_cram, split_cram 
from run.tasks.calling import golem_call_variants, combine_region, genotype, gather_vcfs
from run.tasks.utils import get_dir, return_alignment, prep_db_import, prep_gather_vcfs
from run.pod.yagna_template import yagna_requestor_ps
from run import config

@dynamic(
    container_image=config['current_image'],
    task_config=Pod(pod_spec=yagna_requestor_ps)
    )
def process_samples(indir: FlyteDirectory, regs: List[str]) -> FlyteFile:

    per_reg_als = []
    for f in os.listdir(indir):
        s = f.strip('.cram')
        fi = os.path.join(indir, f)
        idx = index_cram(al=fi)
        for r in regs:
            per_reg = split_cram(al=fi, idx=idx, sample=s, reg=r, ref_loc=config['reference_location'])
            per_reg_idx = index_cram(al=per_reg)
            per_reg_al = return_alignment(sample=s, reg=r, almt=per_reg, idx=per_reg_idx)
            per_reg_als.append(per_reg_al)
    
    vcf_objs = golem_call_variants(als=per_reg_als)

    to_gather = []
    for r in regs:
        vnames, vdir = prep_db_import(vcf_objs=vcf_objs, region=r)
        db_out = combine_region(vnames_fmt=vnames, vdir=vdir, reg=r)
        geno_out = genotype(db_dir=db_out, reg=r, ref_loc=config['reference_location'])
        to_gather.append(geno_out)

    vnames_fmt, fd = prep_gather_vcfs(combi_dirs=to_gather)
    gather_out = gather_vcfs(vnames_fmt=vnames_fmt, vdir=fd)

    return gather_out

@workflow
def wf(al_dir: str, regs: List[str]) -> FlyteFile:
    
    fd = get_dir(dirpath=al_dir)
    out_ = process_samples(indir=fd, regs=regs)
    return out_

builtin_lp = LaunchPlan.create(
    "Built-In Launchplan",
    wf, 
    default_inputs={
        "al_dir": "/coa/data/alignments",
        "regs": ["chr21", "chr22"]
        }
    )
