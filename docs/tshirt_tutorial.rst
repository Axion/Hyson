Building T-shirt database
-------------------------

We are going to create a small application which will help us to track collection of t-shirts

Plan
````

We want to have simple Ext JS 4 application with a grid containing our t-shirt collection, we need an add button
somewhere so we can show window with add form, we want to update t-shirt information and delete old t-shirts.
Additionally having a t-shirt details panel would be nice. A button to select a random t-shirt for today would be nice too.

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
    ./manage.py startextapp catalog


Create ext application
```````````````````````

Create basic latout
```````````````````

Create t-shirt model
````````````````````

Create ListView for t-shirts
````````````````````````````

Convert ListView to grid
````````````````````````

Put grid into layout
````````````````````

Add CreateView and ModelForm
````````````````````````````

Convert CreateView to Window wth add form
`````````````````````````````````````````

Prepeare dev enviroment
```````````````````````




