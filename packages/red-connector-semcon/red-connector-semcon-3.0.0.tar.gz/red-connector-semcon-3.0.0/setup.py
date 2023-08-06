# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['red_connector_semcon',
 'red_connector_semcon.commons',
 'red_connector_semcon.semcon']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=3.0,<4.0', 'requests>=2.28,<3.0']

entry_points = \
{'console_scripts': ['red-connector-semcon = '
                     'red_connector_semcon.semcon.main:main']}

setup_kwargs = {
    'name': 'red-connector-semcon',
    'version': '3.0.0',
    'description': 'RED Connector Semcon is part of the Curious Containers project.',
    'long_description': '# RED Connector Semcon\n\nRED Connector Semcon is part of the Curious Containers project.\n\nThis connector is designed to read data from a [semantic container](https://www.ownyourdata.eu/en/semcon/).\n\nFor more information please refer to the Curious Containers [documentation](https://www.curious-containers.cc/).\n\n## Limitations / Future Work\n- Selections within the content of a data entry are partially supported in json format. For any other format this is currently not possible.\n\n## Acknowledgements\n\nThe Curious Containers software is developed at [CBMI](https://cbmi.htw-berlin.de/) (HTW Berlin - University of Applied Sciences). The work is supported by the German Federal Ministry of Economic Affairs and Energy (ZIM project BeCRF, grant number KF3470401BZ4), the German Federal Ministry of Education and Research (project deep.TEACHING, grant number 01IS17056 and project deep.HEALTH, grant number 13FH770IX6) and HTW Berlin Booster.\n',
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.curious-containers.cc/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
