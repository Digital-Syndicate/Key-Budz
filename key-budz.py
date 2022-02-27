#!/usr/bin/python3
#replace above with your interpreter

#NEED TO ADD RELEVANT IMPORTS


##Raw Code from Cardano Lotto Engine.  Needs cleanup.

#TODO 1) create API from running application that you can securely inject passcode.
#2) On start, ask if we are a) encrypting keys, and if yes, what and where, b) change the password on existing
#keys, c) injecting a key in to a system that is waiting at startup.
#3) Set up a simple query tool to parse a hash string in to 32 bits.  i.e. last 32 bits, first 32 bits, first 16/last 16, every other, etc.
#4) On new setup, create a human readable text file to be encrypted.  Verify that the decrypted text reads correctly before injecting keys
# in to production system.
#5) write code for production server to COSE sign transactions in memory

#Below code is not production ready, but is availble to view if you would like to use or add to the project
#Huth S0lo Feb 27, 2022 v0.1

##########Encrypt / Decrypt keys
#COMMON_ENCRYPTION_KEY = getpass()
#AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

def lock_up_keys():
    load_system_control()
    COMMON_ENCRYPTION_KEY = getpass()
    i = 0
    while i < len(system_control):
        collection = system_control['collection'][i]
        p = 0
        while p < system_control['pools_participating'][i]:
            key_type = f'pool{(p+1)}'
            encrypted_key = encrypt_key(collection, key_type)
            update_string = f"UPDATE cardano_keys set pool{(p+1)}_stake = '{encrypted_key}' WHERE collection = '{collection}'"
            psql.execute(f'{update_string}', database)
            p += 1
        key_type = f'custodian'
        encrypted_key = encrypt_key(collection, key_type)
        update_string = f"UPDATE cardano_keys set custodian_wallet = '{encrypted_key}' WHERE collection = '{collection}'"
        psql.execute(f'{update_string}', database)
        key_type = f'prize'
        encrypted_key = encrypt_key(collection, key_type)
        update_string = f"UPDATE cardano_keys set custodian2_wallet = '{encrypted_key}' WHERE collection = '{collection}'"
        psql.execute(f'{update_string}', database)
        i += 1


def get_common_cipher():
    return AES.new(COMMON_ENCRYPTION_KEY, AES.MODE_CBC, COMMON_16_BYTE_IV_FOR_AES)

def decrypt_key(encrypted_key):
    common_cipher = get_common_cipher()
    raw_ciphertext = base64.b64decode(encrypted_key)
    decrypted_message_with_padding = common_cipher.decrypt(raw_ciphertext)
    json_string = decrypted_message_with_padding.decode('utf-8').strip()
    decrypted_key = json.loads(json_string)

def encrypt_key(collection, key_type):
    folder = f"./key_files/{collection}/"
    f = open(folder + f'cardano_{key_type}.skey')
    key_content = json.load(f)
    f.close()
    json_string = json.dumps(key_content)
    common_cipher = get_common_cipher()
    cleartext_length = len(json_string)
    next_multiple_of_16 = 16 * math.ceil(cleartext_length / 16)
    padded_cleartext = json_string.rjust(next_multiple_of_16)
    raw_ciphertext = common_cipher.encrypt(padded_cleartext)
    encrypted_key = base64.b64encode(raw_ciphertext).decode('utf-8')
    return encrypted_key