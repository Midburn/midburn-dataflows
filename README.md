# Midburn DataFlows

Data processing and aggregation pipelines for debugging and management of Midburn infrastructure.

## Install midburn-dataflows

See [environment.yaml](environment.yaml) for the required system dependencies.

To get started quickly on any modern OS you can use [Miniconda](https://conda.io/miniconda.html)

The following snippet will install Miniconda on recent Linux distributions:

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

Create and activate the conda environment

```
conda env create -f environment.yaml
conda activate midburn-dataflows
```

To update the dependencies of the active conda environment to the latest version (e.g. after a git pull):

```
conda env update -f environment.yaml
```

Install the midburn-dataflows Python package

```
python3 -m pip install -e .
```

## Running flows

Depending on the flows you want to run you will need to authenticate / config some prerequisites:

* kubectl connected to a [midburn-k8s](https://github.com/Midburn/midburn-k8s) environment with cluster admin permissions

Run all the flows:

```
for FLOW in $(ls flows); do python3 "flows/${FLOW}"; done
```

The flows store data as [tabular data packages](https://frictionlessdata.io/specs/tabular-data-package/) under `data/` directory (not committed)
