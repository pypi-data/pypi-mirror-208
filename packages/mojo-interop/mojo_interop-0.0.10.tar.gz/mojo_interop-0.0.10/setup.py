# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'source/packages'}

packages = \
['mojo',
 'mojo.factories',
 'mojo.interop.clients',
 'mojo.interop.clients.linux',
 'mojo.interop.clients.osx',
 'mojo.interop.clients.windows',
 'mojo.interop.clusters',
 'mojo.interop.clusters.raspberrypi',
 'mojo.interop.protocols.dns',
 'mojo.interop.protocols.power.dlipower',
 'mojo.interop.protocols.serial',
 'mojo.interop.protocols.ssh',
 'mojo.interop.protocols.upnp',
 'mojo.interop.protocols.upnp.content',
 'mojo.interop.protocols.upnp.devices',
 'mojo.interop.protocols.upnp.extensions',
 'mojo.interop.protocols.upnp.extensions.dynamic',
 'mojo.interop.protocols.upnp.extensions.dynamic.embeddeddevices',
 'mojo.interop.protocols.upnp.extensions.dynamic.rootdevices',
 'mojo.interop.protocols.upnp.extensions.dynamic.services',
 'mojo.interop.protocols.upnp.extensions.standard.embeddeddevices',
 'mojo.interop.protocols.upnp.extensions.standard.rootdevices',
 'mojo.interop.protocols.upnp.extensions.standard.services',
 'mojo.interop.protocols.upnp.extensions.standard.services.UPnP',
 'mojo.interop.protocols.upnp.generator',
 'mojo.interop.protocols.upnp.generator.dynamic',
 'mojo.interop.protocols.upnp.services',
 'mojo.interop.protocols.upnp.xml']

package_data = \
{'': ['*'],
 'mojo.interop.protocols.upnp.generator': ['standard/embeddeddevices/UPnP/*',
                                           'standard/services/UPnP/*']}

install_requires = \
['mojo-networking>=0.0.4,<0.1.0', 'mojo-xmodules>=0.0.34,<0.1.0']

setup_kwargs = {
    'name': 'mojo-interop',
    'version': '0.0.10',
    'description': 'Automation Mojo Interop Extensions',
    'long_description': '===============================\nAutomation Mojo Interop Package\n===============================\n\nThis *Automation Mojo Interop Package* contains interop extensions that add interop functionality to\nthe test environment *Landscape* object for a variety of platform clients, clusters, and protocols.\n\n==========\nReferences\n==========\n\n- `User Guide <userguide/userguide.rst>`\n- `Coding Standards <userguide/10-00-coding-standards.rst>`\n',
    'author': 'None',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
