# Riksdagens Protokoll Part-Of-Speech Tagging

This package implements part-of-speech tagging of `Riksdagens Protokoll` Parla-CLARIN XML files.

## Update riksprot tagger system

If **pyriksprot_tagger** repository folder already exists:

```bash
% cd "pyriksprot-tagger-folder"
% git pull
```

If repository folder doesn't exist:

```bash
% cd "some-folder"
% git clone git@github.com:welfare-state-analytics/pyriksprot_tagger.git
```

## Update configuration

Update configurational elements in "pyriksprot-tagger-folder"/.env:

| Environment variable | Description |
| --- | --- |
| RIKSPROT_DATA_FOLDER | Parent folder (location) of Riksdagens corpus data folder |
| RIKSPROT_REPOSITORY_URL |  https://github.com/welfare-state-analytics/riksdagen-corpus.git |
| RIKSPROT_REPOSITORY_TAG | Target corpus version. Must be a valid Github tag |
| SPARV_DATADIR | Sparv data folder |
| STANZA_DATADIR | Stanza data folder |
| OMP_NUM_THREADS | Number of threads to use |

```env
RIKSPROT_DATA_FOLDER="/data/riksdagen_corpus_data"
RIKSPROT_REPOSITORY_URL="https://github.com/welfare-state-analytics/riksdagen-corpus.git"
RIKSPROT_REPOSITORY_TAG="v0.4.5"
SPARV_DATADIR="/data/sparv"
STANZA_DATADIR="/data/sparv/models/stanza"
OMP_NUM_THREADS=10
```

## Create or update Riksdagens Corpus data repository

```bash
% cd "pyriksprot-tagger-folder"
# If you want to create a new clone of the repository:
% make full-clone-repository
# If you want to update existing repository:
% make full-pull-repository
# If you want to save space a do a shallow clone
% make shallow-update-repository
# Update timestamp of repository work folder files to match last commit timestamp (important!):
% make update-repository-timestamps
```

## Update / tag a new version of RIKSPROT:

Prerequisites:
 - [ ] Pull latest version of **welfare-state-analytics/pyriksprot_tagger**
 - [ ] Update configuration (see above)

If you want to use snakemake:
 - [ ] Edit options (target name) in workflow/config/config.yml
 - [ ] Run **make annotate** (ca: 10 hours run time)

If you want to use **tag-it** script (preferred, faster):

 - [ ] Run **PYTHONPATH=. nohup ./tag-it.sh > tag-it.version.log &**

## Create metadata database:

 - [ ] Pull or clone latest version of **welfare-state-analytics/pyriksprot**
 - [ ] Update configuration (specify tag) to use in **pyriksprot/.env**
 - [ ] Run **make metadata**

## Create speech corpus

 - [ ] Pull or clone latest version of **welfare-state-analytics/pyriksprot**
 - [ ] Update configuration (specify tag) to use in **pyriksprot/.env**
 - [ ] Run make extract-speeches-to-feather


## How to annotate protocols using snakemake (not recommended)


 - Annotate using default settings.
```bash
make annotate
```

 - Update a single year (and set cpu count).

```bash
make annotate YEAR=1960 CPU_COUNT=1
```

 - Call snakemake directly:

```bash
$ nohup make annotate PROCESSES_COUNT=4 >& run.log &
or
$ nohup poetry run snakemake -j4 --keep-going --keep-target-files &
```

```bash
nohup poetry run snakemake --config -j4 --keep-going --keep-target-files &
```

## Install from PyPI (not recommended)

Verify current Python version (`pyenv` is recommended for easy switch between versions).

 - Create a new Python virtual environment (sandbox):

```bash
cd /some/folder
mkdir riksprot_tagging
cd riksprot_tagging
python -m venv .venv
source .venv/bin/activate
```

 - Install the pipeline and run setup script.

```bash
pip install pyriksprot_tagger
setup-pipeline
```

To tag protocols you first need to activate the installed environment, and then follow steps above on how to tag protocols using snakemake.


```bash
cd /some/folder/pyriksprot
source .venv/bin/activate
```
