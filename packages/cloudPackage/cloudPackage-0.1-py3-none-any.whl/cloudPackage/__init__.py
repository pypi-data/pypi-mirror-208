import boto3
import json

def getParameter(name):
    session = boto3.Session(
    region_name='ap-south-1',
    aws_access_key_id='AKIAYRRINRHOI2WGJOUL',
    aws_secret_access_key='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')
    ssm = session.client('ssm')
    return ssm.get_parameter(Name=name, WithDecryption=True)


def recurse(d, keys=()):
    if type(d) == dict:
        for k in d:
            for rv in recurse(d[k], keys + (k,)):
                yield rv
    else:
        yield (keys, d)


def getParams(config):
    print("getting parameter from SSM ")
    for compound_key, val in recurse(config):
        out = getParameter(val)
        value = out['Parameter']['Value']
        if (-1 < value.find("{")) & (-1 < value.find("}")):
            result = json.loads(value)
        else:
            result = value
        config[compound_key[0]][compound_key[1]] = result
    
    return config