terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "eu-west-2"
}

resource "aws_iam_user"  "scanner_user" {
    name = "ai_scanner_user"
}

resource "aws_iam_policy" "scanner_policy" {
    name   = "ai-scanner-read-only-policy"
    policy = jsonencode ({
        Version = "2012-10-17"
        Statement = [
            {
                Action = [
                    "s3:ListAllMyBuckets",
                    "s3:GetBucketAcl",
                    "s3:GetBucketPolicy",
                    "s3:GetBucketEncryption",
                    "s3:GetPublicAccessBlock",
                    "iam:ListRoles",
                    "iam:GetRolePolicy",
                    "iam:ListAttachedRolePolicies",
                    "ec2:DescribeSecurityGroups",
                    "cloudtrail:DescribeTrails",
                    "cloudtrail:GetTrailStatus",
                ]
                Effect = "Allow"
                Resource = "*"
            },
        ]
    })
}

resource "aws_iam_user_policy_attachment" "attach" {
    user = aws_iam_user.scanner_user.name
    policy_arn = aws_iam_policy.scanner_policy.arn
}