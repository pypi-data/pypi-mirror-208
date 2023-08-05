#!/bin/sh
FOLDER='bin'
DEACTIVATE='deactivate'

case "$(uname -s)" in

   Darwin)
     echo 'Mac OS X'
     FOLDER='bin'
     ;;

   Linux)
     echo 'Linux'
     FOLDER='bin'
     ;;

   CYGWIN*|MINGW32*|MSYS*|MINGW*)
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

virtualenv env_1 -p python
source ./env_1/${FOLDER}/activate
./env_1/${FOLDER}/pip3 install -r requirements.txt
venv-pack -p env_1 -o dist/pyspark_venv.tar.gz -f
# env_1/${FOLDER}/${DEACTIVATE}
deactivate
