#!/bin/sh
#
# This script is used to generate a new release
#
# Guy Turcotte, December 2020
#

folder="Simple8chRelay.indigoPlugin"

if [ -f "$folder.zip" ]
then
  echo "File $folder.zip already exist!"
  return 1
fi

mkdir "$folder"

cp -r Contents "$folder"

zip -r "$folder.zip" "$folder"

rm -rf "$folder"

echo "Completed."
