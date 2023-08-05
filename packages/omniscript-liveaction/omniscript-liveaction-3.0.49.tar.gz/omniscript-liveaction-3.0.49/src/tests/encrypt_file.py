# import required module
import sys
from encryption_util import EncryptionUtil


if __name__ == '__main__':
    if len(sys.argv) < 1:
        sys.exit("Missing required argument: key")

    key = sys.argv[1]
    EncryptionUtil(key).encrypt_file('local.device.properties', 'device.encrypted')
