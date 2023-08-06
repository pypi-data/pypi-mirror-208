# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['classy_imaginary',
 'classy_imaginary.cli',
 'classy_imaginary.enhancers',
 'classy_imaginary.enhancers.phraselists',
 'classy_imaginary.img_processors',
 'classy_imaginary.modules',
 'classy_imaginary.modules.diffusion',
 'classy_imaginary.modules.midas',
 'classy_imaginary.modules.midas.midas',
 'classy_imaginary.samplers',
 'classy_imaginary.training_tools',
 'classy_imaginary.vendored',
 'classy_imaginary.vendored.basicsr',
 'classy_imaginary.vendored.blip',
 'classy_imaginary.vendored.clip',
 'classy_imaginary.vendored.clipseg',
 'classy_imaginary.vendored.codeformer',
 'classy_imaginary.vendored.k_diffusion',
 'classy_imaginary.vendored.k_diffusion.models']

package_data = \
{'': ['*'],
 'classy_imaginary': ['bin/*', 'configs/*', 'data/*'],
 'classy_imaginary.vendored': ['noodle_soup_prompts/*'],
 'classy_imaginary.vendored.blip': ['configs/*']}

install_requires = \
['imaginAIry==11.1.0']

setup_kwargs = {
    'name': 'classy-imaginary',
    'version': '0.6.2',
    'description': 'This is not a useful package. It is a wrapper around imaginary to provide a Class interface.',
    'long_description': 'This is not a useful package. It is a wrapper around imaginary to provide a Class interface.\n',
    'author': 'Hanoush',
    'author_email': 'hanoush87@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
