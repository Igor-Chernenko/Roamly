"""
utils.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Utility functions ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

unorginized file with random utility functions that support code
"""

def is_email(identification: str) -> bool:
    return "@" in identification and "." in identification.split("@")[-1]

#currently allows @.com, or other simple things, later fix with regex
