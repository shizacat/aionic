NIC.RU API Python library
==========================

The package is the async library for the API of Russian DNS registrator
Ru-Center (a.k.a. NIC.RU). It provides classes for managing DNS services,
zones and records.

This project bases on: https://github.com/andr1an/nic-api

Installation
------------

Using ``pip``::

    pip install aionic

Usage
-----

Initialization
~~~~~~~~~~~~~~

To start using the API, you should get a pair of OAuth application login and
password from NIC.RU. Here is the registration page:
https://www.nic.ru/manager/oauth.cgi?step=oauth.app_register


.. code:: python

    import asyncio
    from nic_api import NICApi

    def print_token(token: dict):
        print("Token:", token)

    api = NICApi(
        client_id = "---",
        client_secret = "---",
        username = "---/NIC-D",
        password = "---",
        scope = "GET:/dns-master/.+",
        token_updater=print_token
    )

    # First you need to get token
    async def main():
        await api.get_token()

    asyncio.run(main)

Get token
~~~~~~~~~

Call the ``get_token()`` method:

.. code:: python

    # First you need to get token
    async def main():
        await api.get_token()

    asyncio.run(main)

Now you are ready to use the API.

If you want, you may to save token to anything (example into file) throuht
callback ``token_updater`` and then he had used for authorize.
While the token is valie, you don't need to provide neither username or password
to access the API.

Viewing services and DNS zones
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the NIC.RU, DNS zones are located in "services":

.. code:: python

    api.services()

Usually there is one service per account. Let's view available zones in the
service ``MY_SERVICE``:

.. code:: python

    async def main():
        await api.zones('MY_SERVICE')

    asyncio.run(main)

**Always check if the zone has any uncommitted changes to it before
making any modifications - your commit will apply other changes too!**

Getting DNS records
~~~~~~~~~~~~~~~~~~~

For viewing or modifying records, you need to specify both service and DNS
zone name:

.. code:: python

    async def main():
        await api.records('MY_SERIVCE', 'example.com')

    asyncio.run(main)

Creating a record
~~~~~~~~~~~~~~~~~

To add a record, create an instance of one of the ``nic_api.models.DNSRecord``
subclasses, i.e. ``ARecord``:

.. code:: python

    import aionic.models as nic_models
    record_www = nic_models.ARecord(name='www', a='8.8.8.8', ttl=3600)

Add this record to the zone and commit the changes:

.. code:: python

    async def main():
        await api.add_record(record_www, 'MY_SERVICE', 'example.com')
        await api.commit('MY_SERVICE', 'example.com')

    asyncio.run(main)

Deleting a record
~~~~~~~~~~~~~~~~~

Every record in the zone has an unique ID, and it's accessible via
``DNSRecord.id`` property. When you got the ID, pass it to the
``delete_record`` method:

.. code:: python

    async def main():
        await api.delete_record(10, 'MY_SERVICE', 'example.com')
        await api.commit('MY_SERVICE', 'example.com')

    asyncio.run(main)

Do not forget to always commit the changes!
