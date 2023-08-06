# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jinja_unquote_resolvers_filter']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'types-PyYAML==6.0.12.9']

setup_kwargs = {
    'name': 'jinja-unquote-resolvers-filter',
    'version': '0.0.1',
    'description': 'A Jinja filter for allowing Sceptre resolvers in var files',
    'long_description': "# README\n\n## Overview\n\nA custom Jinja filter for Sceptre for unquoting resolvers appearing in\nvar files.\n\n## Motivation\n\nIn Sceptre, resolvers are an essential feature for simplifying complex\nconfigurations by enabling dynamic data retrieval. Resolvers such as\n`!stack_output_external` and `!stack_output` are particularly useful\nfor referencing output values from other stacks or external sources,\namong many others.\n\nWhen using resolvers in var files, however, they must be protected from\nbeing interpreted as YAML tags by the YAML loader.\n\nThis plugin addresses this challenge by allowing you to safely include\nresolvers in your var files. It ensures that resolvers are not processed\nas YAML tags by the loader, and then turned back into YAML tags after\nJinja interpolation in the generated config.\n\n## Installation\n\nInstallation instructions\n\nTo install directly from PyPI\n```shell\npip install jinja-unquote-resolvers-filter\n```\n\nTo install from the git repo\n```shell\npip install git+https://github.com/Sceptre/jinja-unquote-resolvers-filter.git\n```\n\n## Usage/Examples\n\nIn your var file:\n\n```yaml\nSubnets:\n  - '!stack_output_external mystack::subnet_a'  # Quotes needed to protect a YAML tag.\n  - '!stack_output_external mystack::subnet_b'\n\nVPC: '!stack_output_external mystack::vpc_id'\n```\n\nIn your config:\n\n```yaml\nj2_environment:\n  extensions:\n    - jinja_unquote_resolvers_filter.UnquoteResolversFilterExtension\n\nsceptre_user_data:\n  subnets:\n    {{ var.Subnets | unquote_resolvers(output_indent=4, trim=True) }}\n  vpc: {{ var.VPC }}  # This filter is not needed if the quoted resolvers are passed in as scalars.\n```\n\n## Arguments\n\n- `indent` (optional, default=2): The number of spaces to use for indentation of nested structures in the output YAML.\n- `output_indent` (optional, default=0): The number of spaces to use for indentation of the entire output YAML.\n- `trim` (optional, default=False): Whether to trim leading and trailing spaces in the output YAML.\n\n## Limitations\n\nAt this time, resolver expressions must be wrapped in a single line of text. That is, instead of:\n\n```yaml\nmy_multiline_resolver: |\n  !from_json\n    - !request http://www.whatever.com\n```\n\nInstead write:\n\n```yaml\nmy_multiline_resolver: '!from_json [!request http://www.whatever.com]'\n```\n",
    'author': 'Sceptre',
    'author_email': 'sceptreorg@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Sceptre/jinja-unquote-resolvers-filter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
