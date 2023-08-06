#!/bin/bash
export OMP_NUM_THREADS=16
export PYTHONPATH=.

# source .env

target_folder=
source_pattern="*"
tag=
force=0
update=1
max_procs=1
now_timestamp=$(date "+%Y%m%d_%H%M%S")
log_dir=./logs

function usage()
{
    echo "usage: tag-it [--data-folder folder] [--source-pattern pattern] --target-folder folder --tag tag [--force]"
    echo "Creates new database using source as template. Source defaults to production."
    echo ""
    echo "   --data-folder             source root folder"
    echo "   --target-folder           target folder"
    echo "   --tag                     source corpus tag"
    echo "   --source-pattern          source folder pattern"
    echo "   --force                   drop target if exists"
    echo "   --update                  update target if exists"
    echo "   --max-procs               max number of parallel jobs"
    echo ""
}

data_folder=/data/riksdagen_corpus_data

POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        --source-pattern)
            source_pattern="$2"; shift; shift
        ;;
        --tag)
            tag="$2"; shift; shift
        ;;
        --data-folder)
            data_folder="$2"; shift; shift
        ;;
        --target-folder)
            target_folder="$2"; shift; shift
        ;;
        --max-procs)
            max_procs="$2"; shift; shift
        ;;
        --force)
            force=1 ;
        ;;
        --update)
            update=1 ;
        ;;
        --help)
            usage ;
            exit 0
        ;;
        *)
        POSITIONAL+=("$1")
        shift
        ;;
    esac
done

set -- "${POSITIONAL[@]}"


if [ ! -d "$data_folder" ]; then
    echo "error: data folder doesn't exist"
    usage
    exit 64
fi

if [ "$tag" == "" ]; then
    echo "error: tag not specified" ;
    usage
    exit 64
fi

if [ "$target_folder" == "" ]; then
    echo "error: target folder not specified" ;
    usage
    exit 64
fi

if [ -d "$target_folder" ]; then
    if [ $force == 1 ]; then
        echo "info: dropping existing target" ;
        echo rm -rf $target_folder ;
    elif [ $update == 0 ]; then
        echo "error: target folder exists (use --force or --update to remove/update existing tagging)" ;
        exit 64 ;
    fi
fi

if [[ $max_procs < 1 || $max_procs > 6 ]]; then
    echo "error: max procs bust be an integer between 1 and 6" ;
    exit 64
fi

mkdir -p $log_dir

repository_folder=${data_folder}/riksdagen-corpus
corpus_folder=${repository_folder}/corpus/protocols

workdir_tag=undefined
if type "$tag_info" > /dev/null; then
    workdir_tag=$(tag_info --key tag /data/riksdagen_corpus_data/riksdagen-corpus)
else
    export PYTHONPATH=.
    workdir_tag=$(poetry run python scripts/tag_info.py --key tag /data/riksdagen_corpus_data/riksdagen-corpus)
    # echo "error: tag_info not found - unable to verify that workdir tag id ${tag}"
    # exit 64 ;
fi

if [ "$tag" != "$workdir_tag" ]; then
    echo "error: workdir tag is $workdir_tag, expected ${tag}" ;
    exit 64 ;
fi

tag_info $repository_folder > ${target_folder}/version.yml

sub_folders=`find ${corpus_folder} -maxdepth 1 -mindepth 1 -name "${source_pattern}" -type d -printf '%f\n' | sort`

yaml_file=$log_dir/tag_config_${now_timestamp}.yml

cat <<EOF > $yaml_file
root_folder: ${data_folder}
source_folder: ${corpus_folder}
target_folder: ${target_folder}
repository_folder: ${repository_folder}
repository_tag: ${tag}
EOF
echo "yml file: $yaml_file"
cat $yaml_file

echo "processes: $max_procs"
echo "force: $force"

if [[ $max_procs > 1 ]]; then

    tagit_command_file="$log_dir/tagit_commands_${now_timestamp}.txt"

    echo "command file: $tagit_command_file"

    rm -rf $tagit_command_file

    for sub_folder in $sub_folders; do
        echo "poetry run python ./scripts/tag.py ${corpus_folder}/$sub_folder ${target_folder}/$sub_folder $yaml_file" >> ${tagit_command_file}
    done

    echo "info: running in parallel mode using $max_procs processes"
    cat $tagit_command_file | xargs -I CMD --max-procs=4 bash -c CMD

else
    echo "info: running in sequential mode"
    for sub_folder in $sub_folders; do
        PYTHONPATH=. python ./scripts/tag.py ${corpus_folder}/$sub_folder ${target_folder}/$sub_folder $yaml_file
    done
fi
