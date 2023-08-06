#! /usr/bin/python
import sys
import os
import base64
from .lib.Argument import Argument
Arg=Argument(sys.argv)

def Encoding(message):
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    return base64_message

def Decoding(base64_message):
    # base64_message = "c3JpZGhhcg=="
    decoded_bytes = base64.b64decode(base64_message)
    decoded_message = decoded_bytes.decode('utf-8')
    return decoded_message

def main():
    if Arg.hasCommands(["base64"]):
        if Arg.hasCommands(["Encode"]) and Arg.hasOptionValue("--string"):
            string = Arg.getoptionvalue("--string")
            encoded_message = Encoding(string)
            print(encoded_message)
        elif Arg.hasCommands(["Decode"]) and Arg.hasOptionValue("--string"): 
            string = Arg.getoptionvalue("--string")
            decoded_message = Decoding(string)
            print(decoded_message) 
    
if __name__ == "__main__":
    main()