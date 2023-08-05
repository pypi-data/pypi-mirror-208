#!/bin/sh
FOLDER='bin'
DEACTIVATE='deactivate'

case "$(uname -s)" in

   Darwin)
     pip install wget
     python doxygen_python.py linux
     brew install doxygen graphviz gnu-sed
     echo 'Mac OS X'
     FOLDER='bin'
     ;;

   Linux)
     pip install wget
     python doxygen_python.py linux
     brew install doxygen graphviz gnu-sed
     echo 'Linux'
     FOLDER='bin'
     ;;

   CYGWIN*|MINGW32*|MSYS*|MINGW*)
     pip install wget
     python doxygen_python.py windows
     echo 'MS Windows'
     FOLDER='Scripts'
     DEACTIVATE='deactivate.bat'
     ;;

   # Add here more strings to compare
   # See correspondence table at the bottom of this answer

   *)
     echo 'Other OS'
     ;;
esac
