# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['client']

package_data = \
{'': ['*']}

install_requires = \
['pyln-bolt7>=1.0', 'pyln-proto>=0.12']

setup_kwargs = {
    'name': 'pyln-client',
    'version': '23.5',
    'description': 'Client library and plugin library for Core Lightning',
    'long_description': '# pyln-client: A python client library for lightningd\n\nThis package implements the Unix socket based JSON-RPC protocol that\n`lightningd` exposes to the rest of the world. It can be used to call\narbitrary functions on the RPC interface, and serves as a basis for plugins\nwritten in python.\n\n\n## Installation\n\n`pyln-client` is available on `pip`:\n\n```\npip install pyln-client\n```\n\nAlternatively you can also install the development version to get access to\ncurrently unreleased features by checking out the Core Lightning source code and\ninstalling into your python3 environment:\n\n```bash\ngit clone https://github.com/ElementsProject/lightning.git\ncd lightning/contrib/pyln-client\npoetry install\n```\n\nThis will add links to the library into your environment so changing the\nchecked out source code will also result in the environment picking up these\nchanges. Notice however that unreleased versions may change API without\nwarning, so test thoroughly with the released version.\n\n## Examples\n\n\n### Using the JSON-RPC client\n```py\n"""\nGenerate invoice on one daemon and pay it on the other\n"""\nfrom pyln.client import LightningRpc\nimport random\n\n# Create two instances of the LightningRpc object using two different Core Lightning daemons on your computer\nl1 = LightningRpc("/tmp/lightning1/lightning-rpc")\nl5 = LightningRpc("/tmp/lightning5/lightning-rpc")\n\ninfo5 = l5.getinfo()\nprint(info5)\n\n# Create invoice for test payment\ninvoice = l5.invoice(100, "lbl{}".format(random.random()), "testpayment")\nprint(invoice)\n\n# Get route to l1\nroute = l1.getroute(info5[\'id\'], 100, 1)\nprint(route)\n\n# Pay invoice\nprint(l1.sendpay(route[\'route\'], invoice[\'payment_hash\']))\n```\n\n### Writing a plugin\n\nPlugins are programs that `lightningd` can be configured to execute alongside\nthe main daemon. They allow advanced interactions with and customizations to\nthe daemon.\n\n```python\n#!/usr/bin/env python3\nfrom pyln.client import Plugin\n\nplugin = Plugin()\n\n@plugin.method("hello")\ndef hello(plugin, name="world"):\n    """This is the documentation string for the hello-function.\n\n    It gets reported as the description when registering the function\n    as a method with `lightningd`.\n\n    If this returns (a dict), that\'s the JSON "result" returned.  If\n    it raises an exception, that causes a JSON "error" return (raising\n    pyln.client.RpcException allows finer control over the return).\n    """\n    greeting = plugin.get_option(\'greeting\')\n    s = \'{} {}\'.format(greeting, name)\n    plugin.log(s)\n    return s\n\n\n@plugin.init()\ndef init(options, configuration, plugin):\n    plugin.log("Plugin helloworld.py initialized")\n    # This can also return {\'disabled\': <reason>} to self-disable,\n\t# but normally it returns None.\n\n\n@plugin.subscribe("connect")\ndef on_connect(plugin, id, address, **kwargs):\n    plugin.log("Received connect event for peer {}".format(id))\n\n\nplugin.add_option(\'greeting\', \'Hello\', \'The greeting I should use.\')\nplugin.run()\n\n```\n',
    'author': 'Christian Decker',
    'author_email': 'decker.christian@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
