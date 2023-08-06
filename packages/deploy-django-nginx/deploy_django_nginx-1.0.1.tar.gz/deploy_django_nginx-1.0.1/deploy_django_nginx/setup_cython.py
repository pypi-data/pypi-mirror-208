from setuptools import setup, find_packages
from Cython.Build import cythonize


API_ROOT = '/data2/work/suqingdong/code/deploy_django_nginx/tests/demo/api'


setup(
    ext_modules=cythonize(
        '**/*.py',
        language_level='3',
        exclude=['manage.py'],
        nthreads=16,
    ),
    package_dir={'': API_ROOT},
    # data_files=[
    #     (
    #         'api_build',
    #         ['manage.py']
    #     ),
    # ],
    # script_args=[
    #     'build_ext', '-b', 'api_build',
    #     # 'clean',
    # ],
)
