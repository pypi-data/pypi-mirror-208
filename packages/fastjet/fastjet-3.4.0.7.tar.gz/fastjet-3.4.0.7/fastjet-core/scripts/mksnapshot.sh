#!/bin/bash

# check whether all is committed
if [[ `svn status | grep -v -e '^X' -e external | egrep -e '^[A-Z]' | wc -l` -gt 0 ]] ; then
 echo "ERROR: working copy has local changes"
 exit -1
fi

# get an up to date version
svn update || exit -1

# get the revision number 
rev=`svn info | grep Revision | sed s'/[^0-9]*//'`
# and then generate an extra label for the version number, including also the date
extralabel=`date +"%Y%m%d"`-rev$rev
echo "Extra label is: $extralabel"

#----------------------------------------------------------------------
# Create a new tarball (and then put things back to normal)
#
# update version numbers in some critical files (why not use ./scripts/set-version ???)
sed 's/\(AC_INIT.*\)])/\1-'$extralabel'])/' < configure.ac > configure.ac.new
mv configure.ac.new configure.ac
pushd src
./genconfig.sh ../include/fastjet/config_win.h
popd

# now make and test the distribution 
make -j4 distcheck 

# and put the configure file back to where it was
svn revert configure.ac
svn revert include/fastjet/config_win.h

# then get things ready for the output for manual operations
filename=`ls -rt *$extralabel*.tar.gz | tail -1`
filebase=`echo $filename | sed 's/.tar.gz//'`

#----------------------------------------------------------------------
# create a patch file corresponding to the edits needed for the snapshot file
remoteSnapshotHTML='tycho.lpthe.jussieu.fr:~salam/www/fastjet3/snapshots.html'
oldSnapshotHTML='/tmp/snapshots-incoming.html'
newSnapshotHTML='/tmp/snapshots-'$extralabel.html
diffSnapshotHTML='/tmp/snapshots-diff-'$extralabel.html
scp -p $remoteSnapshotHTML $oldSnapshotHTML
if [[ -e $newSnapshotHTML ]]; then
    rm $newSnapshotHTML
fi
touch $newSnapshotHTML
addedLine=false
while IFS='' read -r line || [[ -n "$line" ]]; do
    echo "$line" >> $newSnapshotHTML
    if [[ $line =~ 'ul id=snapshots' ]]; then
        echo '    <li> <a href="repository/snapshots/'"$filename"'">'"$filename"'</a>' >> $newSnapshotHTML
        addedLine=true
    fi
done < "$oldSnapshotHTML"
# if we were successful then 
if [[ $addedLine ]]; then
    diff -u $oldSnapshotHTML $newSnapshotHTML > $diffSnapshotHTML
    echo "Snapshot file diff created as $diffSnapshotHTML"
    cat $diffSnapshotHTML
else
    echo "Failed to correctly create $newSnapshoHTML"
fi

#----------------------------------------------------------------------
# and tell the user you have a result and what they should do
echo "**************************************************"
echo "Have produced the file: $filename"
echo Now run 
echo scp -p $filename tycho.lpthe.jussieu.fr:'~'salam/www/fastjet/repository/snapshots/
echo svn cp svn+ssh://tycho.lpthe.jussieu.fr/ada1/lpthe/salam/svn/fastjet/trunk/fastjet-release svn+ssh://tycho.lpthe.jussieu.fr/ada1/lpthe/salam/svn/fastjet/tags/snapshots/$filebase -m \'tagged $filebase snapshot\'
echo

# watch out: we apply a patch so as not to modify special permissions on the file
# (e.g. fastjet group write access, +x flag, etc.)
if [[ $addedLine ]]; then
    echo "scp -p $diffSnapshotHTML tycho.lpthe.jussieu.fr:$diffSnapshotHTML"
    echo "ssh tycho.lpthe.jussieu.fr patch /ada1/lpthe/salam/www/fastjet3/snapshots.html $diffSnapshotHTML"
fi
