Building T-shirt database
-------------------------

We are going to create a small application which will help us to track collection of t-shirts


Prepeare dev enviroment
```````````````````````

This tutorial assumes that you already have working MySQL installation, Python version 2.6 or higher and pip. If not,
please refer to any django/mysql installaction guide for your system.

Install django::

    pip install django

Install Hyson::

    pip install http+git://github.com/Axion/Hyson.git

Create new Django project::

    django-admin.py startproject tshirt
    cd tshirt