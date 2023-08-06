#!/bin/bash
# Downloads stanza pre-trained models from Språkbanken

STANZA_MODELS_URL=https://svn.spraakdata.gu.se/sb-arkiv/pub/stanza
TARGET_FOLDER=/data/sparv/models/stanza

mkdir -p $TARGET_FOLDER

if [ ! -f $TARGET_FOLDER/resources.json ]; then
    cat << EOF > $TARGET_FOLDER/resources.json
{
    "sv": {
        "lang_name": "Swedish",
        "tokenize": {
            "orchid": {},
            "best": {}
        },
        "default_processors": {
            "tokenize": "orchid"
        },
        "default_dependencies": {
        }
    }
}
EOF
fi

download() {

    source_file=$1
    folder=$2

    mkdir -p $TARGET_FOLDER/$folder

    wget --output-document ${source_file}.zip $STANZA_MODELS_URL/${source_file}.zip
    unzip -o ${source_file}.zip -d $TARGET_FOLDER/$folder
    rm -f ${source_file}.zip

}

pushd .

cd $TARGET_FOLDER

wget -O version.html https://svn.spraakdata.gu.se/sb-arkiv/pub/stanza/

download stanza_pretrain
download morph_stanza_full2 pos
download lem_stanza lem
download synt_stanza_full2 dep

download morph_stanza_full pos

popd
