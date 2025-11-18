import os
import sys
import subprocess
import argparse

GUNICORN_SERVICE = "prospector.service"

# Assumes 'manage.py' is in the directory where this script is run.

def run_command(command, check_return=True, suppress_output=False, sudo=False):
    """Executes a shell command and prints the output/status."""
    if sudo:
        command = "sudo " + command

    print(f"\n---> Running: {command}")

    try:
        # Use shell=True for convenience, but be mindful of security if accepting user input directly.
        # This script uses fixed/trusted commands.
        result = subprocess.run(
            command,
            shell=True,
            check=check_return,
            text=True,
            capture_output=True
        )
        if not suppress_output:
            print("--- Command Output ---")
            print(result.stdout.strip())
            if result.stderr.strip():
                print("--- Command Error Output (if any) ---")
                print(result.stderr.strip())
            print("----------------------")
        return result
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Command failed with return code {e.returncode}")
        print(f"Stdout:\n{e.stdout}")
        print(f"Stderr:\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n[ERROR] Command not found. Is it installed and in PATH? ({command.split()[0]})")
        sys.exit(1)


def get_user_confirmation(prompt):
    """Prompts the user for a yes/no confirmation."""
    while True:
        response = input(f"{prompt} (y/n): ").lower().strip()
        if response in ('y', 'yes'):
            return True
        elif response in ('n', 'no', ''):
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def handle_migrations():
    """Handles Django makemigrations and migrate if confirmed by the user."""
    if get_user_confirmation("Do you want to run Django migrations (makemigrations and migrate)?"):
        print("\nStarting Django migrations...")
        # Run makemigrations (suppressed output unless it fails)
        run_command("python manage.py makemigrations --no-input", suppress_output=True)
        # Run migrate
        run_command("python manage.py migrate --no-input")
        print("Migrations complete.")
    else:
        print("Skipping migrations.")


def handle_gunicorn_restart():
    """Restarts the Gunicorn service."""
    print(f"\nRestarting Gunicorn service ({GUNICORN_SERVICE})...")
    # Requires sudo access
    run_command(f"systemctl restart {GUNICORN_SERVICE}", sudo=True, suppress_output=True)
    run_command(f"systemctl status {GUNICORN_SERVICE} --no-pager | head -n 3",
                sudo=True)  # Show status for verification
    print("Gunicorn service restarted successfully.")


def get_current_commit_hash():
    """Gets the current git commit hash."""
    try:
        result = run_command("git log -1 --pretty=format:%H", suppress_output=True, check_return=True)
        return result.stdout.strip()
    except:
        return None


# --- Main Functions ---

def deploy_app(target_branch):
    """Performs the full deployment routine."""
    print("--- Starting Deployment Process ---")

    # Get current commit hash before pull for an easy rollback reference
    previous_commit = get_current_commit_hash()
    if previous_commit:
        print(f"Current commit before deploy: {previous_commit[:8]} (Use this for easy rollback)")

    # 1. Pull latest code from the specified target
    print(f"\n1. Pulling latest source code from Git (Target: {target_branch})...")

    # First, ensure we are on the target branch/commit locally
    run_command(f"git checkout {target_branch}")
    # Then pull the latest changes for that branch
    run_command(f"git pull origin {target_branch}")

    # 2. Run Migrations (optional)
    print("\n2. Checking for/running database migrations...")
    handle_migrations()

    # 3. Restart Gunicorn
    print("\n3. Restarting Gunicorn to load new code...")
    handle_gunicorn_restart()

    print("\n--- Deployment Complete! ---")

    if previous_commit:
        print(f"To roll back to the state before this deploy, use the command:")
        # Show rollback command using the previous commit hash
        print(f"python {sys.argv[0]} rollback {previous_commit[:8]}")


def rollback_app(target_commit):
    """Rolls back the application to a specified commit or tag."""
    print(f"--- Starting Rollback Process to target: {target_commit} ---")

    # 1. Fetch tags and checkout target
    print("\n1. Fetching Git tags and checking out target...")
    run_command("git fetch --tags")
    # Reset local changes (optional, but good practice for rollback)
    run_command("git reset --hard")
    run_command(f"git checkout {target_commit}")

    # 2. Run Migrations (optional - usually necessary for a full rollback)
    print("\n2. Checking for/running database migrations for rollback...")
    handle_migrations()  # If the rollback commit has different migrations

    # 3. Restart Gunicorn
    print("\n3. Restarting Gunicorn to load previous code...")
    handle_gunicorn_restart()

    print(f"\n--- Rollback to {target_commit} Complete! ---")
    print("Please thoroughly test the restored system.")


def main():
    """Parses command-line arguments and executes the appropriate function."""
    parser = argparse.ArgumentParser(
        description="Automated Django deployment and rollback script."
    )

    # Define subcommands
    subparsers = parser.add_subparsers(dest='command', required=True, help='Deployment command to execute')

    # Subparser for deploy
    deploy_parser = subparsers.add_parser('deploy',
                                          help='Performs standard deployment (checkout, pull, migrate, restart services)')
    deploy_parser.add_argument(
        'target',
        help='The Git branch or tag/commit to checkout and pull from (e.g., main, stage).'
    )

    # Subparser for rollback (uses the same 'target' positional argument)
    rollback_parser = subparsers.add_parser('rollback', help='Rolls back to a specific Git tag or commit hash')
    rollback_parser.add_argument(
        'target',
        help='The Git tag or commit hash to roll back to (e.g., v1.0.0 or 8a1b3c4f)'
    )

    args = parser.parse_args()

    # Check for correct execution location (where manage.py is)
    if not os.path.exists('manage.py'):
        print(
            "[CRITICAL ERROR] This script must be run from the Django project root directory (where manage.py resides).")
        sys.exit(1)

    if args.command == 'deploy':
        deploy_app(args.target)
    elif args.command == 'rollback':
        rollback_app(args.target)


if __name__ == "__main__":
    main()
