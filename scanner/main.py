from scanner.session import create_session
from scanner.checks.iam import check_iam_roles
from scanner.checks.s3 import check_s3_buckets


def run_checks():
    session = create_session()
    findings = []
    # Run IAM checks
    findings.extend(check_iam_roles(session))
    # Run S3 checks
    findings.extend(check_s3_buckets(session))
    return findings

if __name__ == "__main__":
    findings = run_checks()
    for finding in findings:
        print(f"Service: {finding['service']}, Resource: {finding['resource']}, Issue: {finding['issue']}")