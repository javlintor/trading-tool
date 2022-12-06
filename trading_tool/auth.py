import os

# Dictionary containing valid username and password pairs
# The password for each user is read from an environment variable with the corresponding name
VALID_USERNAME_PASSWORD_PAIRS = {
    'lucas': os.environ.get("LUCAS_PASS"),
    'javi': os.environ.get("JAVI_PASS")
}