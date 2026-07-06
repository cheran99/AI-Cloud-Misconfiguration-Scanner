import resource


def is_overly_permissive(statement, resource_name, policy_name):
    if statement['Effect'] == 'Allow':
        if statement['Action'] in ['*', ['*']] or statement['Resource'] in ['*', ['*']]:
            return True
    return False

def summarise_statements(statement):
    resource = statement['Resource']
    if isinstance(resource, str):
        resource = [resource]
    is_wide_open = '*' in resource
    services = {action.split(':')[0] for action in statement['Action']}
    action_count = len(statement['Action'])
    if len(services) > 5:
        summary = f"{action_count} action(s) across services: {', '.join(sorted(services)[:5])} and {len(services) - 5} more, Resource: {'all resources' if is_wide_open else 'scoped resources'}"
    else:
        summary = f"{action_count} action(s) across services: {', '.join(sorted(services))}, Resource: {'all resources' if is_wide_open else 'scoped resources'}"
    return summary

def check_iam_users(session):
    client = session.client('iam')
    findings = []

    try:
        paginator = client.get_paginator('list_users')
        page_iterator = paginator.paginate()

        print("Listing IAM users...")

        for page in page_iterator:
            for user in page['Users']:
                user_name = user['UserName']
                policy = None
                managed_policy = None

                try:
                    policy_paginator = client.get_paginator('list_user_policies')
                    policy_iterator = policy_paginator.paginate(UserName=user_name)
                    for policy_page in policy_iterator:
                        for policy in policy_page['PolicyNames']:
                            response = client.get_user_policy(
                                UserName=user_name,
                                PolicyName=policy
                            )

                            for statement in response['PolicyDocument']['Statement']:
                                if is_overly_permissive(statement, user_name, "inline"):
                                    findings.append({
                                        "resource": user_name,
                                        "issue": f"{user_name} has overly permissive inline policy",
                                        "severity": "HIGH",
                                        "service": "IAM",
                                    })

                except client.exceptions.NoSuchEntityException:
                    print(f"No policy found for user {user_name} with policy name {policy}")
                    continue

                try:
                    managed_policy_paginator = client.get_paginator('list_attached_user_policies')
                    managed_policy_iterator = managed_policy_paginator.paginate(UserName=user_name)
                    for managed_policy_page in managed_policy_iterator:
                        for managed_policy in managed_policy_page['AttachedPolicies']:
                            managed_policy_response = client.get_policy_version(
                                PolicyArn=managed_policy['PolicyArn'],
                                VersionId=client.get_policy(PolicyArn=managed_policy['PolicyArn'])['Policy']['DefaultVersionId']
                            )

                            for statement in managed_policy_response['PolicyVersion']['Document']['Statement']:
                                if is_overly_permissive(statement, user_name, "managed"):
                                    findings.append({
                                        "resource": user_name,
                                        "issue": f"{user_name} has overly permissive managed policy",
                                        "severity": "HIGH",
                                        "service": "IAM",
                                    })

                except client.exceptions.NoSuchEntityException:
                    print(f"No managed policy found for user {user_name} with managed policy name {managed_policy['PolicyName'] if managed_policy is not None else None}")
                    continue

        group_paginator = client.get_paginator('list_groups')
        group_iterator = group_paginator.paginate()

        print("Listing IAM groups...")

        for group_page in group_iterator:
            for group in group_page['Groups']:
                group_name = group['GroupName']
                policy = None
                managed_policy = None
                inline_found = False
                managed_found = False

                try:
                    group_policy_paginator = client.get_paginator('list_group_policies')
                    group_policy_iterator = group_policy_paginator.paginate(GroupName=group_name)
                    for group_policy_page in group_policy_iterator:
                        for group_policy in group_policy_page['PolicyNames']:
                            response = client.get_group_policy(
                                GroupName=group_name,
                                PolicyName=group_policy
                            )

                            for statement in response['PolicyDocument']['Statement']:
                                if is_overly_permissive(statement, group_name, "inline"):
                                    inline_found = True
                
                except client.exceptions.NoSuchEntityException:
                    print(f"No policy found for group {group_name} with policy name {group_policy}")
                    continue

                try:
                    managed_group_policy_paginator = client.get_paginator('list_attached_group_policies')
                    managed_group_policy_iterator = managed_group_policy_paginator.paginate(GroupName=group_name)
                    for managed_group_policy_page in managed_group_policy_iterator:
                        for managed_group_policy in managed_group_policy_page['AttachedPolicies']:
                            managed_group_policy_response = client.get_policy_version(
                                PolicyArn=managed_group_policy['PolicyArn'],
                                VersionId=client.get_policy(PolicyArn=managed_group_policy['PolicyArn'])['Policy']['DefaultVersionId']
                            )

                            for statement in managed_group_policy_response['PolicyVersion']['Document']['Statement']:
                                if is_overly_permissive(statement, group_name, "managed"):
                                    managed_found = True

                except client.exceptions.NoSuchEntityException:
                    print(f"No managed policy found for group {group_name} with managed policy name {managed_group_policy['PolicyName'] if managed_group_policy is not None else None}")
                    continue

                try:
                    if inline_found or managed_found:
                        group_response = client.get_group(GroupName=group_name)
                        affected_users_list = [user['UserName'] for user in group_response['Users']]
                
                        if affected_users_list:
                            findings.append({
                                "resource": group_name,
                                "issue": f"{group_name} has overly permissive {('inline' if inline_found else 'managed') if not (inline_found and managed_found) else 'inline and managed'} policy",
                                "affected_users": affected_users_list,
                                "severity": "HIGH",
                                "service": "IAM",
                            })
                        else:
                            findings.append({
                                "resource": group_name,
                                "issue": f"{group_name} has no users but has overly permissive {('inline' if inline_found else 'managed') if not (inline_found and managed_found) else 'inline and managed'} policies",
                                "affected_users": "None",
                                "severity": "HIGH",
                                "service": "IAM",
                            })
                        continue
                except client.exceptions.NoSuchEntityException:
                    print(f"No users found for group {group_name}")
                    continue

    except Exception as e:
        print(f"Error occurred while fetching users: {e}")
    
    return findings

def check_iam_roles(session):
    client = session.client('iam')
    findings = []
    
    try:
        paginator = client.get_paginator('list_roles')
        page_iterator = paginator.paginate()

        print("Listing IAM roles...")

        for page in page_iterator:
            for role in page['Roles']:
                role_name = role['RoleName']
                policy = None
                managed_policy = None

                try:
                    policy_paginator = client.get_paginator('list_role_policies')
                    policy_iterator = policy_paginator.paginate(RoleName=role_name)
                    for policy_page in policy_iterator:
                        for policy in policy_page['PolicyNames']:
                            response = client.get_role_policy(
                                RoleName=role_name,
                                PolicyName=policy
                            )
                            inline_found = False

                            for statement in response['PolicyDocument']['Statement']:
                                if is_overly_permissive(statement, role_name, "inline"):
                                    inline_found = True
                            
                            if inline_found:
                                specific_statement = [summarise_statements(statement) for statement in response['PolicyDocument']['Statement'] if is_overly_permissive(statement, role_name, "inline") == True]
                                findings.append({
                                    "resource": role_name,
                                    "issue": f"{role_name} has overly permissive inline policy involving:\n{'\n '.join(specific_statement)}",
                                    "severity": "HIGH",
                                    "service": "IAM",
                                })

                except client.exceptions.NoSuchEntityException:
                    print(f"No policy found for role {role_name} with policy name {policy}")
                    continue

                try:
                    managed_policy_paginator = client.get_paginator('list_attached_role_policies')
                    managed_policy_iterator = managed_policy_paginator.paginate(RoleName=role_name)
                    for managed_policy_page in managed_policy_iterator:
                        for managed_policy in managed_policy_page['AttachedPolicies']:
                            managed_policy_response = client.get_policy_version(
                                PolicyArn=managed_policy['PolicyArn'],
                                VersionId=client.get_policy(PolicyArn=managed_policy['PolicyArn'])['Policy']['DefaultVersionId']
                            )
                            managed_found = False
                        
                            for statement in managed_policy_response['PolicyVersion']['Document']['Statement']:
                                if is_overly_permissive(statement, role_name, "managed"):
                                    managed_found = True
                            
                            if managed_found:
                                specific_statement = [summarise_statements(statement) for statement in managed_policy_response['PolicyVersion']['Document']['Statement'] if is_overly_permissive(statement, role_name, "managed") == True]
                                findings.append({
                                    "resource": role_name,
                                    "issue": f"{role_name} has overly permissive managed policy involving:\n{'\n '.join(specific_statement)}",
                                    "severity": "HIGH",
                                    "service": "IAM",
                                })

                except client.exceptions.NoSuchEntityException:
                    print(f"No managed policy found for role {role_name} with managed policy name {managed_policy['PolicyName'] if managed_policy is not None else None}")
                    continue

    except Exception as e:
        print(f"Error occurred while fetching roles: {e}")
    
    return findings