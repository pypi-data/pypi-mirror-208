from setuptools import setup

def readme_file():
    with open("README.rst") as rf:
        return rf.read()

setup(
    name='scMet',
    version='1.0.3',
    author='Gw yang',
    author_email='stu_gwyang@163.com',
    description='Fits bulk RNA-seq data using single-cell RNA-seq (scRNA-seq) data, enabling accurate estimation and analysis of gene expression profiles and metabolic flux balance',
    long_description='',
    url='https://github.com/your_username/your_package',
    packages=['scMet'],
    install_requires=[
        'scanpy',
        'pandas',
        'combat==0.2.1',
        'numpy',
        'matplotlib',
        'sklearn',
        'tqdm',
        'scipy',
        'tensorflow',
        'anndata'
    ],
    python_requires='>=3.8',
)
