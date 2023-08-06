#!/bin/bash
# move_missing_speech_tag()
# {
#     find ./speech_xml/ -type f ! -exec grep -q 'speech' {} \; -print > empty_protocols/filenames.txt
#     find ./speech_xml/ -type f ! -exec grep -q 'speech' {} \; -print0 | xargs -0 -I {} mv {} ./empty_protocols
# }

move_empty_speech_tags()
{
    filename=$1
    content=`xmlstarlet sel -t -m "//speech" -v . $filename | grep -q '[^[:space:]]'`
    if [ "$content" == "" ] ; then
        echo "$filename is empty"
    fi
}

find ./source -type f |  while read filename; do move_empty_speech_tags "$filename"; done
