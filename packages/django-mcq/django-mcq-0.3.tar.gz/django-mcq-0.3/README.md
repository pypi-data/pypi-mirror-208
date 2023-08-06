# Django Multiple Choice Question


Installation
------------
Install django-mcq

Run `pip install django-mcq`.

Add `'quiz'` to your `INSTALLED_APPS` setting.

    INSTALLED_APPS = (
        ...
        'quiz',
        ...
    )


Add the following to your projects `urls.py` file.


    urlpatterns = [
        ...
        path('quiz/', include('quiz.urls')),
    ]


Create a template `quiz_base.html` file in **templates** folder:

    <!doctype html>
    <html lang="en">
        <head>
            {% block quiz_css %}{% endblock %}
        </head>
        <body>
            {% block quiz_body %}{% endblock %}
            {% block quiz_js %}{% endblock %}
        </body>
    </html>

Migrate database:

    python manage.py migrate

Load sample quizzes:

    python manage.py loaddata sample_quizzes.json

Now login a user and navigate to <http://127.0.0.1:8000/quiz/>


Packaging pypi
--------------

* delete files in `dist` folder
* increment the version number in your `setup.py` file
* `$ python3 -m build`
* `twine upload dist/*`