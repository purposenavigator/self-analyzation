import subprocess
import sys

def login_ecr_with_subprocess(aws_region='us-east-1', ecr_registry=None):
    """Logs in Docker to AWS ECR using CLI commands via subprocess."""
    print(f"--- Starting ECR Login via subprocess for region {aws_region} ---")

    if not ecr_registry:
        # Attempt to construct the registry URL if not provided
        # Note: This requires fetching the AWS Account ID, which adds complexity.
        # For simplicity here, we'll assume a common pattern or require it.
        # A robust solution would call STS get-caller-identity first.
        # Let's just use the example ID for demonstration if not provided.
        # THIS IS NOT A ROBUST WAY TO GET THE REGISTRY URL automatically.
        print("Warning: ecr_registry not provided. Using placeholder based on region.")
        # A better approach would be to require this argument or fetch account ID.
        # For this example, we hardcode the previous example ID. Replace if needed.
        aws_account_id = '885416451907'
        ecr_registry = f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com"
        print(f"Using assumed registry: {ecr_registry}")


    aws_command = ['aws', 'ecr', 'get-login-password', '--region', aws_region]
    docker_command = ['docker', 'login', '--username', 'AWS', '--password-stdin', ecr_registry]

    try:
        # 1. Get password from AWS CLI
        print(f"Running: {' '.join(aws_command)}")
        aws_process = subprocess.run(
            aws_command, capture_output=True, text=True, check=True
        )
        ecr_password = aws_process.stdout.strip()
        if not ecr_password:
            print("Error: No password received from AWS command.", file=sys.stderr)
            return False

        print("Password retrieved successfully.")

        # 2. Log in Docker using the password via stdin
        print(f"Running: {' '.join(docker_command[:5])} ...") # Avoid printing registry twice if complex
        docker_process = subprocess.run(
            docker_command, input=ecr_password, capture_output=True, text=True, check=True
        )
        print("Docker login successful!")
        print("Docker Output:\n", docker_process.stdout)
        if docker_process.stderr:
             print("Docker Stderr:\n", docker_process.stderr)
        return True

    except FileNotFoundError as e:
        print(f"Error: Command not found: {e.filename}", file=sys.stderr)
        print("Ensure AWS CLI and Docker are installed and in your PATH.", file=sys.stderr)
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(e.cmd)}", file=sys.stderr)
        print(f"Return code: {e.returncode}", file=sys.stderr)
        print(f"Stdout:\n{e.stdout}", file=sys.stderr)
        print(f"Stderr:\n{e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    # You might need to provide the correct registry URL for your account
    # e.g., my_registry = "123456789012.dkr.ecr.us-east-1.amazonaws.com"
    # success = login_ecr_with_subprocess(ecr_registry=my_registry)
    success = login_ecr_with_subprocess() # Uses placeholder registry

    print("\n--- Subprocess ECR Login Finished ---")
    if success:
        print("Outcome: Login successful via subprocess.")
    else:
        print("Outcome: Login failed via subprocess.")