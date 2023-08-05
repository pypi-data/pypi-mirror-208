from argparse import ArgumentParser as _ArgumentParser
from zipfile import ZipFile as _ZipFile
import os as _os
import site as _site


def create(path: str = '.', name: str = 'template'):
    root = _os.path.join(_site.getsitepackages()[1], 'apidevtools')
    with _ZipFile(_os.path.join(root, 'template', 'template.zip'), 'r') as template_zip_file:
        template_zip_file.extractall(path)
    _os.rename(_os.path.join(path, 'template'), _os.path.join(path, name))


if __name__ == '__main__':
    parser = _ArgumentParser()
    parser.add_argument('--path')
    parser.add_argument('--name')
    args = parser.parse_args()
    args = {'path': args.path, 'name': args.name}

    create(args.get('path'), args.get('name'))
