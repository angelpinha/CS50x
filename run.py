# This script runs and configures the app inside the local machine 
import os
import sys

# Define if the program should run in development mode
# Asks the user for their preference
response = input("Would you like to run in development mode? (y/n): ")

if response not in ['y', 'n']:
    print("Should give a valid response.")
    print("Try again!")
    sys.exit(1)

if response.lower() == 'y':
    development = True
    run_command = "flask --debug run"
else:
    development = False
    run_command = "flask run"

commands = [
    "pip install -e .",
    run_command
]

if development == True:
    print("Running app in DEVELOPMENT mode")
else:
    print("Running app in NORMAL mode")

for command in commands:
    os.system(command)
