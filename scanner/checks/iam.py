import boto3

def check_iam_roles(session):
    client = session.client('iam')
    findings = []
    
    try:
        paginator = client.get_paginator('list_roles')
        page_iterator = paginator.paginate()

        for page in page_iterator:
            for role in page['Roles']:
                role_name = role['RoleName']
                try:
                    policy_paginator = client.get_paginator('list_role_policies')
                    policy_iterator = policy_paginator.paginate(RoleName=role_name)
                    for policy_page in policy_iterator:
                        for policy in policy_page['PolicyNames']:
                            PolicyNames = policy
                            response = client.get_role_policy(
                                RoleName=role_name,
                                PolicyName=PolicyNames
                            )

                            for statement in response['PolicyDocument']['Statement']:
                                if statement['Effect'] == 'Allow' and statement['Action'] in ['*', ['*']] and statement['Resource'] in ['*', ['*']]:
                                    findings.append({
                                        "resource": role_name,
                                        "issue": "Role has overly permissive policy",
                                        "severity": "HIGH",
                                        "service": "IAM",
                                    })

                except client.exceptions.NoSuchEntityException:
                    print(f"No policy found for role {role_name} with policy name {PolicyNames}")
                    continue

    except Exception as e:
        print(f"Error occurred while fetching roles: {e}")
    
    return findings