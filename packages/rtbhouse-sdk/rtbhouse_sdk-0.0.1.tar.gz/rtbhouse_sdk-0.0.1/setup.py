# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rtbhouse_sdk']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.24.0,<0.25.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'rtbhouse-sdk',
    'version': '0.0.1',
    'description': 'RTB House SDK',
    'long_description': 'RTB House SDK\n=============\n\nOverview\n--------\n\nThis library provides an easy-to-use Python interface to RTB House API. It allows you to read and manage you campaigns settings, browse offers, download statistics etc.\n\nAPI docs: https://api.panel.rtbhouse.com/api/docs\n\nInstallation\n------------\n\nRTB House SDK can be installed with `pip <https://pip.pypa.io/>`_: ::\n\n    $ pip install rtbhouse_sdk\n\n\nUsage example\n-------------\n\nLet\'s write a script which fetches campaign stats (imps, clicks, postclicks) and shows the result as a table (using ``tabulate`` library).\n\nFirst, create ``config.py`` file with your credentials: ::\n\n    USERNAME = \'jdoe\'\n    PASSWORD = \'abcd1234\'\n\n\nSet up virtualenv and install requirements: ::\n\n    $ pip install rtbhouse_sdk tabulate\n\n\n.. code-block:: python\n\n    from datetime import date, timedelta\n    from operator import attrgetter\n\n    from rtbhouse_sdk.client import BasicAuth, Client\n    from rtbhouse_sdk.schema import CountConvention, StatsGroupBy, StatsMetric\n    from tabulate import tabulate\n\n    from config import PASSWORD, USERNAME\n\n    if __name__ == "__main__":\n        with Client(auth=BasicAuth(USERNAME, PASSWORD)) as api:\n            advertisers = api.get_advertisers()\n            day_to = date.today()\n            day_from = day_to - timedelta(days=30)\n            group_by = [StatsGroupBy.DAY]\n            metrics = [\n                StatsMetric.IMPS_COUNT,\n                StatsMetric.CLICKS_COUNT,\n                StatsMetric.CAMPAIGN_COST,\n                StatsMetric.CONVERSIONS_COUNT,\n                StatsMetric.CTR\n            ]\n            stats = api.get_rtb_stats(\n                advertisers[0].hash,\n                day_from,\n                day_to,\n                group_by,\n                metrics,\n                count_convention=CountConvention.ATTRIBUTED_POST_CLICK,\n            )\n        columns = group_by + metrics\n        data_frame = [\n            [getattr(row, c.name.lower()) for c in columns]\n            for row in reversed(sorted(stats, key=attrgetter("day")))\n        ]\n        print(tabulate(data_frame, headers=columns))\n\n\nLicense\n-------\n\n`MIT <http://opensource.org/licenses/MIT/>`_\n',
    'author': 'RTB House Apps Team',
    'author_email': 'apps@rtbhouse.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/rtbhouse-apps/rtbhouse-python-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.1,<4.0',
}


setup(**setup_kwargs)
