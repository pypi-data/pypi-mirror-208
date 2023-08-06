from pathlib import Path

from setuptools import setup, find_packages

from excel_models import __version__

project_dir = Path(__file__).parent
try:
    long_description = (project_dir / 'README.md').read_text()
except FileNotFoundError:
    long_description = ''

requirements = (
    'openpyxl',
    'returns-decorator',
)

requirements_dev_lint = (
    'flake8',
    'flake8-commas',
    'flake8-quotes',
)

requirements_dev_test = (
    'pytest',
    'pytest-cov',
)

requirements_dev = (
    *requirements_dev_lint,
    *requirements_dev_test,
)

requirements_ci = (
    *requirements_dev_lint,
    *requirements_dev_test,
    'coveralls',
)

setup(
    name='excel-models',
    version=__version__,
    packages=find_packages(exclude=['tests', 'tests.*']),
    description='Model-style Excel File Accessor',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/MichaelKim0407/excel-models',
    license='MIT',
    author='Zheng Jin',
    author_email='mkim0407@gmail.com',

    python_requires='>=3.11',
    install_requires=requirements,
    extras_require={
        'dev': requirements_dev,
        'ci': requirements_ci,
    },

    classifiers=[
        'Intended Audience :: Developers',

        'Development Status :: 3 - Alpha',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',

        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
