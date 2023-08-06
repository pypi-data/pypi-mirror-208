""""""""""""""""""""""""""
Fedinesia
""""""""""""""""""""""""""

|Repo| |CI| |Downloads|

|Checked against| |Checked with|

|Code style| |Version| |Wheel|

|AGPL|


***!!! BEWARE, THIS TOOL WILL DELETE SOME OF YOUR POSTS ON THE FEDIVERSE !!!***

Fedinesia is a command line (CLI) tool to delete old statuses from Mastodon or Pleroma instances.
It respects rate limits imposed by servers.

Install and run from `PyPi <https://pypi.org>`_
=================================================

It's ease to install Fedinesia from Pypi using the following command::

    pip install fednesia

Once installed Fedinesia can be started by typing ``fedinesia`` into the command line.

Install and run from `Source <https://codeberg.org/MarvinsMastodonTools/fedinesia>`_
==============================================================================================

Alternatively you can run Fedinesia from source by cloning the repository using the following command line::

    git clone https://codeberg.org/MarvinsMastodonTools/fedinesia.git

Fedinesia uses `PDM <https://pdm.fming.dev/latest/>`_ for dependency control, please install PDM before proceeding further.

Before running, make sure you have all required python modules installed. With PDM this is as easy as::

    pdm sync --group :all

Run Fedinesia with the command `pdm run fedinesia`

Configuration / First Run
=========================

Fedinesia will ask for all necessary parameters when run for the first time and store them in ```config.json``
file in the current directory.

Licensing
=========
Fedinesia is licensed under the `GNU Affero General Public License v3.0 <http://www.gnu.org/licenses/agpl-3.0.html>`_

Supporting Fedinesia
==========================

There are a number of ways you can support Fedinesia:

- Create an issue with problems or ideas you have with/for Fedinesia
- You can `buy me a coffee <https://www.buymeacoffee.com/marvin8>`_.
- You can send me small change in Monero to the address below:

Monero donation address
-----------------------
``86ZnRsiFqiDaP2aE3MPHCEhFGTeipdQGJZ1FNnjCb7s9Gax6ZNgKTyUPmb21WmT1tk8FgM7cQSD5K7kRtSAt1y7G3Vp98nT``


.. |AGPL| image:: https://www.gnu.org/graphics/agplv3-with-text-162x68.png
    :alt: AGLP 3 or later
    :target:  https://codeberg.org/MarvinsMastodonTools/fedinesia/src/branch/main/LICENSE.md

.. |Repo| image:: https://img.shields.io/badge/repo-Codeberg.org-blue
    :alt: Repo at Codeberg.org
    :target: https://codeberg.org/MarvinsMastodonTools/fedinesia

.. |Downloads| image:: https://pepy.tech/badge/fedinesia
    :alt: Download count
    :target: https://pepy.tech/project/fedinesia

.. |Code style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code Style: Black
    :target: https://github.com/psf/black

.. |Checked against| image:: https://img.shields.io/badge/Safety--DB-Checked-green
    :alt: Checked against Safety DB
    :target: https://pyup.io/safety/

.. |Checked with| image:: https://img.shields.io/badge/pip--audit-Checked-green
    :alt: Checked with pip-audit
    :target: https://pypi.org/project/pip-audit/

.. |Version| image:: https://img.shields.io/pypi/pyversions/fedinesia
    :alt: PyPI - Python Version

.. |Wheel| image:: https://img.shields.io/pypi/wheel/fedinesia
    :alt: PyPI - Wheel

.. |CI| image:: https://ci.codeberg.org/api/badges/MarvinsMastodonTools/fedinesia/status.svg
    :alt: CI / Woodpecker
    :target: https://ci.codeberg.org/MarvinsMastodonTools/fedinesia
