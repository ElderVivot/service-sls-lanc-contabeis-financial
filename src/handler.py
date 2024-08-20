try:
    import unzip_requirements
except ImportError:
    pass

try:
    import io
    import boto3
    import os
    from src.read_lines_and_processed import ReadLinesAndProcessed
    from src.functions import readExcelPandas, returnDataInDictOrArray
except Exception as e:
    print("Error importing libraries", e)

AWS_ACCESS_KEY_ID = os.environ.get('AWS_S3_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_S3_SECRET_ACCESS_KEY')
REGION_NAME = os.environ.get('AWS_S3_REGION')


def main(event, context):

    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION_NAME)

    for item in event.get("Records"):
        eventSource = item.get('eventSource')
        layoutFilter = ''
        if eventSource == 'aws:dynamodb':
            url = item.get("dynamodb").get('NewImage').get('url').get('S')
            layoutFilter = returnDataInDictOrArray(item, ['dynamodb', 'NewImage', 'layoutFilter', 'S'])
            urlSplit = url.split('/')
            bucket = urlSplit[2].split('.')[0]
            key = '/'.join(urlSplit[3:])
            extension = key.split('.')[1]
            fileObj = client.get_object(Bucket=bucket, Key=key)
            fileContent = fileObj['Body'].read()
            fileBytesIO = io.BytesIO(fileContent)
        else:
            s3 = item.get("s3")
            bucket = s3.get("bucket").get("name")
            key = s3.get("object").get("key")
            extension = key.split('.')[1]
            fileObj = client.get_object(Bucket=bucket, Key=key)
            fileContent = fileObj['Body'].read()
            fileBytesIO = io.BytesIO(fileContent)

        extension = extension.lower()
        ReadLinesAndProcessed().executeJobMainAsync(fileBytesIO, key, True, extension, layoutFilter=layoutFilter)
