import os
from pathlib import Path, PurePath
from typing import List, Tuple
from flytekit import kwtypes, workflow, dynamic, task, ContainerTask
from flytekit.types.file import FlyteFile
from flytekit.types.directory import FlyteDirectory
from flytekitplugins.pod import Pod
from .pod_templates import yagna_requestor
from .utils import VCF, Alignment, run_golem
from .pod_templates import yagna_requestor_ps
from .flyte_haplotypecaller import main


@task(
    container_image='docker.io/coacervate/requestor:latest',
    task_config=Pod(pod_spec=yagna_requestor_ps)
    )
def golem_call_variants(als: List[Alignment]) -> List[VCF]:
    payloads = []
    vcfs = []
    for al in als:
        working_dir = PurePath(al.almt.path).parent

        # Download alignment and index from object store to pod for uploading to Golem
        al.almt.download()
        al.idx.download()

        # Prepare payload for passing to requestor agent
        payload = {
            "sample": al.sample,
            "region_str": al.reg,
            "working_dir": working_dir,
            "req_align_path": Path(al.almt.path),
            "req_align_index_path": Path(al.idx.path),
            "req_vcf_path": working_dir.joinpath(f"{al.sample}_{al.reg}.g.vcf.gz"),
            "req_vcf_index_path": working_dir.joinpath(f"{al.sample}_{al.reg}.g.vcf.gz.tbi"),
        }

        # Prepare VCF based on output paths
        vcf = VCF(
            sample=al.sample,
            reg=al.reg,
            vcf=FlyteFile(path=str(payload['req_vcf_path'])),
            idx=FlyteFile(path=str(payload['req_vcf_index_path'])),
        )
        
        vcfs.append(vcf)
        payloads.append(payload)

    # Call requestor agent entrypoint with payloads
    run_golem(main, payloads)
    return vcfs

golem_test = ContainerTask(
    name="golem-test",
    input_data_dir="/mnt",
    output_data_dir="/var/outputs",
    inputs=kwtypes(),
    outputs=kwtypes(),
    image="docker.io/coacervate/requestor:latest",
    pod_template = yagna_requestor,
    # pod_template_name = "my-pod-template", # Modify vols / svc here for yagna
    command=[
        "python",
        "/data/agents/hello_golem.py"
    ],
)

basic_test = ContainerTask(
    name="basic-test",
    input_data_dir="/var/inputs",
    output_data_dir="/var/outputs",
    inputs=kwtypes(indir=FlyteDirectory),
    outputs=kwtypes(),
    image="ghcr.io/flyteorg/rawcontainers-shell:v2",
    # pod_template = pt,
    # pod_template_name = "my-pod-template", # Modify vols / svc here for yagna
    command=[
        # "ls",
        # "-la",
        # "/var/inputs",
        "sleep",
        "infinity"
    ],
)

index_cram = ContainerTask(
    name="index_cram",
    input_data_dir="/var/inputs",
    output_data_dir="/var/outputs",
    inputs=kwtypes(al_in=FlyteFile),
    outputs=kwtypes(idx_out=FlyteFile),
    image="docker.io/coacervate/requestor:latest",
    command=[
        "samtools",
        "index",
        "/var/inputs/al_in",
        "-o",
        "/var/outputs/idx_out"
    ],
)

split_cram = ContainerTask(
    name="split_cram",
    input_data_dir="/var/inputs",
    output_data_dir="/var/outputs",
    inputs=kwtypes(al_in=FlyteFile, idx_in=FlyteFile, reg=str),
    outputs=kwtypes(reg_out=FlyteFile),
    image="docker.io/coacervate/requestor:latest",
    command=[
        "samtools",
        "view",
        "-T",
        "/root/reference/resources_broad_hg38_v0_Homo_sapiens_assembly38.fasta",
        "-O",
        "cram",
        "-o",
        "/var/outputs/reg_out",
        "-X",
        "/var/inputs/al_in",
        "/var/inputs/idx_in",
        "{{.inputs.reg}}",
    ],
)