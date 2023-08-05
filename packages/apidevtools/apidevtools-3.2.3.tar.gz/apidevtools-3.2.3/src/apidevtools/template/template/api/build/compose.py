from subprocess import Popen, PIPE
from os import path


file = path.abspath('compose.yml')
command = f'docker-compose -p postgres -f {file} up -d --build'
print(f'{command}')
process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE)
out, err = process.communicate()
print(f'{out.decode()}')
