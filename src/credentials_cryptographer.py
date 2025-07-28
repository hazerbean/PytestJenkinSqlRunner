from cryptography.fernet import Fernet

# The key generation and Encryption can be done periodically to ensure there are new values for security reasons

# key = Fernet.generate_key()
key = b'XTiTsoOJq5qTqmkXG_fKAeelckl3qlEiTPFBarJ5ryU='
crypter = Fernet(key)

#user_name = crypter.encrypt(b"")
#print(str(user_name,'utf8'))

#password = crypter.encrypt(b"")
#print(str(password,'utf8'))

def decrypt_credential(cred):
    try:
        decrypted_cred = crypter.decrypt(cred)
        return str(decrypted_cred,'utf8')
    except:
        return None
