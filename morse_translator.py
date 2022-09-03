# Python program to implement Morse Code Translator
# Inspired by: https://www.geeksforgeeks.org/morse-code-translator-python/

# Pay attention: values out of MORSE_CODE_DICT will be translated as @ character


# Dictionary representing the morse code chart
MORSE_CODE_DICT = {'A': '.-', 'B': '-...',
                   'C': '-.-.', 'D': '-..', 'E': '.',
                   'F': '..-.', 'G': '--.', 'H': '....',
                   'I': '..', 'J': '.---', 'K': '-.-',
                   'L': '.-..', 'M': '--', 'N': '-.',
                   'O': '---', 'P': '.--.', 'Q': '--.-',
                   'R': '.-.', 'S': '...', 'T': '-',
                   'U': '..-', 'V': '...-', 'W': '.--',
                   'X': '-..-', 'Y': '-.--', 'Z': '--..',
                   '1': '.----', '2': '..---', '3': '...--',
                   '4': '....-', '5': '.....', '6': '-....',
                   '7': '--...', '8': '---..', '9': '----.',
                   '0': '-----', ', ': '--..--', '.': '.-.-.-',
                   '?': '..--..', '/': '-..-.', '-': '-....-',
                   '(': '-.--.', ')': '-.--.-',
                   # service values:
                   ' ': ' ', '': ''
                   }


def encrypt(message):
    """
    Function to encrypt the string
    according to the morse code chart
    """
    encrypted_message = ' '.join([MORSE_CODE_DICT[i] if i in MORSE_CODE_DICT.keys() else '@'for i in message])
    return encrypted_message


def decrypt(message):
    """
    Function to decrypt the string
    from morse to english
    """
    morse2en_dict = {v: k for k, v in MORSE_CODE_DICT.items()}
    decrypted_message = ''.join([morse2en_dict[i] if i in morse2en_dict.keys() else '@' for i in message.split(' ')])
    return decrypted_message


# Hard-coded driver function to run the program
def main():
    message = "GEEKS-FOR-GEEKS"
    result = encrypt(message.upper())
    print(result)
    assert result == "--. . . -.- ... -....- ..-. --- .-. -....- --. . . -.- ..."

    message = "--. . . -.- ... -....- ..-. --- .-. -....- --. . . -.- ... "
    result = decrypt(message)
    print(result)
    assert result == "GEEKS-FOR-GEEKS"


# Executes the main function
if __name__ == '__main__':
    main()
