import subprocess
import shlex # For robust command splitting
import os # To construct paths reliably

# Define the Docker image name and tag
image_name = "885416451907.dkr.ecr.us-east-1.amazonaws.com/self-analyzation:host-fargate"

# --- Path Configuration ---
# Get the directory where the script is located.
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the Dockerfile, relative to the script's location.
# Goes up one directory from 'scripts' and then into 'docker'.
dockerfile_path = os.path.join(script_dir, "..", "docker", "Dockerfile")
# Normalize the path to resolve ".." components (e.g., /path/to/scripts/../docker -> /path/to/docker)
dockerfile_path = os.path.normpath(dockerfile_path)


# The build context is the parent directory of the 'scripts' directory (the project root).
build_context = os.path.join(script_dir, "..")
# Normalize the build context path
build_context = os.path.normpath(build_context)


# --- Docker Build Command ---
# Constructs the docker build command
# -t: Specifies the name and optionally a tag in the 'name:tag' format
# -f: Specifies the path to the Dockerfile.
# The last argument is the build context (the directory containing the Dockerfile and other files)
# Using shlex.quote to ensure paths with spaces are handled correctly, though not strictly necessary for these specific paths.
docker_build_command = f"docker build -t {shlex.quote(image_name)} -f {shlex.quote(dockerfile_path)} {shlex.quote(build_context)}"

# --- Docker Push Command ---
# Constructs the docker push command
# This command pushes the image to the specified Docker registry
docker_push_command = f"docker push {shlex.quote(image_name)}"

def run_command(command_str):
    """
    Executes a shell command and prints its output.

    Args:
        command_str (str): The command to execute.

    Returns:
        bool: True if the command was successful, False otherwise.
    """
    print(f"Executing command: {command_str}")
    try:
        # shlex.split is used to correctly split the command string into arguments,
        # which is important for security and correctness, especially with complex commands.
        # The command is executed in the shell, so paths are relative to the script's CWD if not absolute.
        # However, we've made dockerfile_path and build_context absolute or correctly relative.
        process = subprocess.Popen(shlex.split(command_str), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

        # Stream stdout
        print("\n--- Command Output ---")
        for stdout_line in iter(process.stdout.readline, ""):
            if stdout_line:
                print(stdout_line, end="")
        process.stdout.close()

        # Wait for the command to complete and get the return code
        return_code = process.wait()

        # Check for errors
        if return_code != 0:
            print(f"\n--- Error executing command (Code: {return_code}) ---")
            # Print stderr if there was an error
            stderr_output = process.stderr.read()
            if stderr_output:
                print("Error details:")
                print(stderr_output)
            process.stderr.close()
            return False
        else:
            print(f"\n--- Command executed successfully ---")
            process.stderr.close() # Ensure stderr is closed even on success
            return True
    except FileNotFoundError:
        print(f"Error: The command 'docker' was not found. Please ensure Docker is installed and in your PATH.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    print(f"Script directory: {script_dir}")
    print(f"Calculated Dockerfile path: {dockerfile_path}")
    print(f"Calculated Build context: {build_context}")

    print("\n--- Starting Docker Build ---")
    if run_command(docker_build_command):
        print("\n--- Docker Build Successful ---")
        print("\n--- Starting Docker Push ---")
        if run_command(docker_push_command):
            print("\n--- Docker Push Successful ---")
        else:
            print("\n--- Docker Push Failed ---")
    else:
        print("\n--- Docker Build Failed ---")
        print("Skipping Docker Push due to build failure.")


