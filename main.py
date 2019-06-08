"""This file contains the script to launch the food substitutes program
To launch the program, you have to create a connection file create a DB_info.py
file which contains the following
variables:
HOST = "YourHost"
USER = "YourUserName"
PASSWORD = "YourPassword"
DB = "off"
"""

import classes

LAUNCH = classes.Display()

LAUNCH.application()
