import subprocess
import sys

def main():
    try:
        # Run chess_main.py with a 2-second timeout
        result = subprocess.run(
            [sys.executable, 'ChessMain.py'],
            timeout=2,
            capture_output=True,
            text=True
        )
        # Print stdout and stderr if the process completed within timeout
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
    except subprocess.TimeoutExpired as e:
        # Handle timeout: print whatever output was captured before timeout
        print("Process timed out after 2 seconds.")
        print("STDOUT (up to timeout):")
        print(e.stdout)
        print("STDERR (up to timeout):")
        print(e.stderr)

if __name__ == "__main__":
    main()