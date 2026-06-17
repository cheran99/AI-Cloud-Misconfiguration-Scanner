def check_cloudtrail(session):
    client = session.client("cloudtrail")
    findings = []

    try:
        trails = client.describe_trails()["trailList"]

        if not trails:
            findings.append({
                "issue": "No trails found",
                "severity": "CRITICAL",
                "service": "CloudTrail",
            })
        
        for trail in trails:
            trail_name = trail["Name"]
            try:
                status = client.get_trail_status(
                    Name=trail["TrailARN"]
                    )
                
                if not status["IsLogging"]:
                    findings.append({
                        "resource": trail_name,
                        "issue": "CloudTrail is not logging",
                        "severity": "HIGH",
                        "service": "CloudTrail",
                    })
            
            except client.exceptions.TrailNotFoundException:
                print(f"Trail not found: {trail_name}")
                continue

    except Exception as e:
        print(f"Error occurred while checking CloudTrail: {e}")

    return findings