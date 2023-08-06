.. what_is_appian_locust-inclusion-begin-do-not-remove

#######################################
What is Appian Locust?
#######################################

Appian Locust is a wrapper library around `Locust <https://locust.io>`__ for load testing Appian.
This library is intended to be used as an alternative to tools such as Jmeter and Load Runner.

Appian Locust capabilities

- Logging in and logging out
- Form interactions (filling/submitting)
- Finding and interacting with basic components on a SAIL interface
- Navigating to records/reports/sites

.. what_is_appian_locust-inclusion-end-do-not-remove


For full documentation, visit the `docs page <https://appian-locust.readthedocs.io/en/latest/>`__

.. disclaimer-inclusion-begin-do-not-remove

**Disclaimer:**
This library is continuously evolving.
Currently the main focus is supporting essential use-cases.
We are happy to accept contributions to further extend functionality, address bug fixes and improve usability.
Please see the `Contributing <contributing.html>`__ section and feel free to reach out.

.. disclaimer-inclusion-end-do-not-remove

.. quick_start-inclusion-begin-do-not-remove

********************
Quick Start Guide
********************

This is a quick guide to getting up and running with the appian-locust library. You will need Python 3.7+ installed on your machine before proceeding.

Setup
------------

1. Install appian-locust using `pip`, for more comprehensive projects we recommend using `pipenv`.

.. code-block:: bash

      pip install appian-locust


If using ``pipenv``, simply start from the following ``Pipfile``:

.. code-block:: toml

    [packages]
    appian-locust = {version = "*"}

    [requires]
    python_version = "3.10"

    [pipenv]
    allow_prereleases = true

2. Configure your test to point at the Appian instance you will be using.
You can use example file provided in this repository `example_config.json <https://gitlab.com/appian-oss/appian-locust/-/blob/master/examples/example_config.json>`_:

- Set ``host_address`` to the address of your Appian instance.
- In ``auth``, specify the username and password of the user account to use.

.. code-block:: json

    {
        "host_address": "site-name.appiancloud.com",
        "auth": [
            "user.name",
            "password"
        ]
    }

3. Run the sample test `example_locustfile.py <https://gitlab.com/appian-oss/appian-locust/-/blob/master/examples/example_locustfile.py>`_.

.. code-block:: bash

    locust -f example_locustfile.py -u 1 -t 60 --headless

If everything is set up correctly, you should start to see output from the load test reporting results. This should run for 60 seconds and end with a summary report of the results.

* For more examples of different site interactions, see the ``example_*.py`` files included in this repository.
* For more in-depth information about the test library, see the rest of this documentation.

Build from source
----------------------
Clone the repository:

.. code-block:: bash

    git clone -o prod git@gitlab.com:appian-oss/appian-locust.git


Install the library globally:

.. code-block:: bash

    pip install -e appian-locust


If you’re using a virtualenv or a dependency management tool (e.g. ``pipenv``), you can do the same type of install, but you will want to be in the context of the virtualenv (i.e. source the virtualenv), and you’ll need to pass the path to the repository you cloned.

Note: It’s highly recommended that you use a virtual environment when installing python artifacts. You can follow the instructions `here <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>`__ to install virtualenv and pip.

If you have issues installing, make sure you have the proper prerequisites installed for Locust and its dependencies.
If you're having trouble on Windows, check `here <https://github.com/locustio/locust/issues/1208#issuecomment-569693439>`__

Troubleshooting
----------------
* **"Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known"**

  * check that ``host_address`` is specified correctly in `example_config.json <https://gitlab.com/appian-oss/appian-locust/-/blob/master/examples/example_config.json>`_.

* **"Login unsuccessful, no multipart cookie found...make sure credentials are correct"**

  * check that `auth` specifies a valid username and password combination for the site you're testing on in `example_config.json <https://gitlab.com/appian-oss/appian-locust/-/blob/master/examples/example_config.json>`_.

* **"General request and response debugging"**

  * Add ``self.appian.interactor.record_mode = True`` to your ``AppianTaskSet`` subclass.  Files will be placed in ``/record_responses`` where the runner is executed.

.. quick_start-inclusion-end-do-not-remove
