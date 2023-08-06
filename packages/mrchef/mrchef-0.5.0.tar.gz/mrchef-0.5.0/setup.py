# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mrchef']

package_data = \
{'': ['*']}

install_requires = \
['coloredlogs>=15.0.1',
 'decorator>=5.1.1',
 'git-autoshare>=1.0.0-beta.6',
 'mergedeep>=1.3.4',
 'plumbum>=1.7.2',
 'requests>=2.27.1',
 'tomlkit>=0.10.0',
 'xdg>=5.1.1']

entry_points = \
{'console_scripts': ['mrchef = mrchef.__main__:run']}

setup_kwargs = {
    'name': 'mrchef',
    'version': '0.5.0',
    'description': 'Metarepo Chef',
    'long_description': "# Mr. Chef\n\n👨\u200d🍳 Meta-Repo Chef. Culinary git helper to work with code buffets.\n\n## Why\n\nIt has features that no other meta-repo manager has:\n\n-   Code is 100% reproducible.\n-   Full freeze-warmup-freeze coding cycle.\n-   Upstream patching supported.\n-   Downstream patching supported.\n-   Mixed and multi-patching repo supported.\n-   Automated updates.\n-   Automatic disk space economization with [git-autoshare][].\n-   Food! 🥘\n\nLet's dive in. Imagine you need to create an app that requires many unrelated modules to\nbe properly glued together. How would you organize your source code?\n\nThere are multiple answers to that question:\n\n-   Use separate repos and glue them together through packaging. But what if some code\n    you need isn't properly packaged? What if some dependencies need more than 1 patch\n    to work?\n-   Use [a monorepo](https://en.wikipedia.org/wiki/Monorepo). However, what happens if\n    some parts are open source and you need to upstream or review changes?\n-   Use [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules). However,\n    that requires that every time you do a `git checkout`... or almost any git\n    command..., you need to use some `--recurse-submodules` flag. Also it gives _a lot_\n    of headaches when you move files around and perform basically any operation. And\n    what if you need to merge 2 upstream patches?\n-   Use [git subtrees](https://www.atlassian.com/git/tutorials/git-subtree). But then,\n    you need even more deep knowledge than with submodules to be able to review or\n    publish patches. And again, how to merge more than one patch?\n-   Use [Pijul](https://pijul.org/posts/2022-01-07-monorepos/). But the world isn't\n    ready for it yet. Still we need Git.\n\nThe solution is to [use a meta-repo](https://notes.burke.libbey.me/metarepo/). There are\nmany meta-repo managers out there, but none of them has all the features that I already\ntold you about Mr. Chef.\n\n## Glossary\n\nMr. Chef introduces a new code management concept based on the metaphor of a buffet. Use\nthis glossary to understand the rest of the recipe... readme! Sorry...\n\n-   _Buffet_ is the main git repository that contains all the instructions to build it.\n-   The _config file_ is a file named `mrchef.toml` that stands in the root of your\n    _buffet_ and configures what Mr. Chef should do.\n-   The _kitchen_ is the root folder, inside the _buffet_, where you can find the\n    _meals_. It's configured inside the _config file_.\n-   A _meal_ is like a git submodule: another git repo inside your _kitchen_.\n-   A _spice_ is a patch that is added to a _meal_.\n-   The _freezer_ is where we store the gory details needed to make the kitchen 100%\n    reproducible. Mr. Chef saves it in a file called `.mrchef.freezer.toml`.\n-   _Warming up_ means getting meals outside of the _freezer_ and putting them in the\n    _kitchen_, ready to cook!\n-   _Freezing_ means writing a new _freezer_ that can reproduce what's currently _warmed\n    up_ in the _kitchen_.\n\n## How\n\n### Using CLI\n\nInstall it:\n\n```sh\npipx install mrchef\n```\n\nUsually you start by creating a new configuration file:\n\n```sh\nmrchef init\n```\n\nIt will create a new `mrchef.toml` file with some comments about how to use it. You can\ndelete them once you know how to do it.\n\nNow, you will need to add a meal:\n\n```sh\nmrchef meal-add kitchen/hello https://github.com/octocat/Hello-World master\n```\n\n💡 Mr. Chef uses [git-autoshare][] automatically. It will help you if you need to clone\nhuge repos! But you have to configure it before adding the meals.\n\nYou can add more meals just like that.\n\nMaybe you need to apply a couple of spices to the meal? OK:\n\n```sh\nmrchef spice-add kitchen/hello https://github.com/octocat/Hello-World/pull/2256\nmrchef spice-add kitchen/hello https://github.com/octocat/Hello-World/pull/34\n```\n\nDid `master` get new commits? Or did those PRs get updated? Update everything:\n\n```sh\nmrchef update\n```\n\nCool, huh? 😏 Mr. Chef can do more things! To see all commands and what they do:\n\n```sh\nmrchef --help-all\n```\n\n### Using Python\n\nInstall it:\n\n```sh\npip install mrchef\n```\n\nUse it:\n\n```python\nimport mrchef\n```\n\n### Using Nix\n\nInstall it:\n\n```sh\nnix profile install gitlab:moduon/mrchef\n```\n\nDid I say buffets are 100% reproducible? Nothing better than [Nix](https://nixos.org/)\nfor that job.\n\nGo read [the flake](./flake.nix). You'll find helpers ready to convert a buffet into\naggregated source code. Read [the minimal test](./tests/nix/testMinimal.nix) to\nunderstand how to use them. Ready to replace git submodules?\n\nKeep in mind this if using nix:\n\n-   You should enable flakes. At least, until https://github.com/NixOS/nix/issues/5541\n    or https://github.com/NixOS/nix/issues/5119 are fixed.\n\n## Who\n\nCreated and maintained by [Moduon Team](https://www.moduon.team/).\n\nOriginal idea by [Jairo Llopis](https://www.recallstack.icu/).\n\n## Where\n\nAnywhere you want! 🎁 It's [GPL 3.0+](./LICENSE).\n\n[git-autoshare]: https://github.com/acsone/git-autoshare\n",
    'author': 'Moduon',
    'author_email': 'info@moduon.team',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://gitlab.com/moduon/mrchef',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
