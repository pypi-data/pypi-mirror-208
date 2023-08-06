# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['unpast', 'unpast.utils']

package_data = \
{'': ['*']}

install_requires = \
['fisher==0.1.10',
 'jenkspy==0.2.0',
 'kneed>=0.8.3,<0.9.0',
 'matplotlib-venn==0.11.6',
 'numba==0.55.2',
 'numpy==1.22.3',
 'pandas==1.4.2',
 'python-louvain==0.15',
 'scikit-learn==1.1.0',
 'scikit-network==0.25.0',
 'scipy==1.7.3',
 'statsmodels==0.13.2']

entry_points = \
{'console_scripts': ['run_unpast = unpast.run_unpast:main']}

setup_kwargs = {
    'name': 'unpast',
    'version': '0.1.6',
    'description': 'A novel method for unsupervised patient stratification.',
    'long_description': '# UnPaSt\n\nUnPaSt is a novel method for identification of differentially expressed biclusters in gene expression matrix. It searches for gene sets up- or down-regulated in subsets of samples:\n\n![alt text](https://github.com/ozolotareva/DESMOND2/blob/a26d8d7b2075d47a4edc8fc9ce7eca72a2dac7db/poster/DESMOND2_steps2.png?raw=true)\n\n\nWebserver: https://unpast.zbh.uni-hamburg.de/\n\n## Installation\nThis UnPaSt can be installed using `pip./poster/DESMOND2.png`, `poetry`, run using `Docker`, or as a script (see examples section). Follow the appropriate instructions below for your preferred method.\nYou need to have R (for WGCNA, it is suggested to use v.1.70-3) and **Python 3.8-3.10** installed. The main reason why Python 3.11 is not supported is because Scikit-network does not support it now.\n\n**Using different Python versions, even with the same libraries versions, leads to slightly different computational results.**\n\n1. Using pip: \\\nTo install the project using `pip`, first make sure you have `pip` installed on your system. If you haven\'t installed it already, you can find the installation instructions [here](https://pip.pypa.io/en/stable/installation/). \\\nOnce `pip` is installed, you can install the project by running the following command:\n```bash\npip install unpast\n```\nRun it:\n```bash\nrun_unpast -h\n```\n**Dependencies**. To use this package, you will need to have R and the [WGCNA library](https://horvath.genetics.ucla.edu/html/CoexpressionNetwork/Rpackages/WGCNA/) installed. You can easily install these dependencies by running the following command after installing unpast:\n```bash\npython -m unpast.install_r_dependencies\n\n# or you can install it directly\nR -e "install.packages(\'BiocManager\'); BiocManager::install(\'WGCNA\')"\n```\n2. Installation using Poetry: \\\nTo install the package using Poetry, first make sure you have Poetry installed, clone the repo and then run:\n```bash\npoetry add unpast\n```\nRun it:\n```bash\npoetry run run_unpast -h\n```\n**Dependencies**. To use this package, you will need to have R and the [WGCNA library](https://horvath.genetics.ucla.edu/html/CoexpressionNetwork/Rpackages/WGCNA/) installed. You can easily install these dependencies by running the following command after installing unpast:\n```bash\npoetry run python -m unpast.install_r_dependencies\n\n# or you can install it directly\nR -e "install.packages(\'BiocManager\'); BiocManager::install(\'WGCNA\')"\n```\n3. Running with Docker: \\\nYou can also run the package using Docker. First, pull the Docker image:\n```bash\ndocker pull freddsle/unpast:latest\n```\nNext, run the container:\n```bash\ndocker run -v /your/data/path/:/user_data/ freddsle/unpast:latest --exprs /user_data/exprs.tsv --out_dir /user_data/out_dir/\n```\n\n## Examples\n* UnPaSt requires a tab-separated file with standardized expressions of genes (or transcripts) in rows, and samples in columns. Gene and sample names must be unique. \n* A subset of 200 randomly chosen samples from TCGA-BRCA and UnPaSt output:\n[test data](https://unpast-backend.zbh.uni-hamburg.de/download_example)\n\n<pre>\n# running UnPaSt with default parameters and example data\npython ./unpast/run_unpast.py --exprs TCGA_200.exprs_z.tsv --basename TCGA_200_results\n\n# with different binarization and clustering methods\npython ./unpast/run_unpast.py --exprs TCGA_200.exprs_z.tsv --basename results --binarization ward --clustering WGCNA\n\n# help\npython ./unpast/run_unpast.py -h\n</pre>\n\n## Outputs\n* \\<basename\\>.bin=[GMM|Jenks],clust=[Louvain|WGCNA|DESMOND].biclusters.tsv - a .tsv table with found biclsuters, where \n    - avgSNR is average SNR over all genes in the biclusters\n    - columns "n_genes" and "n_samples" provide the numbers of genes and samples, respectively \n    - "gene","sample" contain gene and sample names respectively\n    - "gene_indexes" and  "sample_indexes" - 0-based gene and sample indexes in the input matrix.\n* binarized expressions, background distributions of SNR for each bicluster size and binarization statistics [if clustering is WGCNA,  or  \'--save_binary\' flag is added]\n* modules found by WGCNA [if clustering is WGCNA]\n\n# About \nUnPaSt is an unconstrained version of DESMOND method ([repository](https://github.com/ozolotareva/DESMOND), [publication](https://academic.oup.com/bioinformatics/article/37/12/1691/6039116?login=true))\n\nMajor modifications:\n * it does not require the network of gene interactions \n * UnPaSt clusters individual genes instead of gene pairs\n * uses Gaussian mixture models or Jenks method for binarization of individual gene expressions\n * SNR threshold is authomatically determined; it depends on bicluster size in samples and user-defined p-value cutoff\n \n## License\nFree for non-for-profit use. For commercial use please contact the developers. \n\n### Poster CDCS workshop\'22\n![./poster/DESMOND2_poster_v5.png](https://github.com/ozolotareva/DESMOND2/blob/a26d8d7b2075d47a4edc8fc9ce7eca72a2dac7db/poster/DESMOND2_poster_v5.png?raw=true)\n### Poster ISMB and MCCMB\'21\n![./poster/DESMOND2.pdf](https://github.com/ozolotareva/DESMOND2/blob/a26d8d7b2075d47a4edc8fc9ce7eca72a2dac7db/poster/DESMOND2.png?raw=true)\n',
    'author': 'Olga Zolotareva (ozolotareva)',
    'author_email': 'None',
    'maintainer': 'Olga Zolotareva (ozolotareva)',
    'maintainer_email': 'None',
    'url': 'https://github.com/ozolotareva/DESMOND2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
