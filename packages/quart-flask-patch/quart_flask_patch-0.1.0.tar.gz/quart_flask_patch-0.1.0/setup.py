# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['quart_flask_patch']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'quart-flask-patch',
    'version': '0.1.0',
    'description': 'Quart-Flask-Patch is a Quart extension that patches Quart to work with Flask extensions.',
    'long_description': "Quart-Flask-Patch\n=================\n\n|Build Status| |pypi| |python| |license|\n\nQuart-Flask-Patch is a Quart extension that patches Quart to work with\nFlask extensions.\n\nQuickstart\n----------\n\nQuart-Flask-Patch must be imported first in your main module, so that\nthe patching occurs before any other code is initialised. For example,\nif you want to use Flask-Login,\n\n.. code-block:: python\n\n   import quart_flask_patch\n\n   from quart import Quart\n   import flask_login\n\n   app = Quart(__name__)\n   login_manager = flask_login.LoginManager()\n   login_manager.init_app(app)\n\nExtensions known to work\n------------------------\n\nThe following flask extensions are tested and known to work with\nquart,\n\n- `Flask-BCrypt <https://flask-bcrypt.readthedocs.io>`_\n- `Flask-Caching <https://flask-caching.readthedocs.io>`_\n- `Flask-KVSession <https://github.com/mbr/flask-kvsession>`_\n- `Flask-Limiter <https://github.com/alisaifee/flask-limiter/>`_ See\n  also `Quart-Rate-Limiter\n  <https://github.com/pgjones/quart-rate-limiter>`_\n- `Flask-Login <https://github.com/maxcountryman/flask-login/>`_ See\n  also `Quart-Login <https://github.com/0000matteo0000/quart-login>`_\n  or `Quart-Auth <https://github.com/pgjones/quart-auth>`_\n- `Flask-Mail <https://pythonhosted.org/Flask-Mail/>`_\n- `Flask-Mako <https://pythonhosted.org/Flask-Mako/>`_\n- `Flask-Seasurf <https://github.com/maxcountryman/flask-seasurf/>`_\n- `Flask-SQLAlchemy <https://flask-sqlalchemy.palletsprojects.com>`_\n  See also `Quart-DB <https://github.com/pgjones/quart-db>`_\n- `Flask-WTF <https://flask-wtf.readthedocs.io>`_\n\nExtensions known not to work\n----------------------------\n\nThe following flask extensions have been tested are known not to work\nwith quart,\n\n- `Flask-CORS <https://github.com/corydolphin/flask-cors>`_, as it\n  uses ``app.make_response`` which must be awaited. Try `Quart-CORS\n  <https://github.com/pgjones/quart-cors>`_ instead.\n- `Flask-Restful <https://flask-restful.readthedocs.io>`_\n  as it subclasses the Quart (app) class with synchronous methods\n  overriding asynchronous methods. Try `Quart-OpenApi\n  <https://github.com/factset/quart-openapi/>`_ or `Quart-Schema\n  <https://github.com/pgjones/quart-schema>`_ instead.\n\nCaveats\n-------\n\nFlask extensions must use the global request proxy variable to access\nthe request, any other access e.g. via\n``~quart.local.LocalProxy._get_current_object`` will require\nasynchronous access. To enable this the request body must be fully\nreceived before any part of the request is handled, which is a\nlimitation not present in vanilla flask.\n\nTrying to use Flask alongside Quart in the same runtime will likely\nnot work, and lead to surprising errors.\n\nThe flask extension must be limited to creating routes, using the\nrequest and rendering templates. Any other more advanced functionality\nmay not work.\n\nSynchronous functions will not run in a separate thread (unlike Quart\nnormally) and hence may block the event loop.\n\nFinally the flask_patching system also relies on patching asyncio, and\nhence other implementations or event loop policies are unlikely to\nwork.\n\nContributing\n------------\n\nQuart-Flask-Patch is developed on `GitHub\n<https://github.com/pgjones/quart-flask-patch>`_. If you come across\nan issue, or have a feature request please open an `issue\n<https://github.com/pgjones/quart-flask-patch/issues>`_. If you want\nto contribute a fix or the feature-implementation please do (typo\nfixes welcome), by proposing a `merge request\n<https://github.com/pgjones/quart-flask-patch/merge_requests>`_.\n\nTesting\n~~~~~~~\n\nThe best way to test Quart-Flask-Patch is with `Tox\n<https://tox.readthedocs.io>`_,\n\n.. code-block:: console\n\n    $ pip install tox\n    $ tox\n\nthis will check the code style and run the tests.\n\nHelp\n----\n\nThe Quart-Flask-Patch `documentation\n<https://quart-flask-patch.readthedocs.io/en/latest/>`_ is the best\nplaces to start, after that try searching `stack overflow\n<https://stackoverflow.com/questions/tagged/quart>`_ or ask for help\n`on gitter <https://gitter.im/python-quart/lobby>`_. If you still\ncan't find an answer please `open an issue\n<https://github.com/pgjones/quart-flask-patch/issues>`_.\n\n\n.. |Build Status| image:: https://github.com/pgjones/quart-flask-patch/actions/workflows/ci.yml/badge.svg\n   :target: https://github.com/pgjones/quart-flask-patch/commits/main\n\n.. |pypi| image:: https://img.shields.io/pypi/v/quart-flask-patch.svg\n   :target: https://pypi.python.org/pypi/Quart-Flask-Patch/\n\n.. |python| image:: https://img.shields.io/pypi/pyversions/quart-flask-patch.svg\n   :target: https://pypi.python.org/pypi/Quart-Flask-Patch/\n\n.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg\n   :target: https://github.com/pgjones/quart-flask-patch/blob/main/LICENSE\n",
    'author': 'pgjones',
    'author_email': 'philip.graham.jones@googlemail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/pgjones/quart-flask-patch/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
