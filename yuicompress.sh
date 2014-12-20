#!/bin/bash
#
# yuicompress.sh - easy use of yuicompressor (http://yui.github.io/yuicompressor/)
#
# Open Source. No License.

YUICOMPRESSOR_HOME=/opt/yuicompressor

verbose=false
quiet=false

while getopts "qv" opt; do
  case $opt in
    q)
      quiet=true
      ;;
    v)
      verbose=true
      ;;
    \?)
      exit 1
      ;;
  esac
done

for file in `find . -name "*.js" -o -name "*.css" -print | sort`
do
    if [ $verbose == "true" ]; then
        echo "Compressing $file"
    elif [ $quiet == "true" ]; then
        :
    else
        echo -n "."
    fi

    java -jar $YUICOMPRESSOR_HOME/yuicompressor.jar -o $file $file
done

echo ""

exit 0
