#!/bin/bash

# install.sh file is part of slpkg.

# Copyright 2014-2023 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__version() {
# Grab version from __metadata_.py file
cat setup.cfg | grep "version =" | tr -d "[:space:]" | cut -c9-13 | tr , .
}

PRGNAM=slpkg
VERSION=${VERSION:-$(__version)} 

ARCHIVES="$PRGNAM-$VERSION.tar.gz $PRGNAM-$VERSION.tar.bz2 $PRGNAM-$VERSION.zip"

cd ..
for file in $ARCHIVES; do
  if [ -f $file ]; then
    cp $file $PRGNAM-$VERSION/slackbuild
    cd $PRGNAM-$VERSION/slackbuild
    chmod +x $PRGNAM.SlackBuild
    ./$PRGNAM.SlackBuild
    rm $file
  fi
done 
