import boto3


def check_s3_buckets(session):
    client = session.client('s3')
    findings = []
    
    try:
        response = client.list_buckets()

        print("Listing S3 buckets...")

        for bucket in response['Buckets']:
            name = bucket['Name']
            try:
                block_response = client.get_public_access_block(
                    Bucket = name
                )
                config = block_response['PublicAccessBlockConfiguration']
                if not all([
                    config['BlockPublicAcls'],
                    config['IgnorePublicAcls'],
                    config['BlockPublicPolicy'],
                    config['RestrictPublicBuckets']
                ]):
                    findings.append({
                        "resource": bucket['Name'],
                        "issue": "Public Access Block not configured",
                        "severity": "HIGH",
                        "service": "S3",
                    })

            except client.exceptions.NoSuchPublicAccessBlockConfiguration as e:
                findings.append({
                        "resource": bucket['Name'],
                        "issue": "No public access block configuration found",
                        "severity": "HIGH",
                        "service": "S3",
                    })
                
            try:
                encryption_response = client.get_bucket_encryption(
                    Bucket = name
                )
                rules = encryption_response['ServerSideEncryptionConfiguration']['Rules']
                if not any(rule['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] == 'aws:kms' for rule in rules):
                    findings.append({
                        "resource": bucket['Name'],
                        "issue": "Bucket encryption not using AWS KMS",
                        "severity": "HIGH",
                        "service": "S3",
                    })
            except client.exceptions.ServerSideEncryptionConfigurationNotFoundError:
                findings.append({
                    "resource": bucket['Name'],
                    "issue": "No bucket encryption configuration found",
                    "severity": "CRITICAL",
                    "service": "S3",
                })

    except Exception as e:
        print(f"Error listing buckets: {e}")

    return findings