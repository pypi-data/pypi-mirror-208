# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['speed_cli']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'speed-cli',
    'version': '0.1.1',
    'description': 'Effortlessly create descriptive, colorized command line interfaces (CLIs) for your script collections!',
    'long_description': '# Speed-CLI\nEffortlessly create descriptive, colorized command line interfaces (CLIs) for your script collections!\n\nSimplify script and package management by quickly creating a CLI that automatically parses arguments and returns of \nyour functions. Get an instant understanding of your collection without diving into extensive documentation. \nCustomize descriptions and add informative text, making script interaction easy without remembering all the details.\n\n![speed_cli_showcase](https://github.com/Mnikley/Speed-CLI/assets/75040444/12f8506b-a78c-4feb-ac8e-8d56202d23e8)\n\n## Basic Usage\n```\nfrom speed_cli import CLI\nfrom your_package import test_func, test_func_two, test_func_three\n\nCLI(menu=[\n    test_func, \n    test_func_two, \n    test_func_three\n])\n```\nand that\'s it! With a `your_package.py` file looking like this:\n```\ndef test_func():\n    print("K")\n\ndef test_func_two(number):\n    print(f"Doing some calculations with: {number}!")\n\ndef test_func_three(my_num: int = 5, my_str: str = \'fredl\') -> str:\n    return f"{my_num**2} {my_str}"\n```\nthis would give you an interactive prompt like this:\n\n![image](https://github.com/Mnikley/Speed-CLI/assets/75040444/968962f1-b54a-416b-b602-b5bb45ff1778)\n\n.. of course, you can always modify your CLI and make it more fancy and descriptive! Lets say i want to give \nthe second function some more description, and add custom fields:\n```\n    from speed_cli import CLI, Color, MenuEntry\n\n    red = Color(\'red\')\n    CLI(color="blue",\n        menu=[\n            test_func,\n            MenuEntry(func=test_func_two,\n                      title="My second test function",\n                      description="This function is used to do this and that!",\n                      warning=f"Be aware to pass the argument {red.colorize(\'number\')} !!"\n                      ),\n            test_func_three\n        ])\n```\nwould give you:\n\n![image](https://github.com/Mnikley/Speed-CLI/assets/75040444/e83422f5-82cf-459c-9e4a-3a534195bb3c)\n\n.. the `Color` class also allows you to simply use colored texts in your prints:\n```\nfrom speed_cli import Color\n\nc = Color()\nprint(f"I like {c.colorize(\'colors\')} to {c.colorize(\'emphasize\', color=\'green\', bold=True)} on the "\n      f"{c.colorize(\'important\', color=\'black\', background=\'bg_cyan\')} stuff!")\n```\ngives you:\n\n![image](https://github.com/Mnikley/Speed-CLI/assets/75040444/b3c1b06a-56e5-4d27-913e-c966c4c8f524)\n\n# TODO:\n- currently only accepts strings as arguments, conversions have to be done in underlying function; convert based on types if given',
    'author': 'Matthias Ley',
    'author_email': 'matthias.ley@pm.me',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Mnikley/Speed-CLI',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
