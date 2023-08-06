Dorothy Image Service Client
============================

Client for the Dorothy Image Server built using the `requests
library <https://docs.python-requests.org/en/latest/>`__.

--------------

Index and Contents
------------------

-  `Getting started <#getting-started>`__

   -  `Authentication <#authentication>`__
   -  `Examples of use <#examples-of-use>`__

-  `Development <#development>`__

--------------

Getting started
---------------

All JSONs returned by the API were serialized into Python objects to
make server usage easier and more standardized among team members.

Authentication
~~~~~~~~~~~~~~

To authenticate access to routes, it is necessary to obtain a token. The
token can be provided by the admin members of the Dorothy server. Once
the token has been obtained, it is possible to authenticate the client
in 3 ways:

**1. Passing the token directly as a parameter to the client**

.. code:: python:

   from doroty_client import Client

   service = Client(token="Your token here")

**2. Through environment variable**

.. code:: python:

   from doroty_client import Client
   from os import environment

   environment["DOROTYSDK_ACCESS_TOKEN"] = "your token here"


   service = Client()

**3. Through a text file**

Create a txt file in a path of interest whose content is just your
token.

.. code:: python:

   from doroty_client import Client

   service = Client(path="/path/to/the/file.txt")

Examples of use
~~~~~~~~~~~~~~~

Once the authentication is done, it is possible to perform the following
tasks:

**Search for an image**

.. code:: python:

   some_image = service.image("china_CHNCXR_0099_0_3D81FF")

**Search for an dataset**

.. code:: python:

   dataset_china = service.dataset("china")

**Listing images from a dataset**

.. code:: python:

   dataset_china = service.dataset("china")
   images = dataset_china.list_images()

**Downloading an image**

.. code:: python:

   some_image = service.image("china_CHNCXR_0099_0_3D81FF")
   image_bytes = some_image.download_image()

This client was built based on the requests library. For any questions
about its use, read the library documentation.

Development
-----------

For development, just clone the repository and create a virtual
environment from the declared dependencies. Direct pushes to main branch
are not allowed as main represents the most stable version of the
client. Look to develop a feature on a new branch and then later open PR
to the dev branch.
