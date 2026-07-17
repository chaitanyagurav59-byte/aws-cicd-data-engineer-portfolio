import boto3
import json
import os
import tempfile
import zipfile
import mimetypes
import shutil

codepipeline = boto3.client("codepipeline")

WEBSITE_BUCKET = "chaitanya-data-engineer-portfolio-web"


def lambda_handler(event, context):

    print("Starting portfolio deployment...")

    job_id = None

    try:
        job_data = event["CodePipeline.job"]
        job_id = job_data["id"]

        artifact_credentials = job_data["data"]["artifactCredentials"]

        artifact_s3 = boto3.client(
            "s3",
            aws_access_key_id=artifact_credentials["accessKeyId"],
            aws_secret_access_key=artifact_credentials["secretAccessKey"],
            aws_session_token=artifact_credentials["sessionToken"]
        )

        website_s3 = boto3.client("s3")

        input_artifacts = job_data["data"]["inputArtifacts"]

        if not input_artifacts:
            raise Exception(
                "No input artifact received from CodePipeline"
            )

        artifact = input_artifacts[0]

        artifact_location = artifact["location"]["s3Location"]

        artifact_bucket = artifact_location["bucketName"]
        artifact_key = artifact_location["objectKey"]

        print(f"Artifact bucket: {artifact_bucket}")
        print(f"Artifact key: {artifact_key}")

        temp_directory = tempfile.gettempdir()

        zip_path = os.path.join(
            temp_directory,
            "source.zip"
        )

        extract_path = os.path.join(
            temp_directory,
            "portfolio"
        )

        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)

        if os.path.exists(zip_path):
            os.remove(zip_path)

        os.makedirs(
            extract_path,
            exist_ok=True
        )

        print("Downloading CodePipeline artifact...")

        artifact_s3.download_file(
            artifact_bucket,
            artifact_key,
            zip_path
        )

        print("Artifact downloaded successfully.")

        print("Extracting artifact...")

        with zipfile.ZipFile(zip_path, "r") as zip_file:
            zip_file.extractall(extract_path)

        print("Artifact extracted successfully.")

        allowed_files = {
            "index.html",
            "style.css",
            "script.js"
        }

        uploaded_files = []

        for root, directories, files in os.walk(extract_path):

            for file_name in files:

                if file_name not in allowed_files:
                    continue

                local_file_path = os.path.join(
                    root,
                    file_name
                )

                content_type, _ = mimetypes.guess_type(
                    local_file_path
                )

                if content_type is None:
                    content_type = "application/octet-stream"

                print(f"Uploading {file_name}...")

                website_s3.upload_file(
                    local_file_path,
                    WEBSITE_BUCKET,
                    file_name,
                    ExtraArgs={
                        "ContentType": content_type
                    }
                )

                uploaded_files.append(file_name)

                print(
                    f"{file_name} uploaded successfully."
                )

        required_files = {
            "index.html",
            "style.css",
            "script.js"
        }

        missing_files = required_files - set(uploaded_files)

        if missing_files:
            raise Exception(
                f"Missing website files: {sorted(missing_files)}"
            )

        print("Portfolio deployment successful.")
        print(f"Uploaded files: {uploaded_files}")

        codepipeline.put_job_success_result(
            jobId=job_id
        )

        print("Success reported to CodePipeline.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Portfolio deployed successfully",
                "uploaded_files": uploaded_files
            })
        }

    except Exception as error:

        print(f"Deployment failed: {str(error)}")

        if job_id:

            try:
                codepipeline.put_job_failure_result(
                    jobId=job_id,
                    failureDetails={
                        "message": str(error)[:1000],
                        "type": "JobFailed"
                    }
                )

            except Exception as pipeline_error:

                print(
                    f"Could not report failure: {str(pipeline_error)}"
                )

        raise