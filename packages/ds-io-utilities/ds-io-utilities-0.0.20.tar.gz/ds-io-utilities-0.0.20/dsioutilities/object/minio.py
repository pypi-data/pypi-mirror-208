from ..utils import packages_are_installed
import logging

if not packages_are_installed(["s3fs", "minio"]): 
    message = "Please install minio (https://pypi.org/project/minio/) and s3fs (https://pypi.org/project/s3fs/) if you want to use datasets contained in Minio."
    logging.error(message)
    exit(1)
else:

    from ..utils import input_or_output, get_asset_property


    def get_path(name):
        
        bucket_name = get_asset_property(asset_name=name, property="minio_bucket")

        if input_or_output(name) == "input":
            return "s3://" + bucket_name + "/" + get_asset_property(name)
        elif input_or_output(name) == "output":
            return "s3://" + bucket_name + "/" + get_asset_property(name)
        else:
            raise Exception("Error: cannot establish if dataset is an input or output one! Are you sure the name is right?")

    def get_metadata(name):

        use_ssl = get_asset_property(asset_name=name, property="use_ssl") if get_asset_property(asset_name=name, property="use_ssl") is not None else False

        # Get credentials
        minio_url = get_asset_property(asset_name=name, property="minIO_URL")
        access_key = get_asset_property(asset_name=name, property="minIO_ACCESS_KEY")
        secret_key = get_asset_property(asset_name=name, property="minIO_SECRET_KEY")
        bucket_name = get_asset_property(asset_name=name, property="minio_bucket")

        metadata = {"type": "minio", 
                    "url": minio_url,
                    "access_key": access_key,
                    "secret_key": secret_key,
                    "bucket_name": bucket_name,
                    "use_ssl": use_ssl}

        return metadata