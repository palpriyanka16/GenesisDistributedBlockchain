
import rsa
import codecs
import hashlib

privkey_file = input("Enter private key file name (.pem): ")
with open(privkey_file, "rb") as file:
    privkey_file_contents = file.read()

privkey = rsa.PrivateKey.load_pkcs1(privkey_file_contents)

data = input("Enter data to be signed: ")
data_hash = hashlib.sha256(data.encode()).hexdigest().encode()

signature = rsa.sign(data_hash, privkey, 'SHA-256')
signature_hex = codecs.encode(signature, 'hex').decode()

print()
print("\nTRANSACTION: \n")

print()
print("*" * 60)
print("\nData: \n")
print(data)

print()
print("*" * 60)
print("\nSignature: \n")
print(signature_hex)
print()
print("*" * 60)
