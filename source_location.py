import boto3
import os

mt = boto3.client("mediatailor")

def lambda_handler(event, context):

    detail = event["detail"]
    metadata = detail.get("userMetadata", {})

    folder = metadata.get("folder", None)

    if not folder:
        raise Exception("ERROR: No se envió 'folder' en el UserMetadata.")

    print("Carpeta:", folder)

    hls_path = f"/convert/{folder}/playlist.m3u8"
    print("HLS path:", hls_path)

    vod_name = folder

    SOURCE_LOCATION_NAME = os.environ["SOURCE_LOCATION_NAME"]

    response = mt.create_vod_source(
        SourceLocationName=SOURCE_LOCATION_NAME,
        VodSourceName=vod_name,
        HttpPackageConfigurations=[
            {
                "Type": "HLS",
                "Path": hls_path,
                "SourceGroup": "source-group-1"
            }
        ]
    )

    print("MediaTailor -> OK:", response)

    return {
        "status": "ok",
        "folder": folder,
        "vodName": vod_name,
        "hls_path": hls_path
    }
