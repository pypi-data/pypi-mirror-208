# params-aws
Load and Save typed Parameters in AWS Datastore

## Install
```
pip install params-aws
```

## Using the library
Ensure that `aws_access_key_id` and `aws_secret_access_key` is properly set in ~/.aws/credentials. 
Or any place where boto3 would recognize - https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

### Import
```
from params_aws import params_aws
from params_aws import model
```

### List parameters
```
>>> params_aws.get_parameter_names()
['test']
```

### Get parameter with type
This will be cached for 12 hour
```
>>> params_aws.get_parameter('test', model.DBConfig, cached=True)
DBConfig(host='host', user='username', password='password', port=5432, ssl=False)
```

### Put parameter
We should use the cli (see below)
```
>>> params_aws.put_parameter('test', model.DBConfig, 'value')
```

## CLI
```
>>> params_aws_cli names
test
test2

>>> params_aws_cli types
DBConfig
GGAPIConfig

>>> params_aws_cli get-value test
{
  "host": "host",
  "user": "username",
  "password": "password",
  "port": 5432,
  "ssl": false
}

>>> params_aws_cli get test DBConfig
host='host' user='username' password='password' port=5432 ssl=False

>>> params_aws_clit put test DBConfig
(launches an editor which saves and validate on exit)
```