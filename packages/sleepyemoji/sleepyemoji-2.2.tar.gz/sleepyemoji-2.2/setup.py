# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['sleepyemoji',
 'option_utils',
 'animals',
 'combos',
 'faces',
 'fetcher',
 'hands',
 'icons',
 'people']
setup_kwargs = {
    'name': 'sleepyemoji',
    'version': '2.2',
    'description': 'Print all the emojis that sleepyboy thinks are worthwhile!',
    'long_description': '# **SleepyEmoji**\n*Fetch your favorite emojis fast!*\n\n<br />\n\n## **Welcome to sleepyemoji!**\nThere\'s now a paralyzing volume of unicode characters known as "emojis", which is great for creative expression, but bad for fetching the ~%10 of emojis you ever care to use.\n\nSleepyEmoji has entered the chat!\n\n<br />\n\n### **Table of Contents** 📖\n<hr>\n\n  - **Get Started**\n  - Usage\n  - Technologies\n  - Contribute\n  - Acknowledgements\n  - License/Stats/Author\n\n<br />\n\n## **Get Started 🚀**\n<hr>\n\nTo Install:\n```sh\npip install sleepyemoji\n```\nTo update:\n```sh\npip install sleepyemoji --upgrade\n```\n\nAnd set a personal alias in your shell to run the following script:\n```python\nfrom sleepyemoji import sleepyemoji\nfrom sys import argv, exit\n\nsleepyemoji(argv[1:])\n\nexit(0)\n```\n\nThat\'s it! It will handle command line argument passthrough. \\\nThis document assumes the script alias to be `emoji`.\n\n<br />\n\n## **Usage ⚙**\n<hr>\n\nAfter setting up the tool, run `emoji [-h|--help]` to display this message:\n```txt\nThis tool prints emojis of one or more catgories, each defined in their own file.\nEmojis are given along with their unicode value, discord shorthand, and ios descriptor.\n\nFor the official emoji index:\n  https://unicode.org/emoji/charts/full-emoji-list.html\n\n\nProvide 1 or more options of various emoji categories, or simply request all of them.\n--------------\nAll:\n  ./main.py [-C|--complete]\nCategories:\n  /main.py [*flags]\n    [-A|--animals]\n    [-F|--faces]\n    [-H|--hands]\n    [-I|--icons]\n    [-P|--people]\n    [--combos|--combinations]\nExample:\n  ./main.py -A -H\nInfo:\n  ./main.py [-h|--help]\n--------------\n```\n\n<br />\n\n## **Technologies 🧰**\n<hr>\n\n  - Just vanilla Python3 🙂\n\n<br />\n\n## **Contribute 🤝**\n<hr>\n\nThis tool is kept in **Envi**, where emoji data is added in `emojis/toolchain` in the corresponding folders. This repository is private, thus the user must appreciate my favorite emojis, mwahahaha!\n\nRemember to pull before you push!\n\n<br />\n\n## **Acknowledgements 💙**\n<hr>\n\nThanks to my late cat Merlin, who whispered best practices in my ear while I wrote this.\n\n<br />\n\n## **License, Stats, Author 📜**\n<hr>\n\n<img align="right" alt="example image tag" src="https://i.imgur.com/jtNwEWu.png" width="200" />\n\n<!-- badge cluster -->\n\n![PyPI - License](https://img.shields.io/pypi/l/sleepyemoji?style=plastic)\n\n<!-- / -->\nSee [License](TODO) for the full license text.\n\nThis package was authored by *Isaac Yep*.',
    'author': 'anthonybench',
    'author_email': 'anythonybenchyep@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/anthonybench/emoji',
    'py_modules': modules,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
