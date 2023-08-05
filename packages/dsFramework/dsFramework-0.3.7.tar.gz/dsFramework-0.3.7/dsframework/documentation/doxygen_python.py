import sys
import wget
import subprocess
import os
import pathlib
type = ''
if sys.argv and len(sys.argv) > 1:
    type = sys.argv[1]
if not type:
    raise Exception('type must be enter')
filename = ''
url = ''
if type == 'windows':
    filename = 'doxygen-1.9.4-setup.exe'
    url = f'https://www.doxygen.nl/files/{filename}'
if type == 'linux':
    filename = 'install.sh'
    url = f'https://raw.githubusercontent.com/Homebrew/install/HEAD/{filename}'
if not filename:
    raise Exception('type not supported')
if not os.path.exists(filename):
    filename = wget.download(url)
path = pathlib.Path(__file__).parent.resolve()
finalPath = os.path.join(path, filename)
process = [finalPath]
if type == 'linux':
    process = [f'chmod +x {finalPath}'] + process
p = subprocess.Popen(process, bufsize=2048, shell=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
p.wait()
result_str = p.stdout.read()
os.remove(filename)
