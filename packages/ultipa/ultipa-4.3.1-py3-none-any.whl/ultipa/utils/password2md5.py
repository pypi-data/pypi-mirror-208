import hashlib


def passwrod2md5(password: str):
    m = hashlib.md5(password.encode())
    return m.hexdigest().upper()


if __name__ == '__main__':
    ret = passwrod2md5('root')
    ret = passwrod2md5(ret)
    print(ret.upper())
