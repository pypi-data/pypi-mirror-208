#!/bin/bash

# gen_sbo_txt.sh is a script to build a SLACKBUILDS.TXT file.
# Thanks to bassmadrigal from LQ forum.
# https://www.linuxquestions.org/questions/slackware-14/script-for-building-a-slackbuilds-txt-4175598436/

for i in */*; do

  NAME=$(echo $i | cut -d "/" -f2)
  FILES=$(ls $i)
  source $i/${NAME}.info
  DESCRIPTION=$(grep -m 1 $NAME $i/slack-desc | cut -d " " -f2-)

  echo SLACKBUILD NAME: $NAME
  echo SLACKBUILD LOCATION: ./$i
  echo SLACKBUILD FILES: $FILES
  echo SLACKBUILD VERSION: $VERSION
  echo SLACKBUILD DOWNLOAD: $DOWNLOAD
  echo SLACKBUILD DOWNLOAD_x86_64: $DOWNLOAD_x86_64
  echo SLACKBUILD MD5SUM: $MD5SUM
  echo SLACKBUILD MD5SUM_x86_64: $MD5SUM_x86_64
  echo SLACKBUILD REQUIRES: $REQUIRES
  echo SLACKBUILD SHORT DESCRIPTION: $DESCRIPTION
  echo

done
