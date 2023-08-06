from thrivve_core import ThrivveCore
from thrivve_core.helpers.amazon.get_s3_client import get_s3_client


def upload_file(file_binary, file_name, content_type, s3_bucket=None, s3_client=None):
    """Upload a file to an S3 bucket"""
    app = ThrivveCore.get_app()
    # Upload the file
    if not s3_client:
        s3_client = get_s3_client()

    result = s3_client.upload_fileobj(
        file_binary,
        s3_bucket if s3_bucket else app.config.get("S3_BUCKET"),
        file_name,
        ExtraArgs={"ContentType": content_type},
    )
    return result
