def check_ec2_security_groups(session):
    client = session.client('ec2')
    findings = []

    try:
        response = client.describe_security_groups()

        print("Listing EC2 security groups...")

        for sg in response['SecurityGroups']:
            group_name = sg['GroupName']
            group_id = sg['GroupId']
            for permission in sg['IpPermissions']:
                protocol = permission.get('IpProtocol', 'unknown')
                from_port = permission.get('FromPort')
                to_port = permission.get('ToPort')
                port_info = "all traffic" if protocol == '-1' else f"{protocol} {from_port} - {to_port}"
                
                for ip_range in permission.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        findings.append({
                            "resource": group_name,
                            "issue": f"Security group {group_name} ({group_id}) has open access to the internet on port {port_info}",
                            "severity": "HIGH",
                            "service": "EC2",
                        })
                
                for ipv6_range in permission.get('Ipv6Ranges', []):
                    if ipv6_range.get('CidrIpv6') == '::/0':
                        findings.append({
                            "resource": group_name,
                            "issue": f"Security group {group_name} ({group_id}) has open access to the internet on port {port_info} (IPv6)",
                            "severity": "HIGH",
                            "service": "EC2",
                        })
    
    except Exception as e:
        print(f"Error describing security groups: {e}")
    
    return findings