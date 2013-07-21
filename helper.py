def rot13(text):
    "Increase every letter in a text by 13 then return a new text"

    new_text = ""
    for char in text:
        if char.isalpha():
            if char.isupper():
                new_char = chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
            else:
                new_char = chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
            new_text += new_char
        else:
            new_text += char
    return new_text
