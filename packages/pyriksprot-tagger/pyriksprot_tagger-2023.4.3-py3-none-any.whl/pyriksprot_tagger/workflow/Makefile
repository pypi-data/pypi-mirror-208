include .env

.DEFAULT_GOAL=help
SHELL:=/bin/bash

.DELETE_ON_ERROR:

ifndef RIKSPROT_DATA_FOLDER
$(error RIKSPROT_DATA_FOLDER is undefined)
endif

RIKSPROT_REPOSITORY_FOLDER := $(RIKSPROT_DATA_FOLDER)/riksdagen-corpus

PYPROJECT := $(shell test -f pyproject.toml && echo -n "yes")
ifeq ($(strip $(PYPROJECT)), yes)
	POETRY=poetry run
else
	POETRY=
endif

OPTS =

# CUSTOM_CONFIG := $(shell test -f config.yml && echo -n "yes")
# ifeq ($(strip $(PYPROJECT)), yes)
# 	OPTS := --configfile ./config.yml --config CUSTOM_CONFIG=true
# endif

ifdef YEAR
OPTS := $(OPTS) year_filter=$(YEAR)
endif

ifdef DISABLE_GPU
OPTS := $(OPTS) disable_gpu=1
endif

ifdef PROCESSES_COUNT
OPTS := $(OPTS) processes=$(PROCESSES_COUNT)
endif

ifneq ($(OPTS),)
OPTS := --config $(OPTS)
endif

# ifdef BATCH_DIVISOR
# OPTS := $(OPTS) --batch tag_protocols=1/$(BATCH_DIVISOR)
# endif

.PHONY: clean
clean:
	@$(POETRY) snakemake -j1 --cleanup-shadow

.PHONY: unlock
unlock:
	@$(POETRY) snakemake -j1 --unlock

.PHONY: init-repository
init-repository:
	@$(POETRY) snakemake -j1 init_repository

.PHONY: tf
tf:
	@$(POETRY) snakemake -j4 word_frequency $(OPTS)

# update-repository:
# 	@$(POETRY) snakemake -j1 update_repository

create-full-repository: full-clone-repository update-repository-timestamps
	@echo "full clone is done!"

.PHONY: full-clone-repository
ONESHELL: full-clone-repository
full-clone-repository:
	@pushd . \
	&& mkdir -p $(RIKSPROT_DATA_FOLDER) \
        && cd $(RIKSPROT_DATA_FOLDER) \
        && rm -rf $(RIKSPROT_REPOSITORY_FOLDER) \
        && git clone $(RIKSPROT_REPOSITORY_URL) \
        && cd $(RIKSPROT_REPOSITORY_FOLDER) \
        && git config core.quotepath off \
        && popd

.PHONY: full-pull-repository
ONESHELL: full-pull-repository
full-pull-repository:
	@pushd . \
	&& cd $(RIKSPROT_REPOSITORY_FOLDER) \
	&& git pull \
	&& popd

.PHONY: update-repository-timestamps
.ONESHELL: update-repository-timestamps
update-repository-timestamps:
	@curl -s https://raw.githubusercontent.com/MestreLion/git-tools/main/git-restore-mtime -o /tmp/git-restore-mtime \
		&& pushd . \
		&& cd $(RIKSPROT_REPOSITORY_FOLDER) \
		&& pwd \
		&& python /tmp/git-restore-mtime --commit-time \
		&& popd

.PHONY: shallow-update-repository
ONESHELL: shallow-update-repository
shallow-update-repository:
	@pushd . \
	&& mkdir -p $(RIKSPROT_DATA_FOLDER) \
        && cd $(RIKSPROT_DATA_FOLDER) \
        && rm -rf $(RIKSPROT_REPOSITORY_FOLDER) \
        && git clone --branch $(RIKSPROT_REPOSITORY_TAG) --depth 1 $(RIKSPROT_REPOSITORY_URL) \
        && cd $(RIKSPROT_REPOSITORY_FOLDER) \
        && git config core.quotepath off \
        && popd

# .PHONY: update-repository-timestamps-snakemake
# update-repository-timestamps-snakemake:
# 	# @if [[ "$$OS" == "Windows_NT" ]]; then
# 	# 	echo "note: Windows OS detected. Please run from Git BASH CLI instead"
# 	# 	echo "usage: scripts/git_update_mtime.sh $(RIKSPROT_DATA_FOLDER)/riksdagen-corpus"
# 	# 	exit 0
# 	# fi
# 	@$(POETRY) snakemake -j1 update_repository_timestamps

.PHONY: annotate
.PHONY: help-workflow clean-workflow
.PHONY: extract-speeches-workflow
.PHONY: dag-workflow dag-pdf-workflow

annotate:
	@$(POETRY) snakemake -j$(PROCESSES_COUNT) --keep-going --keep-target-files --rerun-incomplete $(OPTS)

extract-speeches-workflows:
	@echo "This recipe is deprecated"
	@echo "$(POETRY) snakemake -p -j4"

workflow-dag:
	@$(POETRY) snakemake --dag | dot | display

workflow-dag-pdf:
	@$(POETRY) snakemake --dag | dot -Tpdf > dag.pdf

clean-workflow:
	@$(POETRY) snakemake -j1 --delete-all-output

lint-workflow:
	@$(POETRY) snakemake -j1 lint

test-workflow:
	@$(POETRY) snakemake -j1 --config config_filename=test_config.yml

help-workflow:
	@echo "Higher level recepies: "
	@echo " make clean-workflow					Clean target Snakemake folder"
	@echo " make init-repository				Create shallow clone of Para-Clarin repository"
	@echo " make update_repository				Shallow update of Para-Clarin repository"
	@echo " make update-repository-timestamps   Update file modify dates of files checked out from repository"
	@echo " make extract-speeches-workflow		Extract speeches from ParaClarin XML corpus"
	@echo " make test-workflow					Runs against test repository"
	@echo " make help-workflow  				Display this message"
	@echo " make lint-workflow					Run Snakemake's linter"
	@echo "  "
