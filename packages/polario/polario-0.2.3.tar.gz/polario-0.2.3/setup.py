# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['polario']

package_data = \
{'': ['*']}

install_requires = \
['fsspec>=2023.1.0,<2024.0.0', 'polars>=0.16.8', 'pyarrow>=11.0.0']

entry_points = \
{'console_scripts': ['polario = polario.main:main']}

setup_kwargs = {
    'name': 'polario',
    'version': '0.2.3',
    'description': 'Polars IO',
    'long_description': 'Polars IO utility library\n=================\n\nHelpers to make it easier to read and write Hive partitioned parquet dataset with Polars.\n\nIt is meant to be a library to deal with datasets easily, but also contains a commandline interface\nwhich allows you to inspect parquet files and datasets more easily.\n\nDataset\n=======\nExample of use of `polario.dataset.HiveDataset`\n```python\n\nfrom polario.dataset import HiveDataset\nimport polars as pl\ndf = pl.from_dicts(\n        [\n            {"p1": 1, "v": 1},\n            {"p1": 2, "v": 1},\n        ]\n    )\n\nds = HiveDataset("file:///tmp/", partition_columns=["p1"])\n\nds.write(df)\n\nfor partition_df in ds.read_partitions():\n    print(partition_df)\n\n```\n',
    'author': 'Bram Neijt',
    'author_email': 'bram@neijt.nl',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://bneijt.github.io/polario/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
