import subprocess

# Define the command to activate the virtual environment and run the script
w4af_command = ['pipenv', 'run', './w4af_api', '--i-am-a-developer', '--no-ssl', 'localhost:5001']

# Define the directory to change to
directory = 'w4af/'

# Start the subprocess
w4af_process = subprocess.Popen(
    w4af_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=directory
)

# Communicate with the subprocess
stdout, stderr = w4af_process.communicate()

# Print the output
print(stdout)
print(stderr)
