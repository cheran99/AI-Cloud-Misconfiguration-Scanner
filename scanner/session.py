import boto3
import botocore
from rich.console import Console

console = Console()

def create_session():
    try:
        session = boto3.Session(profile_name='ai-scanner', region_name='eu-west-2')
        client = session.client('sts')
        identity = client.get_caller_identity()

        account_id = identity["Account"]
        user_id = identity["UserId"]
        arn = identity["Arn"]

        console.print("[green]Successfully created session and fetched caller identity.[/green]")
        console.print(f"[blue]Account ID:[/blue] {account_id}")
        console.print(f"[blue]User ID:[/blue] {user_id}")
        console.print(f"[blue]ARN:[/blue] {arn}")
        return session
    except botocore.exceptions.ClientError as e:
        console.print(f"[red]Error fetching caller identity: {e}[/red]")
        return None


if __name__ == "__main__":
    create_session()