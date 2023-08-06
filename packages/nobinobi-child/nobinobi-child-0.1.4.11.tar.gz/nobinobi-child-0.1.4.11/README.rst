=============================
Nobinobi Child
=============================

.. image:: https://badge.fury.io/py/nobinobi-child.svg
    :target: https://badge.fury.io/py/nobinobi-child

.. image:: https://travis-ci.org/prolibre-ch/nobinobi-child.svg?branch=master
    :target: https://travis-ci.org/prolibre-ch/nobinobi-child

.. image:: https://codecov.io/gh/prolibre-ch/nobinobi-child/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/prolibre-ch/nobinobi-child

.. image:: https://pyup.io/repos/github/prolibre-ch/nobinobi-child/shield.svg
     :target: https://pyup.io/repos/github/prolibre-ch/nobinobi-child/
     :alt: Updates

.. image:: https://pyup.io/repos/github/prolibre-ch/nobinobi-child/python-3-shield.svg
     :target: https://pyup.io/repos/github/prolibre-ch/nobinobi-child/
     :alt: Python 3

Application Child for Nobinobi

Documentation
-------------

The full documentation is at https://nobinobi-child.readthedocs.io.

Quickstart
----------

Install Nobinobi Child::

    pip install nobinobi-child

Add it to your `settings.py`:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.BasicAuthentication',
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        ),
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
            'rest_framework_datatables.renderers.DatatablesRenderer',
        ),
        'DEFAULT_FILTER_BACKENDS': (
            'rest_framework_datatables.filters.DatatablesFilterBackend',
        ),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
        'PAGE_SIZE': 50,
    }

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'phonenumber_field',
        'crispy_forms',
        'django_extensions',
        'rest_framework',
        'rest_framework.authtoken',
        'rest_framework_datatables',
        'menu',
        'bootstrap_modal_forms',
        'widget_tweaks',
        'django_select2',
        'bootstrap_datepicker_plus',
        'nobinobi_core',
        'nobinobi_staff',
        'nobinobi_child.apps.NobinobiChildConfig',
        ...
    )

Add Nobinobi Child's URL patterns:

.. code-block:: python

    from nobinobi_core import urls as nobinobi_core_urls
    from nobinobi_staff import urls as nobinobi_staff_urls
    from nobinobi_child import urls as nobinobi_child_urls


    urlpatterns = [
        ...
        path('', include(nobinobi_core_urls)),
        path('', include(nobinobi_staff_urls)),
        path('', include(nobinobi_child_urls)),
        path('select2/', include('django_select2.urls')),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox


Development commands
---------------------

::

    pip install -r requirements_dev.txt
    invoke -l


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
