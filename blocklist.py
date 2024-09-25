"""blocklist.py
THis file contains blocklist of JWT tokens. It will be imported by the app
and the logout resource so that tokens can be added to the blocklist when the user logs out."""

BLOCKLIST = set() # it would be useful to use database for storing the blocklist
