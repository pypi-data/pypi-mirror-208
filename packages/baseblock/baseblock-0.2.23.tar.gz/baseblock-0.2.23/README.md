# Base Block (baseblock)

Base Block of Common Enterprise Python Utilities


## Crypto Base
Usage
```python
from baseblock import CryptoBase

key = CryptoBase.generate_private_key()
```

The `key` is used to both encrypt and decrypt text, like this:
```python
input_text = "Hello, World!"

crypt = CryptoBase(key)

x = crypt.encrypt_str(input_text)
y = crypt.decrypt_str(x)

assert input_text == y
```

The key can also be stored in the environment under **BASEBLOCK_CRYPTO_KEY**.
