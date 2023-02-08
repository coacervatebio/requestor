rule call_variants:
    input:
        script="/data/workflow/scripts/requestor.py",
        alignments=expand("/data/results/alignments/{reg}/{sample}_{reg}.cram", reg=config['regs'], sample=config['samples']),
        indexes=expand("/data/results/alignments/{reg}/{sample}_{reg}.cram.crai", reg=config['regs'], sample=config['samples'])
    output:
        called_vcfs=temp(expand("/data/results/hc_out/{reg}/{sample}_{reg}.g.vcf.gz", reg=config['regs'], sample=config['samples'])),
        indexes=temp(expand("/data/results/hc_out/{reg}/{sample}_{reg}.g.vcf.gz.tbi", reg=config['regs'], sample=config['samples']))
    log: 
        # Capture stderr, DEBUG info in separate logfile
        "/data/workflow/logs/call_variants_stderr.log"
    shell:
        "python {input.script} --subnet {config[golem_subnet]} > {log}"

rule combine_region:
    input:
        gvcfs=set(expand(f"/data/results/hc_out/{{reg}}/{{sample}}_{{reg}}.g.vcf.gz", reg=config['regs'], sample=config['samples'])),
        indexes=set(expand(f"/data/results/hc_out/{{reg}}/{{sample}}_{{reg}}.g.vcf.gz.tbi", reg=config['regs'], sample=config['samples']))
    output:
        temp(directory(f"/data/results/combi_out/{{reg}}_database/"))
    params:
        lambda wildcards, input: ' '.join([f'-V {fn}' for fn in input.gvcfs if f'{wildcards.reg}.' in fn])
    shell:
       "gatk --java-options '-Xmx4g' GenomicsDBImport {params} -L {wildcards.reg} --genomicsdb-workspace-path {output}"

rule genotype:
    input:
        f"/data/results/combi_out/{{reg}}_database/"
    output:
        joint_vcf=temp(f"/data/results/geno_out/combined_{{reg}}.vcf.gz"),
        index=temp(f"/data/results/geno_out/combined_{{reg}}.vcf.gz.tbi")
    params:
        reference=config['ref']
    shell:
        "gatk --java-options '-Xmx4g' GenotypeGVCFs -R {params.reference} -V gendb://{input} -O {output.joint_vcf}"

rule gather_vcfs:
    input:
        expand("/data/results/geno_out/combined_{reg}.vcf.gz", reg=config['regs'])
    output:
        f"/data/results/gather_out/project_output.vcf.gz"
    params:
        lambda wildcards, input: ' '.join([f'-I {fn}' for fn in input])
    shell:
        "gatk --java-options '-Xmx4g' GatherVcfs {params} -O {output}"