# episoder

![episoder](https://code.ott.net/episoder/screenshot.png "episoder 0.8.0")

Episoder is a tool to tell you about new episodes of your favourite TV shows. It
does so by parsing online TV episode guides.

Currently episoder can get data from [epguides](http://www.epguides.com/) and
[TheTVDB](http://www.epguides.com/) and tells you whenever a new episode of a
show listed on one of those sites is aired.

There is also a web-based version of episoder, called
[webisoder](https://github.com/cockroach/webisoder) which can be used for free
at [webisoder.net](https://www.webisoder.net/).

## Dependencies

In order to use episoder, you will need python installed on your system. In
addition to the default distribution, the `requests`, `argparse`, `sqlalchemy`
and `beautifulsoup4` modules are required.

## Downloading

The official website, bug tracker etc. for episoder can be found at
[code.ott.net/episoder](https://code.ott.net/episoder/).

## Installation

You can install episoder through [pypi](https://pypi.python.org/pypi/episoder)
(using `easy_install` or `pip`) or by running `setup.py` from the downloaded and
extracted tarball.

## Configuration

The configuration file at `~/.episoder` contains your default settings for
episoder. After installing episoder, the man page will help you with the
configuration.

## Using episoder

To use episoder you will typically:

* Create a cron job to update your database once a day using `episoder update`
* Add `episoder` to your `~/.bashrc`, `~/.bash_profile`, `/etc/bash.bashrc` or
  `/etc/profile` if you want to see your upcoming shows every time you start a
  shell. Consult your shell's documentation to find out which file to use.
* Or run `episoder notify` at regular intervals to get notifications by e-mail.
