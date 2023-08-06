import os
from pathlib import Path

# from distutils.core import setup, Extension
from setuptools import setup, Extension, find_packages

from Cython.Build import cythonize


def get_all_files_by_suffix(path, suffix='.py'):
    """
    递归生成指定目录及其所有子目录下所有.py文件的路径
    """
    for item in Path(path).iterdir():
        if item.is_file() and item.suffix == suffix:
            yield item
        elif item.is_dir():
            yield from get_all_files_by_suffix(item, suffix=suffix)


def build_cython(path, language_level='3', build='build2'):

    print(f'>>> origin path: {path}')
    print(f'>>> build dir: {build}')

    # extensions = [str(file) for file in get_all_files_by_suffix(path, suffix='.py')]

    # extensions = [
    #     Extension(
    #         str(file.relative_to(path)).replace(file.suffix, '').replace(os.path.sep, '.'),
    #         [str(file)]
    #     ) for file in get_all_files_by_suffix(path, suffix='.py')
    # ]

    # print(extensions[30])

    setup(
        ext_modules=cythonize(
            '**/*py',
            # extensions,
            exclude=['manage.py'],
            language_level=language_level,
            nthreads=8,
            build_dir=build,
            working_path=f'{build}_temp'
        ),
        script_args=[
            'build_ext',
            # '--help',
            f'--build-lib={build}',
            f'--build-temp={build}_temp',
            'clean',
        ],
    )


if __name__ == '__main__':
    build_cython('/data2/work/suqingdong/code/deploy_django_nginx/tests/demo/api')
