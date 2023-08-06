========
idem-gcp
========

.. image:: https://img.shields.io/badge/made%20with-pop-teal
   :alt: Made with pop, a Python implementation of Plugin Oriented Programming
   :target: https://pop.readthedocs.io/

.. image:: https://img.shields.io/badge/made%20with-idem-teal
   :alt: Made with idem, a Python implementation of Plugin Oriented Programming
   :target: https://www.idemproject.io/

.. image:: https://img.shields.io/badge/docs%20on-docs.idemproject.io-blue
   :alt: Documentation is published with Sphinx on docs.idemproject.io
   :target: https://docs.idemproject.io/idem-gcp/en/latest/index.html

.. image:: https://img.shields.io/badge/made%20with-python-yellow
   :alt: Made with Python
   :target: https://www.python.org/

GCP Cloud Provider for Idem.

About
=====

``idem-gcp`` helps manage GCP with ``idem``.

* `idem-gcp source code <https://gitlab.com/vmware/idem/idem-gcp>`__
* `idem-gcp documentation <https://docs.idemproject.io/idem-gcp/en/latest/index.html>`__

What is POP?
------------

This project is built with `pop <https://pop.readthedocs.io/>`__, a Python-based
implementation of *Plugin Oriented Programming (POP)*. POP seeks to bring
together concepts and wisdom from the history of computing in new ways to solve
modern computing problems.

For more information:

* `Intro to Plugin Oriented Programming (POP) <https://pop-book.readthedocs.io/en/latest/>`__
* `pop-awesome <https://gitlab.com/saltstack/pop/pop-awesome>`__
* `pop-create <https://gitlab.com/saltstack/pop/pop-create/>`__

What is Idem?
-------------

This project is built with `idem <https://www.idemproject.io/>`__, an idempotent,
imperatively executed, declarative programming language written in Python. This project extends
idem!

For more information:

* `Idem Project Website <https://www.idemproject.io/>`__
* `Idem Project docs portal <https://docs.idemproject.io/>`__

Getting Started
===============

DEVELOPMENT
===========

Clone the `idem_gcp` repository and install with pip.

.. code:: bash

    git clone git@gitlab.com:my-user/idem_gcp.git
    cd idem_gcp

Create a virtual environment, and then activate it:

.. code:: bash

    python3 -m venv venv
    source venv/bin/activate

Install idem-gcp and other base requirements:

.. code:: bash

    pip3 install -e .
    pip3 install -r requirements/base.txt


Install the following packages in order to run the tests:

.. code:: bash

    pip3 install -r requirements/py3.10/tests.txt

**NOTE:**  Change py3.10 if needed with your  Python version. There is support for py3.7, py3.8, py3.9 and py3.10.

ACCT
====

After installation gcp Idem Provider execution and state modules will be accessible to the pop `hub`.
In order to use them we need to set up our credentials.

Create a new file called `credentials.yaml` and populate it with profiles.
The `default` profile will be used automatically by `idem` unless you specify one with `--acct-profile=profile_name` on the cli.

`acct backends <https://gitlab.com/saltstack/pop/acct-backends>`_ provide alternate methods for storing profiles.

The gcp provider uses the gcp acct plugin for authentication.
A profile needs to specify the authentication parameters for gcp.

credentials.yaml

..  code:: sls

    gcp:
      default:
        username: my_user
        password: my_good_password
        endpoint_url: https://console.gcp.com/api

Now encrypt the credentials file and add the encryption key and encrypted file path to the ENVIRONMENT.

The `acct` command should be available as it is a requisite of `idem` and `idem_gcp`.
Encrypt the the credential file.

.. code:: bash

    acct encrypt credentials.yaml

output::

    -A9ZkiCSOjWYG_lbGmmkVh4jKLFDyOFH4e4S1HNtNwI=

Add these to your environment:

.. code:: bash

    export ACCT_KEY="-A9ZkiCSOjWYG_lbGmmkVh4jKLFDyOFH4e4S1HNtNwI="
    export ACCT_FILE=$PWD/credentials.yaml.fernet


USAGE
=====
A profile can be specified for use with a specific state.
If no profile is specified, the profile called "default", if one exists, will be used:

.. code:: sls

    ensure_user_exists:
      gcp.user.present:
        - acct_profile: my-staging-env
        - name: a_user_name
        - kwarg1: val1

It can also be specified from the command line when executing states.

.. code:: bash

    idem state --acct-profile my-staging-env my_state.sls

It can also be specified from the command line when calling an exec module directly.

.. code:: bash

    idem exec --acct-profile my-staging-env gcp.user.list
