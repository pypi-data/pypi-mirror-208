#!/bin/bash
#
# This script sets all necessary version-number information across
# FastJet (including doxygen and manual). It should be run from the
# top-level fastjet-release directory.
#

if [ $# -ne 1 ]
then
 echo "Usage: scripts/set-version.sh version-number"
 exit
fi

version=$1
echo "------------ Will set FastJet version to $version -----------" 

echo
echo "------------ Setting it in configure.ac ---------------------"
#sed -i.bak 's/\(AC_INIT.*\)])/\1-'$extralabel'])/' configure.ac
sed -i.bak 's/^\(AC_INIT(\[.*\],\[\).*/\1'$version'])/' configure.ac
diff configure.ac.bak configure.ac 
#AC_INIT([FastJet],[3.0.2-devel])

# now make sure the windows config file is consistent
echo
echo "------------ Setting it in include/fastjet/config_win.h -----"
cp -p include/fastjet/config_win.h include/fastjet/config_win.h.bak
cd src
./genconfig.sh ../include/fastjet/config_win.h
cd ..
diff include/fastjet/config_win.h.bak include/fastjet/config_win.h 

echo
echo "------------ Setting it in Doxyfile -------------------------"
sed -i.bak 's/^\(PROJECT_NUMBER.*=\).*/\1 '$version'/' Doxyfile
diff Doxyfile.bak Doxyfile


echo
echo "------------ Setting it in doc/fastjet-doc.tex --------------"
sed -i.bak 's/^\( *\)[^%]*\(%.*VERSION-NUMBER.*\)/\1'$version'\2/' doc/fastjet-doc.tex
diff doc/fastjet-doc.tex.bak doc/fastjet-doc.tex

echo
echo "------------ Recommended ChangeLog entry --------------------"
# NB: -e option of echo ensures that \t translates to a tab character
echo -e "\t* configure.ac:"
echo -e "\t* include/fastjet/config_win.h:"
echo -e "\t* Doxyfile:"
echo -e "\t* tex/fastjet-doc.tex:"
echo -e "\t  changed version to $version"
