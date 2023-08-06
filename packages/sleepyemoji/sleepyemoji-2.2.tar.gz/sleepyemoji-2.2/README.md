# **SleepyEmoji**
*Fetch your favorite emojis fast!*

<br />

## **Welcome to sleepyemoji!**
There's now a paralyzing volume of unicode characters known as "emojis", which is great for creative expression, but bad for fetching the ~%10 of emojis you ever care to use.

SleepyEmoji has entered the chat!

<br />

### **Table of Contents** 📖
<hr>

  - **Get Started**
  - Usage
  - Technologies
  - Contribute
  - Acknowledgements
  - License/Stats/Author

<br />

## **Get Started 🚀**
<hr>

To Install:
```sh
pip install sleepyemoji
```
To update:
```sh
pip install sleepyemoji --upgrade
```

And set a personal alias in your shell to run the following script:
```python
from sleepyemoji import sleepyemoji
from sys import argv, exit

sleepyemoji(argv[1:])

exit(0)
```

That's it! It will handle command line argument passthrough. \
This document assumes the script alias to be `emoji`.

<br />

## **Usage ⚙**
<hr>

After setting up the tool, run `emoji [-h|--help]` to display this message:
```txt
This tool prints emojis of one or more catgories, each defined in their own file.
Emojis are given along with their unicode value, discord shorthand, and ios descriptor.

For the official emoji index:
  https://unicode.org/emoji/charts/full-emoji-list.html


Provide 1 or more options of various emoji categories, or simply request all of them.
--------------
All:
  ./main.py [-C|--complete]
Categories:
  /main.py [*flags]
    [-A|--animals]
    [-F|--faces]
    [-H|--hands]
    [-I|--icons]
    [-P|--people]
    [--combos|--combinations]
Example:
  ./main.py -A -H
Info:
  ./main.py [-h|--help]
--------------
```

<br />

## **Technologies 🧰**
<hr>

  - Just vanilla Python3 🙂

<br />

## **Contribute 🤝**
<hr>

This tool is kept in **Envi**, where emoji data is added in `emojis/toolchain` in the corresponding folders. This repository is private, thus the user must appreciate my favorite emojis, mwahahaha!

Remember to pull before you push!

<br />

## **Acknowledgements 💙**
<hr>

Thanks to my late cat Merlin, who whispered best practices in my ear while I wrote this.

<br />

## **License, Stats, Author 📜**
<hr>

<img align="right" alt="example image tag" src="https://i.imgur.com/jtNwEWu.png" width="200" />

<!-- badge cluster -->

![PyPI - License](https://img.shields.io/pypi/l/sleepyemoji?style=plastic)

<!-- / -->
See [License](TODO) for the full license text.

This package was authored by *Isaac Yep*.