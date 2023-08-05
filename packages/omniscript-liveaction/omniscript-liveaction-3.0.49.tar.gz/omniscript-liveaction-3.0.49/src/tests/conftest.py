import pytest
import keyring
import os
import socket
import sys
import tempfile

from omniscript import omniscript


def pytest_addoption(parser):
    """ Parser for command line arguments """
    parser.addoption('--host', action='store', type=str,
                     default='localhost', help='Host IP Address')
    parser.addoption('--port', action='store', type=int,
                     default=443, help='Engine Port')
    parser.addoption('--secure', action='store_true', default=True,
                     help='Whether this is a secure connection')
    parser.addoption('--user', action='store', type=str,
                     default='root', help='User account name')
    parser.addoption('--password', action='store', type=str,
                     default=None, help='Host password')
    parser.addoption('--performance_logging', action='store_true',
                     default=False, help='Begin engine performance logging')
    parser.addoption('--virtual', action='store_true',
                     help='Engine is running on a virtual machine')


def set_token(host: str, user: str, token: str, port: int):
    """ Helper function to set the token """
    try:
        ip = [str(i[4][0]) for i in socket.getaddrinfo(host, port)][0]
    except Exception:
        ip = host
    label = f'{user}:token'

    keyring.set_password(ip, label, token.decode() if token else None)


@pytest.fixture(scope='session')
def host(pytestconfig) -> str:
    """ Get the host argument """
    return pytestconfig.getoption('--host')


@pytest.fixture(scope='session')
def port(pytestconfig) -> int:
    """ Get the port argument """
    return pytestconfig.getoption('--port')


@pytest.fixture(scope='session')
def secure(pytestconfig) -> bool:
    """ Get the secure argument """
    return pytestconfig.getoption('--secure')


@pytest.fixture(scope='session')
def user(pytestconfig) -> str:
    """ Get the user argument """
    return pytestconfig.getoption('--user')


@pytest.fixture(scope='session')
def password(pytestconfig) -> str:
    """ Get the password argument """
    return pytestconfig.getoption('--password')


@pytest.fixture(scope='session')
def performance_logging(pytestconfig) -> bool:
    """ Get the performance_logging argument """
    return pytestconfig.getoption('--performance_logging')


@pytest.fixture(scope='session')
def virtual(pytestconfig) -> bool:
    """ Get the virtual argument """
    return pytestconfig.getoption('--virtual')


@pytest.fixture(scope='session')
def temp_path():
    """ Get the temporary path fixture """
    temp_path = tempfile.gettempdir() if sys.platform != 'win32' else r'C:\Temp'
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

    yield temp_path


@pytest.fixture(scope='session')
def authentication(host: str, user: str, port: int, password: str):
    """ Obtain the authentication fixture """
    try:
        ip = [str(i[4][0]) for i in socket.getaddrinfo(host, port)][0]
    except Exception:
        ip = host
    label = f'{user}:token'
    token = keyring.get_password(ip, label)
    token_encode = token.encode() if token else None

    # Returning a tuple for all authentication purposes
    yield token_encode, keyring.get_password(ip, user), user, password


@pytest.fixture(scope='session')
def omni(temp_path: str):
    """ Fixture for building the omniscript object for the test session """
    inst = omniscript.OmniScript(
        level=2, flags=omniscript.OMNI_FLAG_NO_HTTPS_WARNINGS)

    inst.set_log_file(os.path.join(temp_path, 'Pytest-Log.log'), 'w')
    inst.info('PyTest Begin')

    yield inst


@pytest.fixture(scope='session', autouse=True)
def engine(omni, host: str, port: int, secure: bool,
           performance_logging: bool, temp_path: str, authentication):
    """ Fixture for buidling engine from omni object """
    inst = omni.create_engine(host, port, secure)

    # Login code
    if not inst:
        error_message = 'Failed Login. No engine. Abort all tests!'
        omni.error(error_message)
        pytest.exit(error_message)

    if performance_logging:
        inst.start_performance_logging(os.path.join(
            temp_path, 'Pytest-Performance.log'), 'w')

    login_successful = False
    token, keyring_password, user, password = authentication

    try:
        if inst.login(user, password, token):
            new_token = inst.get_session_token()
            if new_token != token:
                set_token(host, user, new_token, port)
                login_successful = True
    except Exception:
        pass

    if not password:
        password = keyring_password
    try:
        if inst.login(user, password):
            new_token = inst.get_session_token()
            set_token(host, user, new_token, port)
            login_successful = True
    except Exception:
        pass

    if login_successful:
        yield inst
    else:
        error_message = (f'Failed Login on {host}:{port}. Incomplete or failed engine login '
                         f'for: {user}. Check credentials. Abort all tests!')
        omni.error(error_message)
        pytest.exit(error_message)

    if performance_logging:
        inst.stop_performance_logging()

    inst.disconnect()
    if inst.is_connected():
        omni.error('*** Failed to disconnect from engine.')

    omni.info('PyTest: Done')
