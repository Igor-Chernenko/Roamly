"""
testing_strings.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ strings for testing ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

provides functions that return diffrent strings for testing
"""
from random import choices
import string #ascii_letters, digits, punctuation

def randomstring(length, ascii_letters: bool = False, digits: bool = False, punctuation:bool = False):
    all_chars = ""

    if ascii_letters:
        all_chars += string.ascii_letters
    if digits:
        all_chars += string.digits
    if punctuation:
        all_chars += string.punctuation
    
    generated_string = choices(all_chars,k=length)
    return "".join(generated_string)

print(randomstring(70, ascii_letters=True, digits=True, punctuation= False))

#----------------------------------[ emails ]----------------------------------
def long_email():
    return "vnst229hcLC8PFcvIfXyMJpxR5oVAk98uCWeKqhMRALoC5GzeDvM38pVaYk3pzfqjClJ4xvnst229hcLC8PFcvIfXyMJpxR5oVAk98uCWeKqhMRALoC5GzeDvM38pVaYk3pzfqjClJ4x@gmail.com"

def wierd_email():
    return "u%B/@3{z=n`rx}JS~}6l75mQ5S$FHC3@u:IxwZ7<fNH<:vhz4=*II!9^~%-3nnx,F#w&F)F@sN0!u@gmail.com"

def very_long_email():
    return """
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@gmail.com
            """
#----------------------------------[ sql injections ]----------------------------------
def sql_injections():
    return [
        "' OR '1'='1",
        "' OR 1=1 --",
        "' OR 'a'='a",
        "'; DROP TABLE users; --",
        "admin' --",
        "' AND 1=1 --",
        "' UNION SELECT NULL, NULL --",
        "' OR SLEEP(30) --",
        "' OR pg_sleep(30) --",
        "' OR IF(1=1,SLEEP(3),0) --"
    ]

def smallest_image():
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\xdac\xf8\x0f\x00\x01\x01\x01\x00"
        b"\x18\xdd\xdc\x0b\x00\x00\x00\x00IEND\xaeB`\x82"
    )