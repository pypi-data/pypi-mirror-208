import sys
from cryptography.fernet import Fernet


def write_key(file_name):
    key = Fernet.generate_key()

    with open(file_name, 'wb') as file:
        file.write(key)


if __name__ == '__main__':
    if len(sys.argv) < 1:
        sys.exit('Missing required argument: output_file_name')

    fn = sys.argv[1]
    write_key(fn)
