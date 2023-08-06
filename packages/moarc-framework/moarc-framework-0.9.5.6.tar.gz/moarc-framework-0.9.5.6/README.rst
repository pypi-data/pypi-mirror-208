=====
Moarc Framework
=====

Moarc Framework is a Django app to improve cruds, templates and views.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "moarcframework" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'moarcframework',
    ]

2. Include the moarcframework URLconf in your project urls.py like this::

    path('/', include('moarcframework.urls')),

3. Run ``python manage.py migrate`` to create the moarcframework models.

4. Start the development server and visit http://127.0.0.1:8000/admin/

