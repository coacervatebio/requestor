# Coacervate

## Introduction

Genomic data has been generated [faster and faster](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1002195) since the first human genome was sequenced - with no signs of slowing down. The demand for expertise, and the raw compute power needed to turn those enormous datasets into actionable insights, has exploded alongside it.

Analyzing that data relies on a highly-specialized, [multi-disciplinary](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5471940/) skillset. Tools exist that make this step easier, but they are often black-boxes and prohibitively expensive at scale; this precludes access from aspiring researchers and stifles collaboration.

Usability aside, there's no getting around the sheer scale of computing resources needed. Coupled with the fact that we can no longer rely on [Moore's Law](https://www.technologyreview.com/2016/05/13/245938/moores-law-is-dead-now-what/) to pick up the slack, we need to get creative to maximize the pace of progress.

Leveraging the fact that people are more likely to have access to [high-bandwidth connectivity](https://www.fiercetelecom.com/broadband/att-upgrades-its-fiber-network-offer-2-gig-5-gig-speeds) than to high-performance compute, Coacervate lets you run genomic analyses on an extremely low-cost [global supercomputer](https://www.golem.network). By using incredible open-source [tools](https://gatk.broadinstitute.org/hc/en-us) and [frameworks](https://snakemake.github.io/), this project aims to democratize access to the knowledge _and_ infrastructure required to carry out groundbreaking research.

Coacervate is a free and open-source public good, built to empower every citizen-scientist and eek out every last drop of efficiency in the name of progess.

## Quickstart:
- `docker run --rm -it coacervate/requestor`

  This will pull and run the requestor component of Coacervate. A Golem daemon is spun up in the container and the default Snakemake workflow is executed on test data bundled with the image. If you'd like to write the analysis output to your host please mount an empty directory using `-v /path/to/local/dir:/data/results/gather_out`.

## Status
⚠️⚠️⚠️ This project is currently a **Proof of Concept** and undergoing a *significant* refactor. The quickstart probably still works but is not representative of the new direction. Testing is very much under-construction.

## Approach
Coacervate accepts genomic sequence alignments and produces [joint called](https://gatk.broadinstitute.org/hc/en-us/articles/360035890431-The-logic-of-joint-calling-for-germline-short-variants) VCF files ready for annotation and actionable interpretation. This is achieved by splitting the inputs to parallelize the most [computationally intensive](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254363#pone-0254363-g003) step via the Golem Network. 


## Getting Started with Your Own Data
The recommended way of using Coacervate with your own data is to overwrite different files/directories in the requestor container with compatible equivalents from the host machine. For example, you can overwrite the config and input alignments with `-v /host/config:/data/config/config.yml` and ` -v /host/alignments:/data/results/alignments/full/`. Currently, inputs must be in the CRAM format. 

Please see the files and folders already in place to get an idea of the required formats. The directory structure is similar to the Snakemake [best-practices](https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#distribution-and-reproducibility):
```
├── config
│   └── config.yml
├── resources
│   └── reference
│       ├── resources_broad_hg38_v0_Homo_sapiens_assembly38.dict
│       ├── resources_broad_hg38_v0_Homo_sapiens_assembly38.fasta
│       └── resources_broad_hg38_v0_Homo_sapiens_assembly38.fasta.fai
├── results
│   └── alignments
│       └── full
│           ├── HG03633.cram
│           └── HG04149.cram
└── workflow
    ├── envs
    │   └── env.yml
    ├── logs
    ├── rules
    │   ├── benchmark.smk
    │   ├── local.smk
    │   └── utils.py
    ├── scripts
    │   └── requestor.py
    └── Snakefile
```

## Future Plans
- Distributed data storage in IPFS to remove 1-to-many data transfer bottleneck
- Fully fog-based, only access a portal from your browser
- FHE for clinical samples / sensitive data using [Zama](https://www.zama.ai/)
- Verifiable compute using [Risc Zero](https://www.risczero.com/)

### References
  - Stephens, Zachary D., et al. “Big Data: Astronomical or Genomical?” PLOS Biology, Public Library of Science, https://journals.plos.org/plosbiology/article?id=10.1371%2Fjournal.pbio.1002195. 
  - Heo, Go Eun, et al. “Analyzing the Field of Bioinformatics with the Multi-Faceted Topic Modeling Technique.” BMC Bioinformatics, BioMed Central, 31 May 2017, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5471940/.
  - John, Aji, et al. “Evaluation of Serverless Computing for Scalable Execution of a Joint Variant Calling Workflow.” PLOS ONE, Public Library of Science, https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254363.
