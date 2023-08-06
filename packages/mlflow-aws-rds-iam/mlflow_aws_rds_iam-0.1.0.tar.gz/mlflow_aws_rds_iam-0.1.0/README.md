MLflow AWS RDS IAM Auth Plugins
===============================

MLflow plugins adding AWS RDS IAM authentication for tracking store and model registry store.


Requirements
------------

- Python 3.10+  
- MLflow 2+  
- Boto3

Only Postgres and MySQL are supported (the AWS RDS database engines supported by MLflow as remote backend store).


Installation
------------

```console
pip install mlflow-aws-rds-iam
```


Getting Started
---------------

The plugins are mainly intented for the use of MLflow in server mode, allowing [AWS RDS IAM authentication](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Connecting.html) for the backend store.

```console
mlflow server --backend-store-uri <database URI> --artifacts-destination <artifact store URI>
```


Configuration
-------------

If a *password* is provided in the database URI, AWS IAM authentication will be skipped, *effectively disabling the plugins*.

*Credentials* are required in order to use AWS IAM authentication. Refer to [Boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) for configuration instructions.

*SSL connection to the database is enabled by default*, but can be disabled with the environment variable `MLFLOW_DISABLE_DB_SSL=true`.


License
-------

This project is licensed under the terms of the MIT license.


A [yzr](https://www.yzr.ai/) Free and Open Source project.
