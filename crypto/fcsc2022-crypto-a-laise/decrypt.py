from string import ascii_lowercase

def vigenere_decrypt(ciphertext: str, key: str) -> str:
    result = []
    key = key.lower()
    index = 0  # We want to keep track of the current character in the key

    for char in ciphertext:
        if char.isalpha(): # Ignore space and punctuations
            char_pos = ascii_lowercase.index(char.lower())
            key_pos = ascii_lowercase.index(key[index % len(key)])

            # Here, we evaluate the character
            m_i = (char_pos - key_pos) % 26

            # Then, we turn back the position into an actual letter
            decrypted_char = ascii_lowercase[m_i].upper()
            if char.isupper(): # uppercases arent changed at all
                decrypted_char = decrypted_char.upper()

            result.append(decrypted_char)

            index += 1
        else:
            # No changes were applied, just append
            result.append(char)
            
    return ''.join(result)

print(vigenere_decrypt(("Gqfltwj emgj clgfv ! Aqltj rjqhjsksg ekxuaqs, ua xtwk n&#39;feuguvwb gkwp xwj, ujts f&#39;npxkqvjgw nw tjuwcz ugwygjtfkf qz uw efezg sqk gspwonu. Jgsfwb-aqmu f Pspygk nj 29 cntnn hqzt dg igtwy fw xtvjg rkkunqf."), "FCSC"))