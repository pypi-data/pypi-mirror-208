
.. Licensed to the Apache Software Foundation (ASF) under one
   or more contributor license agreements.  See the NOTICE file
   distributed with this work for additional information
   regarding copyright ownership.  The ASF licenses this file
   to you under the Apache License, Version 2.0 (the
   "License"); you may not use this file except in compliance
   with the License.  You may obtain a copy of the License at

..   http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.


Package ``apache-airflow-providers-smtp``

Release: ``1.1.0rc1``


`Simple Mail Transfer Protocol (SMTP) <https://tools.ietf.org/html/rfc5321>`__


Provider package
----------------

This is a provider package for ``smtp`` provider. All classes for this provider package
are in ``airflow.providers.smtp`` python package.

You can find package information and changelog for the provider
in the `documentation <https://airflow.apache.org/docs/apache-airflow-providers-smtp/1.1.0/>`_.


Installation
------------

You can install this package on top of an existing Airflow 2 installation (see ``Requirements`` below
for the minimum Airflow version supported) via
``pip install apache-airflow-providers-smtp``

The package supports the following python versions: 3.7,3.8,3.9,3.10

Requirements
------------

==================  ==================
PIP package         Version required
==================  ==================
``apache-airflow``  ``>=2.4.0``
==================  ==================

 .. Licensed to the Apache Software Foundation (ASF) under one
    or more contributor license agreements.  See the NOTICE file
    distributed with this work for additional information
    regarding copyright ownership.  The ASF licenses this file
    to you under the Apache License, Version 2.0 (the
    "License"); you may not use this file except in compliance
    with the License.  You may obtain a copy of the License at

 ..   http://www.apache.org/licenses/LICENSE-2.0

 .. Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, either express or implied.  See the License for the
    specific language governing permissions and limitations
    under the License.


.. NOTE TO CONTRIBUTORS:
   Please, only add notes to the Changelog just below the "Changelog" header when there are some breaking changes
   and you want to add an explanation to the users on how they are supposed to deal with them.
   The changelog is updated and maintained semi-automatically by release manager.

Changelog
---------

1.1.0
.....

.. note::
  This release of provider is only available for Airflow 2.4+ as explained in the
  `Apache Airflow providers support policy <https://github.com/apache/airflow/blob/main/PROVIDERS.rst#minimum-supported-version-of-airflow-for-community-managed-providers>`_.

Misc
~~~~

* ``Bump minimum Airflow version in providers (#30917)``

.. Below changes are excluded from the changelog. Move them to
   appropriate section above if needed. Do not delete the lines(!):
   * ``Add full automation for min Airflow version for providers (#30994)``

1.0.1
.....

Bug Fixes
~~~~~~~~~

* ``'EmailOperator': fix wrong assignment of 'from_email' (#30524)``
* ``Accept None for 'EmailOperator.from_email' to load it from smtp connection (#30533)``

.. Below changes are excluded from the changelog. Move them to
   appropriate section above if needed. Do not delete the lines(!):
   * ``Add mechanism to suspend providers (#30422)``

1.0.0
.....

Initial version of the provider.
