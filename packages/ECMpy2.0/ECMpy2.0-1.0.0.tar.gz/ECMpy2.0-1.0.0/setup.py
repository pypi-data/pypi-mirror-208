from setuptools import setup, find_packages

setup(
    name='ECMpy2.0',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'cobra',
        'openpyxl',
        'requests',
        'pebble',
        'xlsxwriter',
        'Bio',
        'Require',
        'quest',
        'scikit-learn',
        'RDKit',
        'seaborn',
        'pubchempy',
        'torch',
        'ipykernel',
        'matplotlib',
    ],
    author='Zhitao Mao',
    author_email='mao_zt@tib.cas.cn',
    description='Automated construction of enzyme constraint models using ECMpy workflow.',
    url='https://github.com/tibbdc/ECMpy2.0',
)
