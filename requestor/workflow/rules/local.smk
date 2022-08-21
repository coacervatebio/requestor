import os
from utils import dir_to_samples

configfile: "/mnt/config/config.yml"
samples = dir_to_samples(f"/mnt/results/alignments/full")

rule all:
    input:
        # expand("/mnt/results/alignments/{sample}.cram.crai", sample=SAMPLES),
        # expand("/mnt/results/alignments/{reg}/{sample}_{reg}.cram", sample=samples, reg=config['regs']),
        # expand("/mnt/results/alignments/{reg}/{sample}_{reg}.cram.crai", sample=samples, reg=config['regs']),
        # expand("/mnt/results/hc_out/{reg}/{sample}_{reg}.g.vcf.gz", sample=samples, reg=config['regs']),
        # expand("/mnt/results/combi_out/{reg}_database/", reg=config['regs']),
        # expand("/mnt/results/geno_out/combined_{reg}.vcf.gz", reg=config['regs']),
        f"/mnt/results/gather_out/project_output.vcf.gz",

rule index_cram:
    input:
        f"/mnt/results/alignments/full/{{sample}}.cram"
    output:
        temp(f"/mnt/results/alignments/full/{{sample}}.cram.crai")
    shell:
        "samtools index {input}"

rule split_cram:
    input:
        alignments=f"/mnt/results/alignments/full/{{sample}}.cram",
        indexes=f"/mnt/results/alignments/full/{{sample}}.cram.crai"
    output:
        temp(f"/mnt/results/alignments/{{reg}}/{{sample}}_{{reg}}.cram")
    shell:
        "samtools view {input.alignments} {wildcards.reg} -T {config[ref]} -O cram -o {output}"

rule index_split_cram:
    input:
        f"/mnt/results/alignments/{{reg}}/{{sample}}_{{reg}}.cram"
    output:
        temp(f"/mnt/results/alignments/{{reg}}/{{sample}}_{{reg}}.cram.crai")
    shell:
        "samtools index {input}"

rule call_variants:
    input:
        alignments=f"/mnt/results/alignments/{{reg}}/{{sample}}_{{reg}}.cram",
        indexes=f"/mnt/results/alignments/{{reg}}/{{sample}}_{{reg}}.cram.crai"
    output:
        called_vcf=temp(f"/mnt/results/hc_out/{{reg}}/{{sample}}_{{reg}}.g.vcf.gz"),
        index=temp(f"/mnt/results/hc_out/{{reg}}/{{sample}}_{{reg}}.g.vcf.gz.tbi")
    shell:
        "gatk --java-options '-Xmx4g' HaplotypeCaller -I {input.alignments} -O {output.called_vcf} -R {config[ref]} -L {wildcards.reg} -ERC GVCF"

rule combine_region:
    input:
        gvcfs=set(expand(f"/mnt/results/hc_out/{{reg}}/{{sample}}_{{reg}}.g.vcf.gz", sample=samples, reg=config['regs'])),
        indexes=set(expand(f"/mnt/results/hc_out/{{reg}}/{{sample}}_{{reg}}.g.vcf.gz.tbi", sample=samples, reg=config['regs']))
    output:
        temp(directory(f"/mnt/results/combi_out/{{reg}}_database/"))
    params:
        lambda wildcards, input: ' '.join([f'-V {fn}' for fn in input.gvcfs if f'{wildcards.reg}.' in fn])
    shell:
       "gatk --java-options '-Xmx4g' GenomicsDBImport {params} -L {wildcards.reg} --genomicsdb-workspace-path {output}"

rule genotype:
    input:
        f"/mnt/results/combi_out/{{reg}}_database/"
    output:
        joint_vcf=temp(f"/mnt/results/geno_out/combined_{{reg}}.vcf.gz"),
        index=temp(f"/mnt/results/geno_out/combined_{{reg}}.vcf.gz.tbi")
    shell:
        "gatk --java-options '-Xmx4g' GenotypeGVCFs -R {config[ref]} -V gendb://{input} -O {output.joint_vcf}"

rule gather_vcfs:
    input:
        expand("/mnt/results/geno_out/combined_{reg}.vcf.gz", reg=config['regs'])
    output:
        f"/mnt/results/gather_out/project_output.vcf.gz"
    params:
        lambda wildcards, input: ' '.join([f'-I {fn}' for fn in input])
    shell:
        "gatk --java-options '-Xmx4g' GatherVcfs {params} -O {output}"