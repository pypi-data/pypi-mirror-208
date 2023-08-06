========
idem-aws
========

.. image:: https://img.shields.io/badge/made%20with-pop-teal
   :alt: Made with pop, a Python implementation of Plugin Oriented Programming
   :target: https://pop.readthedocs.io/

.. image:: https://img.shields.io/badge/made%20with-idem-teal
   :alt: Made with idem, a Python implementation of Plugin Oriented Programming
   :target: https://www.idemproject.io/

.. image:: https://img.shields.io/badge/docs%20on-docs.idemproject.io-blue
   :alt: Documentation is published with Sphinx on docs.idemproject.io
   :target: https://docs.idemproject.io/idem-aws/en/latest/index.html

.. image:: https://img.shields.io/badge/made%20with-python-yellow
   :alt: Made with Python
   :target: https://www.python.org/

AWS Cloud Provider for Idem.

About
=====

``idem-aws`` helps manage AWS with ``idem``.

* `idem-aws source code <https://gitlab.com/vmware/idem/idem-aws>`__
* `idem-aws documentation <https://docs.idemproject.io/idem-aws/en/latest/index.html>`__

What is POP?
------------

This project is built with `pop <https://pop.readthedocs.io/>`__, a Python-based
implementation of *Plugin Oriented Programming (POP)*. POP seeks to bring
together concepts and wisdom from the history of computing in new ways to solve
modern computing problems.

For more information:

* `Intro to Plugin Oriented Programming (POP) <https://pop-book.readthedocs.io/en/latest/>`__
* `pop-awesome <https://gitlab.com/saltstack/pop/pop-awesome>`__
* `pop-create <https://gitlab.com/saltstack/pop/pop-create/>`__

What is Idem?
-------------

This project is built with `idem <https://www.idemproject.io/>`__, an idempotent,
imperatively executed, declarative programming language written in Python. This project extends
idem!

For more information:

* `Idem Project Website <https://www.idemproject.io/>`__
* `Idem Project docs portal <https://docs.idemproject.io/>`__

Getting Started
===============

Prerequisites
-------------

* Python 3.8+
* git *(if installing from source, or contributing to the project)*

Installation
------------

.. note::

   If wanting to contribute to the project, and setup your local development
   environment, see the ``CONTRIBUTING.rst`` document in the source repository
   for this project.

If wanting to use ``idem-aws``, you can do so by either
installing from PyPI or from source.

Install from PyPI
+++++++++++++++++

If package is available via PyPI, include the directions.

.. code-block:: bash

  pip install "idem-aws [full]"

Install from source
+++++++++++++++++++

Clone the ``idem-aws`` repository and install with pip.
Install extra requirements by specifying "localstack" or "full"
in brackets (in ZSH you will have to escape the brackets).

.. code-block:: bash

   # clone repo
   git clone git@<your-project-path>/idem-aws.git
   cd idem-aws

   # Setup venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e idem-aws[full] # [google_auth,localstack,full]

Setup
=====

After installation the AWS Idem Provider execution and state modules will be accessible to the pop ``hub``.
In order to use them we need to set up our credentials.

Create a new file called ``credentials.yaml`` and populate it with credentials.
If you are using localstack, then the ``id`` and ``key`` can be bogus values.
The ``default`` profile will be picked up automatically by ``idem``.

There are many ways aws providers/profiles can be stored. See `acct backends <https://gitlab.com/Akm0d/acct-backends>`_
for more information.

There are multiple authentication backends for ``idem-aws`` which each have their own unique set of parameters.
The following examples show some of the parameters that can be used in these backends to define profiles.
All backends end up creating a boto3 session under the hood and storing it in the ``ctx`` variable that gets passed
to all idem ``exec`` and ``state`` functions.

All authentication backends support two optional parameters, ``endpoint_url`` and ``provider_tag_key``.  The ``endpoint url``
is used to specify an alternate destination for boto3 calls, such as a localstack server or custom dynamodb server.
The ``provider_tag_key`` is used when creating new resources. ``idem-aws`` will only interact with resources that are tagged
with the the customizable ``provider_tag_key`` key.

credentials.yaml:

..  code:: sls

    aws:
      default:
        endpoint_url: http://localhost:4566
        use_ssl: False
        aws_access_key_id: localstack
        aws_secret_access_key: _
        region_name: us-west-1

Additionally, you can use AWS AssumeRole with Idem

..  code:: sls

    aws:
      default:
        endpoint_url: http://localhost:4566
        use_ssl: False
        aws_access_key_id: localstack
        aws_secret_access_key: _
        region_name: us-west-1
        assume_role:
          role_arn: arn:aws:iam::999999999999999:role/xacct/developer
          role_session_name: IdemSessionName

If ``region_name`` is unspecified in the acct profile, it can come from ``acct.extras`` in the idem config file:

.. code:: sls

    # idem.cfg
    acct:
      extras:
        aws:
          region_name: us-west-1

You can also authenticate with ``aws-google-auth`` if it is installed.

.. code:: sls

    aws.gsuite:
      my-staging-env:
        username: user@gmail.com
        password: this_is_available_but_avoid_it
        role_arn: arn:aws:iam::999999999999999:role/xacct/developer
        idp_id: 9999999
        sp_id: 999999999999
        region: us-east-1
        duration: 36000
        account: developer

The google profile example is not named ``default``. To use it, it will need to be specified explicitly in an idem state.

.. code:: sls

    ensure_resource_exists:
      aws.ec2.vpc.present:
        - acct_profile: my-staging-env
        - name: idem_aws_vpc
        - cidr_block: 10.0.0.0/24

It can also be specified from the command line when executing states.

.. code:: bash

    idem state --acct-profile my-staging-env my_state.sls

It can also be specified from the command line when calling an exec module directly.

.. code:: bash

    idem exec --acct-profile my-staging-env boto3.client.ec2.describe_vpcs

The last step to get up and running is to encrypt the credentials file and add the encryption key and encrypted file
path to the ENVIRONMENT.

The ``acct`` command should be available as ``acct`` is a requisite of ``idem`` and ``idem-aws``.
Encrypt the the credential file.

.. code:: bash

    acct encrypt credentials.yaml

output::

    -A9ZkiCSOjWYG_lbGmmkVh4jKLFDyOFH4e4S1HNtNwI=

Add these to your environment:

.. code:: bash

    export ACCT_KEY="-A9ZkiCSOjWYG_lbGmmkVh4jKLFDyOFH4e4S1HNtNwI="
    export ACCT_FILE=$PWD/credentials.yaml.fernet


If no acct_file is supplied, then the default awscli credentials that are picked-up by botocore will be used.
Missing cli options will be filled in by botocore from awscli config.
The order of config priority is:

#. acct profile
#. idem config file
#. awscli config

You are ready to use idem-aws!

Execution Modules
=================

Once everything has been set up properly, execution modules can be called directly by ``idem``.
Execution modules mirror the namespacing of the boto3.client and boto3.resource modules and have the same parameters.

For example, this is how you could list Vpcs from the command line with idem:

.. code:: bash

    idem exec boto3.client.ec2.describe_vpcs

You can specify parameters as well.
In the case of boto3 resources, args will be passed to the resource constructor and kwargs will be passed to the operation like so:

.. code:: bash

    idem exec boto3.resource.ec2.Vpc.create_subnet vpc-71d00419 CidrBlock="10.0.0.0/24"

States
======

States are also accessed by their relative location in ``idem-aws/idem_aws/states``.
For example, ``idem-aws/idem_aws/states/aws/ec2/vpc.py`` contains a function ``absent()``.
In my state file I can create a state that uses the ``absent`` function like so.

my_state.sls:

.. code:: sls

    idem_aws_test_vpc:
      aws.ec2.vpc.absent:
        - name: "idem_aws_test_vpc"

This state can be executed with:

.. code:: bash

    idem state my_state.sls

``idem state`` also has some flags that can significantly boost the scalability and performance of the run.
Let's use this new state which verifies that 100 vpcs are absent:

.. code:: sls

    {% for i in range(100) %}
    idem_aws_test_vpc_{{i}}:
      aws.ec2.vpc.absent:
        - name: "idem_aws_test_vpc_{{i}}"
    {% endfor -%}

State can be executed with ``--runtime parallel`` to make full use of idem's async execution calls:

.. code:: bash

    idem state --runtime parallel my_state.sls

Remote storage for enforced state management
--------------------------------------------

Idem-aws supports remote storage for Idem's enforced state management feature. That is, Idem can
store esm data on AWS S3 bucket. DynamoDB will be used as a file lock to prevent multiple users/processes
access the same storage file concurrently. To use remote storage, the esm profile need to be added to
the credential profile like the following:

.. code:: sls

    aws:
      default:
        use_ssl: True
        aws_access_key_id: AAAAAAAAA5CDFSDER3UQ
        aws_secret_access_key: eHjPASFWERSFwVXKlsdfS4afD
        region_name: eu-west-2
        esm:
          bucket: "idem-state-storage-bucket"
          dynamodb_table: "idem-state-storage-table"
          key: "/idem-state/demo-storage.json"

This esm file means that Idem will use AWS S3 bucket "idem-state-storage-bucket" and DynamoDB table
"idem-state-storage-table" in region eu-west-2. The "key" is the file path to which the esm data
will be read and stored. Both S3 bucket and DynamoDB table need to be created before using the feature.
The DynamoDB table should have the primary key as string "LockID" and nothing else.
