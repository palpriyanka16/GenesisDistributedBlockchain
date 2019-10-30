import sys
import rsa

KEY_SIZE = int(sys.argv[1], 10)

if not (KEY_SIZE >= 512 and (KEY_SIZE & (KEY_SIZE-1)) == 0):
    print("Invalid/Small key size")
    exit(1)

base_name = input("Enter a base name for the key pairs: ")

(pubkey, privkey) = rsa.newkeys(KEY_SIZE)
pubkey_pem = pubkey.save_pkcs1("PEM")
privkey_pem = privkey.save_pkcs1("PEM")

with open(base_name + "_public.pem", "wb") as pubfile:
    pubfile.write(pubkey_pem)

with open(base_name + "_private.pem", "wb") as privfile:
    privfile.write(privkey_pem)

print("Key files created successfully!")
