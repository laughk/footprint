footprint
===============

footpritnt(足跡) is summary generator for Github/Gitlab.com activity.

inspire of `furik <https://github.com/pepabo/furik>`_ .

Install
----------

from PyPI.

.. code:: console

    $ pip install footprint

from github repository.

.. code:: console

    $ pip install git+https://github.com/laughk/footprint.git

Usage
--------

#. make ``~/.footprint.ini`` , ex,

   .. code:: dosini

      [github]
      token = 'Your Github Personal access Token from https://github.com/settings/tokens' 

      [gitlab.com]
      token = 'Your Gitlab.com Private token from https://gitlab.com/profile/account'

#. execute ``footprint`` command.

   .. code:: console

      $ foot --help
      usage: footprint [-h] [-f FROM_STR] [-t TO_STR] [-P] [--gl]

      optional arguments:
        -h, --help            show this help message and exit
        -f FROM_STR, --from FROM_STR
                              set start of date formated "YYYY-MM-DD". (default:
                              current day)
        -t TO_STR, --to TO_STR
                              set end of start date formated "YYYY-MM-DD".
                              (default: current day)
        -P, --private         enable get data from private repository. (default:
                              disable)
        --gl                  [Experimental] enable getting status from gitlab.com.
