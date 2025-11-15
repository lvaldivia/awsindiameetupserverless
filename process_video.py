import json
import boto3
import urllib.parse
import uuid
import os

s3 = boto3.client("s3")

MEDIACONVERT_ROLE = os.environ["MEDIACONVERT_ROLE"]
TEMPLATE_BUCKET = os.environ["TEMPLATE_BUCKET"]
TEMPLATE_KEY = os.environ["TEMPLATE_KEY"]


def get_mediaconvert_client():
    client = boto3.client("mediaconvert")
    endpoint = client.describe_endpoints()["Endpoints"][0]["Url"]
    print(f"MediaConvert endpoint: {endpoint}")
    return boto3.client("mediaconvert", endpoint_url=endpoint)


def lambda_handler(event, context):

    mc = get_mediaconvert_client()

    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

    if not key.startswith("videos/"):
        print("Ignored, not inside /videos/")
        return {"statusCode": 200, "body": "ignored"}

    print(f"New upload: {bucket}/{key}")

    job_id = str(uuid.uuid4())

    s3_input = f"s3://{bucket}/{key}"
    s3_output = f"s3://{bucket}/convert/{job_id}/playlist"

    print("Input:", s3_input)
    print("Output:", s3_output)

    template_obj = s3.get_object(Bucket=TEMPLATE_BUCKET, Key=TEMPLATE_KEY)
    job_settings = json.loads(template_obj["Body"].read())

    job_settings["Inputs"][0]["FileInput"] = s3_input
    job_settings["OutputGroups"][0]["OutputGroupSettings"]["HlsGroupSettings"]["Destination"] = s3_output

    response = mc.create_job(
        Role=MEDIACONVERT_ROLE,
        Settings=job_settings,
         UserMetadata={
            "folder": job_id
        }
    )

    playlist_url = f"{s3_output}playlist.m3u8"

    print("Job OK:", response["Job"]["Arn"])
    print("Playlist:", playlist_url)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "ok": True,
            "job": response["Job"]["Arn"],
            "playlist": playlist_url
        })
    }
