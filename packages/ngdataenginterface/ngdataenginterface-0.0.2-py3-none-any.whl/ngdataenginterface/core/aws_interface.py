import json


def get_object_aws(user_client, bucket_name, object_name):
    return user_client.get_object(
        Bucket=bucket_name,
        Key=object_name,
    )["Body"].read()


def put_object_aws(user_client, bucket_name, object_name, object):
    return user_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=bytes(json.dumps(object).encode("UTF-8")),
    )


def concat_multiple_data_events(events):
    mult_data = ""

    for event in events:
        mult_data += json.dumps(event) + "\n"

    return mult_data[:-1].encode("UTF-8")


def put_multiple_objects_aws_single_file(
    user_client, bucket_name, object_name, objects
):
    concat_mult_objects = concat_multiple_data_events(objects)

    return user_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=concat_mult_objects,
    )


def list_objects_key_aws(client_resource, bucket_name, path):
    bucket_resource = client_resource.Bucket(bucket_name)
    objects_key = []

    for object_summary in bucket_resource.objects.filter(Prefix=path):
        objects_key.append(object_summary.key)

    return objects_key


def list_objects_url_aws(client_resource, bucket_name, path):
    bucket_resource = client_resource.Bucket(bucket_name)
    objects_url = []
    for object_summary in bucket_resource.objects.filter(Prefix=path):
        objects_url.append(f"s3://{object_summary.bucket_name}/{object_summary.key}")
    return objects_url


def delete_objects_aws(client_resource, bucket_name, path):
    # Delete Object Path from Unprocessed EventFiles
    bucket = client_resource.Bucket(bucket_name)
    return bucket.objects.filter(Prefix=path).delete()  # todo alert error
