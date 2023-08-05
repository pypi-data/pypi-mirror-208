import rsa
import base64


# encrypt

class Encryptor(object):
    def __init__(self):
        self._private_key = None
        self._public_key = None

    def set_key(self, public, private=None):
        if not public:
            raise Exception('public key is None')
        is_rsa = 'BEGIN RSA PUBLIC KEY' in public  # 关键是有没有`RSA`
        if is_rsa:
            self._public_key = rsa.PublicKey.load_pkcs1(public.encode())
            self._private_key = private and rsa.PrivateKey.load_pkcs1(private.encode())
        else:
            self._public_key = rsa.PublicKey.load_pkcs1_openssl_pem(public.encode())
            self._private_key = private and rsa.PrivateKey.load_pkcs1_openssl_pem(private.encode())

    def set_pem(self, public, private=None):
        # public
        try:
            with open(public, 'r') as file:
                public_key_str = file.read()
        except:
            public_key_str = None
        # private
        try:
            with open(private, 'r') as file:
                private_key_str = file.read()
        except:
            private_key_str = None
        # set key
        self.set_key(public_key_str, private_key_str)

    def encrypt(self, content: str) -> str:
        encrypted = rsa.encrypt(content.encode(), self._public_key)
        result = base64.b64encode(encrypted).decode('utf-8')
        return result

    def decrypt(self, secret: str) -> str:
        decrypted = base64.b64decode(secret.encode())
        result = rsa.decrypt(decrypted, self._private_key).decode()
        return result


def generate_pem_key(name: str='') -> (rsa.PublicKey, rsa.PrivateKey):
    public_key, private_key = rsa.newkeys(1024)
    public = public_key.save_pkcs1('PEM')  # default 'PEM'
    private = private_key.save_pkcs1('PEM')
    if name:
        prefix = name + '_'
        with open(prefix+'public_key.pem', 'wb') as file:
            file.write(public)
        with open(prefix+'private_key.pem', 'wb') as file:
            file.write(private)
    return public_key, private_key


# test


def test1():
    # public, private = generate_pem_key('test')
    public = '''
    -----BEGIN RSA PUBLIC KEY-----
    MIGJAoGBAIDZn/enhx0RRdNioXblQBywJJSuvcIwF8NPXcBaaplD6einSeC2NzoX
    N2sda4nO25hajiQBD41t2a0g5jP4nF1WWnya9ketnJXLZjotRd8VvxI3Swk+9tSQ
    vcJGBEfzhJ9iUuuygHM7SnxzPosDWm9VtYEJsUIavldLWZ4p4X/nAgMBAAE=
    -----END RSA PUBLIC KEY-----
    '''
    private = '''
    -----BEGIN RSA PRIVATE KEY-----
    MIICYAIBAAKBgQCA2Z/3p4cdEUXTYqF25UAcsCSUrr3CMBfDT13AWmqZQ+nop0ng
    tjc6FzdrHWuJztuYWo4kAQ+NbdmtIOYz+JxdVlp8mvZHrZyVy2Y6LUXfFb8SN0sJ
    PvbUkL3CRgRH84SfYlLrsoBzO0p8cz6LA1pvVbWBCbFCGr5XS1meKeF/5wIDAQAB
    AoGAG2CiObfR4J477OdHEYEydyYCD8l1Ll6Tnf8uF2HexoQEnld1PhbZczFdqBfP
    Mq/OPvf2vbWv/Uf6+WtE+zCWH9n1EG3zXme/DhQ2XYG7+unst4il+srtwrPkW8HA
    eci3Cgys0ximi7DkewLjKuJdS9/PcQf5WFZLllpythB5MgkCRQCmQVnvNuZPUl0Y
    WSDn5+9JYzC9pjS0o4ZS3MKSKET+hIellTRuAPgaK5os3a9DBwabSGo5ZN46J+Kt
    bSmxgxk0EN1VRQI9AMZnShZsGt3OK4vvj6Vmd+zfsdDhlbuGL2Ih/O91pWWh8J2B
    ANFw6vlqfXoDqHTegd8MG8IxFCPyP2qFOwJFAIL1QUk73minASvXsSLbQFJ3boJE
    tImBsaH9wMnuLIKrlEnq4JSx8Lx0kgo7SP2sQBj7DqlM+funRVfEgC4SjTzE+ANd
    Ajw+h6k6/eFNzL++v8bnGy9q0Wmqap6VVooyhIHCOrLhIDPEgDbwy4TTDPP085gx
    FTubP6a0AmHVnnDMMqcCRDv3fzyM1cFm3Uc2RV7IqJUC2ekVbDn2MKfUnBlJs6hk
    25fcLCtYJYYAZvLBcUg/bb7bNwZfAmTBWtYOxiXlO9JT9HAI
    -----END RSA PRIVATE KEY-----
    '''

    s = "hello, world"
    en = Encryptor()
    en.set_key(public, private)

    ss = en.encrypt(s)
    print(ss)

    s = en.decrypt(ss)
    print(s)


def test2():
    # public, private = generate_pem_key()
    s = "hello, world"
    en = Encryptor()
    en.set_pem('test_public_key.pem', 'test_private_key.pem')
    ss = en.encrypt(s)
    print(ss)

    s = en.decrypt(ss)
    print(s)


if __name__ == '__main__':
    test1()
