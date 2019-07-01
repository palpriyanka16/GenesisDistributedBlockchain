
import rsa

KEY_SIZE = 512

base_name = input("Enter a base name for the key pairs: ")

(pubkey, privkey) = rsa.newkeys(512)
pubkey_pem = pubkey.save_pkcs1("PEM")
privkey_pem = privkey.save_pkcs1("PEM")

with open(base_name + "_public.pem", "wb") as pubfile:
    pubfile.write(pubkey_pem)

with open(base_name + "_private.pem", "wb") as privfile:
    privfile.write(privkey_pem)

print("Key files created successfully!")
