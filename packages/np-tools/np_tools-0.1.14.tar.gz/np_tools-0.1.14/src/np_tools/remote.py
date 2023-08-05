"""
Tools for running commands via ssh on remote hosts.
"""
from __future__ import annotations


import doctest
import subprocess
import sys
from typing import Any

import fabric
import np_config
import np_logging
from np_tools.config import ON_WINDOWS
from typing_extensions import Literal

logger = np_logging.get_logger(__name__)

HPC_CREDENTIALS: dict[Literal['user', 'password'], str] = np_config.fetch(
    '/logins'
)['svc_neuropix']

NP_COMPUTERS: dict[str, str]


def ssh(host: str) -> fabric.Connection:
    """Fabric connection to `host` using `svc_neuropix` creds.

    >>> with ssh('w10svad0139') as connection:
    ...     response = connection.run('echo "hello world"', hide=True)

    """
    return fabric.Connection(
        host=host,
        user=HPC_CREDENTIALS['user'],
        connect_kwargs=dict(password=HPC_CREDENTIALS['password']),
    )


hpc = ssh('hpc-login')
"""Fabric connection to `hpc-login` using `svc_neuropix` creds."""


def run_cmd_on_host(
    host: str,
    cmd: str,
    *,
    hide_output: bool = True,  # suppresses stdout
    warn: bool = True,  # suppresses bad exit code error
) -> Any:
    """Run `cmd` on `host` command-line via ssh.

    If `host` is 'localhost', run `cmd` locally in a subprocess.

    >>> print(run_cmd_on_host('w10svad0139', 'hostname').stdout.strip())
    W10SVAD0139
    >>> run_cmd_on_host('localhost', 'echo hello world').stdout.strip()
    b'hello world'
    >>> _ = run_cmd_on_host('localhost', 'echo hello world', hide_output=False)

    # prints 'hello world'
    """
    if host == 'localhost':
        logger.debug('Running command on localhost: %r', cmd)
        result = subprocess.run(
            cmd,
            shell=True,
            check=warn,
            capture_output=hide_output,
        )
        logger.debug('Return code: %s', result.returncode)
        return result

    with ssh(host) as connection:
        logger.debug(
            'Sending command to %s via fabric as %s: %r',
            connection.host,
            connection.user,
            cmd,
        )
        result = connection.run(cmd, hide=hide_output, warn=warn)
        logger.debug('Return code: %s', result.return_code)
    return result


def assert_cli_tool_on_host(host: str, executable: str) -> None:
    """Assert that `executable` exists and can be accessed on `host` via ssh.

    >>> if ON_WINDOWS: assert_cli_tool_on_host('localhost', "robocopy") == None
    True
    >>> if ON_WINDOWS: assert_cli_tool_on_host('w10svad0139', "robocopy") == None
    True

    >>> assert_cli_tool_on_host('localhost', "not-robocopy")
    Traceback (most recent call last):
    ...
    AssertionError
    >>> assert_cli_tool_on_host('w10svad0139', "not-robocopy")
    Traceback (most recent call last):
    ...
    AssertionError

    """
    if host == 'localhost':
        return assert_cli_tool_on_localhost(executable)

    cmd = f'{executable} /?'

    response = run_cmd_on_host(host, cmd, hide_output=True, warn=True)
    if response.return_code == 1:
        raise AssertionError(f'{cmd!r} failed on {host!r}.')


def assert_cli_tool_on_localhost(executable: str) -> None:
    """Assert that `executable` exists and can be accessed on local machine.

    >>> if ON_WINDOWS: assert_cli_tool_on_localhost("robocopy") == None
    True

    >>> assert_cli_tool_on_localhost("not-robocopy")
    Traceback (most recent call last):
    ...
    AssertionError

    """
    try:
        response = subprocess.run(
            [executable, '/?'],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        if not ON_WINDOWS and executable == 'robocopy':
            raise AssertionError(
                f'robocopy is only available on Windows: running on {sys.platform}'
            )
        raise AssertionError(f'{executable!r} could not be found in PATH.')
    else:
        if response.returncode != 16:
            raise AssertionError(
                f'{executable!r} returned exit status {response.returncode}.'
            )


if __name__ == '__main__':
    doctest.testmod(verbose=True, optionflags=doctest.IGNORE_EXCEPTION_DETAIL)
