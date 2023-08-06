.. |License Badge| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT

Introduction
============

zsMet is a CVAE model trained on scRNA-seq data to generate new and
realistic scRNA-seq data. The generated data can then be used to fit
bulk RNA-seq data, enabling the estimation and analysis of gene
expression profiles and metabolic flux balance.

Installation
============

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/yourusername/yourrepository.git

2. Navigate to the project directory:

   .. code-block:: bash

      cd yourrepository

3. Set up a virtual environment.

   For Linux/Mac:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate

   For Windows:

   .. code-block:: bash

      python -m venv venv
      venv\Scripts\activate

4. Install the dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

5. Run the application:

   .. code-block:: bash

      python main.py

Dependencies
------------

-  scanpy
-  pandas
-  combat
-  numpy
-  warnings
-  matplotlib
-  sklearn
-  tqdm
-  scipy
-  tensorflow
-  random
-  anndata

Steps
=====

1. Reading and Merging Single-cell Gene Expression Data
------------------------------------------------------

2. Batch Correction of Simulated and Real Bulk RNA-seq Data
----------------------------------------------------------

3. Preprocessing of Single-cell Gene Expression Data for Deconvolution
---------------------------------------------------------------------

4. Training CVAE-GAN Model for Generating Single-cell Data
--------------------------------------------------------

5. Generating and Filtering Simulated Single-cell Data
-----------------------------------------------------

6. Fitting Bulk RNA-seq Data using Selected Single-cell Data
-----------------------------------------------------------
