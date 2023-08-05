=================================
Academic-community Django project
=================================

`django-academic-community` is a representation of an academic community on the
web using Django.

Some more documentation is in the "docs" directory, but we are working on
improving this.

Quick start for development
---------------------------
1. You need at least python 3.7, postgres and ``pip`` installed
2. Clone this repository::

       git clone https://gitlab.hzdr.de/hcdc/django/django-academic-community.git
       cd django-academic-communty

3. Install the packages (in development mode)::

       pip install .[dev]

5. By default, we assume that there exists a ``django_academic_community``
   database that is writeable for a user name ``django_academic_user`` with
   password ``admin``. But you can change this with environment variables (see
   `settings.py <clm_tools_test_site/settings.py>`__).
   Run::

       python manage.py migrate

   to setup the database.

6. Install the packages for the JS and CSS files::

       npm install

7. Build the JS and CSS files::

       make css
       make js

8. Create a superuser via::

       python manage.py createsuperuser

9.  Run the local development server via::

       python manage.py runserver

    Open the topic browser at http://127.0.0.1:8000/topics, and the admin site
    at http://127.0.0.1:8000/admin


.. _django-reversion: https://django-reversion.readthedocs.io


Building the docs
-----------------
There is some static files generated via sphinx, together with an API
documentation. The source code for this documentation is in the `docs <docs>`__
folder. If you installed this package with the above ``pip install`` command,
you already have everything you need. The only thing that you should have
installed already is ``graphviz`` (e.g. via ``conda install graphviz``).

Navigate to the `docs <docs>`__ folder and run ``make html`` (on linux) or
``make.bat html`` on windows and open the file at
``docs/_build/html/index.html`` in your browser.

Some of the documentation in this content is also available through the admin
docs. When you run the server (``python manage.py runserver``), navigate to the
docs under http://127.0.0.1:8000/admin/docs.

Note that there is still a lot to work on for the documentation, so in case you
are missing something, please do not hesitate to ask.

Running the tests
-----------------
Just run ``tox`` (you installed it with ``pip install .[dev]``).
Note that you will need a running postgres server and a user with the rights
to create a new postgres database.

Contributing
------------

   We are working on a more detailed contributing guide, but here is the
   short version:

When you want to contribute to the code, please do clone the source code
repository and install it with the ``[dev]`` extra, i.e.

.. code:: bash

   git clone https://gitlab.hzdr.de/hcdc/django/clm-community/django-academic-community/
   cd django-academic-community
   pip install -e .[dev]

We use automated formatters (see their config in ``pyproject.toml`` and
``setup.cfg``), namely

-  `Black <https://black.readthedocs.io/en/stable/>`__ for standardized
   code formatting
-  `blackdoc <https://blackdoc.readthedocs.io/en/stable/>`__ for
   standardized code formatting in documentation
-  `Flake8 <http://flake8.pycqa.org/en/latest/>`__ for general code
   quality
-  `isort <https://github.com/PyCQA/isort>`__ for standardized order in
   imports.
-  `mypy <http://mypy-lang.org/>`__ for static type checking on `type
   hints <https://docs.python.org/3/library/typing.html>`__

We highly recommend that you setup `pre-commit
hooks <https://pre-commit.com/>`__ to automatically run all the above
tools every time you make a git commit. This can be done by running

::

   pre-commit install

from the root of the repository. You can skip the pre-commit checks with
``git commit --no-verify`` but note that the CI will fail if it
encounters any formatting errors.

You can also run the pre-commit step manually by invoking

::

   pre-commit run --all-files



Copyright
---------
Copyright © 2021 Helmholtz-Zentrum Hereon, 2020-2021 Helmholtz-Zentrum Geesthacht

Licensed under the EUPL-1.2-or-later

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the EUPL-1.2 license for more details.

You should have received a copy of the EUPL-1.2 license along with this
program. If not, see https://www.eupl.eu/.
