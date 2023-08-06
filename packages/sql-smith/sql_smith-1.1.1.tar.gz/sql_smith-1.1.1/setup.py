# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sql_smith',
 'sql_smith.builder',
 'sql_smith.capability',
 'sql_smith.engine',
 'sql_smith.interfaces',
 'sql_smith.partial',
 'sql_smith.partial.parameter',
 'sql_smith.query',
 'sql_smith.query.mysql',
 'sql_smith.query.postgres',
 'sql_smith.query.sql_server']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sql-smith',
    'version': '1.1.1',
    'description': 'sql-smith is an SQL query builder with zero dependencies and a fluent interface.',
    'long_description': '=========\nsql-smith\n=========\n\n**sql-smith** is an SQL query builder with zero dependencies and a fluent interface.\n\n    The sentence above is, beside the name, a copy from the website of the PHP library\n    Latitude_, for the simple reason that this Python module is a port of Latitude.\n\nRead the full `documentation <https://fbraem.github.io/sql-smith>`_.\n\nInstallation\n************\n\n.. code-block:: sh\n\n    $ pip install sql-smith\n\nQuick Start\n***********\n\nQueryFactory is a factory to create a **SELECT**, **INSERT**, **UPDATE** or **DELETE** query.\nUse the fluent interface of the queries to complete the query.\n\n.. code-block:: python\n\n    from sql_smith import QueryFactory\n    from sql_smith.engine import CommonEngine\n    from sql_smith.functions import field\n    \n    factory = QueryFactory(CommonEngine())\n    query = factory \\\n        .select(\'id\', \'username\') \\\n        .from_(\'users\') \\\n        .where(field(\'id\').eq(5)) \\\n        .compile()\n    \n    print(query.sql)  # SELECT "id", "username" FROM "users" WHERE "id" = ?\n    print(query.params)  # (5)\n\nWhen the query is ready, compile it. The return value of compile is a Query class instance\nwith two properties: sql and params. Use these properties to pass the query to a database.\n\n.. code-block:: python\n\n    import sqlite3\n    \n    db = sqlite3.connect(\'test.db\')\n    cur = db.cursor()\n\n    for row in cur.execute(query.sql, query.params):\n        print(row)\n\nAcknowledgment\n==============\nBig thanks to JetBrains_ to let me use PyCharm for free!\n\n.. _Latitude: https://latitude.shadowhand.com/\n.. _JetBrains: https://www.jetbrains.com/pycharm/\n',
    'author': 'fbraem',
    'author_email': 'franky.braem@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
