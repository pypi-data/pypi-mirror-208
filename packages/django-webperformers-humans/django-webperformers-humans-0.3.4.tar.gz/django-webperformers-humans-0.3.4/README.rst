Django humans
=====

Warning - templates are built using TailwindCSS - you need to build a styles for them manually

Humans is a Django app:
1. Exposing humans.txt file
2. Exposing project team over /team/ path
3. Exposing each project team member over /team/member-name path

Model Humans is created to manage team members and their information

App uses templates:
1. *teamComponent.html* - main component of displaying team members
2. *teamPage.html* - page, including teamComponent.html component, and extending base template. Base template should have humansContent block.
3. *personPage.html* - page, displaying each tem member individually, and extending base template. Base template should have humansContent block.

To override them, just create same files in your templates dir humans folder

Quick start
-----------

1. Add "humans" to your INSTALLED_APPS setting like this::

    ``INSTALLED_APPS = [
        ...,
        "humans",
    ]``

2. Include the humans URLconf in your project urls.py like this::

    ``path('', include('humans.urls')),``

3. Run ``python manage.py migrate`` to create the humans models.

4. Add ``{% block humansContent %}{% endblock %}`` to your base template to include pages in

