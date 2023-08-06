# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 21:44:59 2022

@author: sarathbabu
"""

def encrypt(text,s=3):
    """Performs Encryption of the text data with a symmetric key number s.
    
    Parameters:
        text(string) : Input text to be encrypted
        
        s(int) : Default value = 3, Symmetric Key number to perform ciphering
        
    Returns:
        string: Encrypted Input text 
    """
    result = ""
    # transverse the plain text
    for i in range(len(text)):
        char = text[i]
        # Encrypt uppercase characters in plain text
    
        if (char.isupper()):
            result += chr((ord(char) + s-65) % 26 + 65)
        # Encrypt lowercase characters in plain text
        else:
            result += chr((ord(char) + s - 97) % 26 + 97)
    return result

def decrypt(text,s=3):
    """Performs Decryption of the text data with a symmetric key number s.
    
    Parameters:
        text(string) : Input text to be decrypted
        
        s(int) : Default value = 3, Symmetric Key number to perform ciphering
        
    Returns:
        string: Decrypted Input text 
    """
    result = ""
    # transverse the plain text
    for i in range(len(text)):
        char = text[i]
        # Decrypt uppercase characters in plain text

        if (char.isupper()):
            result += chr((ord(char) - s-65) % 26 + 65)
        # Decrypt lowercase characters in plain text
        else:
            result += chr((ord(char) - s - 97) % 26 + 97)
    return result