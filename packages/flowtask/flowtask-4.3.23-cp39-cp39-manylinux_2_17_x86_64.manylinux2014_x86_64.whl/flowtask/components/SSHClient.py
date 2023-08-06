import os
import asyncio
from typing import Dict, List, Union
import logging
from datetime import datetime
from pathlib import Path, PurePath
import asyncssh
from flowtask.exceptions import ComponentError, FileNotFound, FileError

from .interfaces import ClientInterface

asyncssh.set_debug_level(1)
asyncssh.set_log_level(logging.INFO)
logging.basicConfig(level='INFO')

class SSHClient(ClientInterface):
    """
    SSHClient.

    Overview

            Basic SSH Client with connection, download and tunnel Support.

    .. table:: Properties
        :widths: auto


    +--------------+----------+-----------+-------------------------------------------------------+
    | Name         | Required | Summary                                                           |
    +--------------+----------+-----------+-------------------------------------------------------+
    | client_keys  |   Yes    | SSH public key                                                    |
    +--------------+----------+-----------+-------------------------------------------------------+
    | source       |   Yes    | List of algorithms to be used in connection encryption            |
    +--------------+----------+-----------+-------------------------------------------------------+
    | tunnel       |   Yes    | Describes an SSH tunnel connection                                |
    +--------------+----------+-----------+-------------------------------------------------------+




    Return the list of arbitrary days
    """
    block_size: int = 16384
    max_requests: int = 128
    algorithms = [
        'ssh-rsa',
        'ssh-dss',
        'sk-ssh-ed25519-cert-v01@openssh.com',
        'sk-ecdsa-sha2-nistp256-cert-v01@openssh.com',
        'ssh-ed25519-cert-v01@openssh.com',
        'ssh-ed448-cert-v01@openssh.com',
        'ecdsa-sha2-nistp521-cert-v01@openssh.com',
        'ecdsa-sha2-nistp384-cert-v01@openssh.com',
        'ecdsa-sha2-nistp256-cert-v01@openssh.com',
        'ecdsa-sha2-1.3.132.0.10-cert-v01@openssh.com',
        'ssh-rsa-cert-v01@openssh.com',
        'ssh-dss-cert-v01@openssh.com',
        'sk-ssh-ed25519@openssh.com',
        'sk-ecdsa-sha2-nistp256@openssh.com',
        'ssh-ed25519',
        'ssh-ed448',
        'ecdsa-sha2-nistp521',
        'ecdsa-sha2-nistp384',
        'ecdsa-sha2-nistp256',
        'ecdsa-sha2-1.3.132.0.10',
        'rsa-sha2-256',
        'rsa-sha2-512'
    ]

    def __init__(self, credentials: Dict, host: str, port: str, tunnel: Dict = None, **kwargs) -> None:
        self.commands: List = []
        self.only_sftp: bool = False
        if 'commands' in kwargs:
            self.commands = kwargs['commands']
            del kwargs['commands']
        self.tunnel: Dict = None
        if tunnel:
            self.tunnel = tunnel
        if 'max_requests' in kwargs:
            self.max_requests = kwargs['max_requests']
        if 'block_size' in kwargs:
            self.block_size = kwargs['block_size']
        super(SSHClient, self).__init__(credentials, host, port, **kwargs)

    async def close(self, timeout: int = 1, reason: str = 'Connection Ended.'):
        """Close Method."""
        try:
            if self._connection:
                await asyncio.wait_for(
                    self._connection.wait_closed(),
                    timeout=timeout
                )
        except (asyncio.TimeoutError, asyncio.CancelledError):
            self._connection.disconnect(
                code=asyncssh.DISC_BY_APPLICATION,
                reason=reason,
                lang='en-US'
            )
        except (OSError) as err:
            print(
                f'Error on SSH disconnection, reason: {err!s}'
            )
        except Exception as err:
            raise ComponentError(
                f"SSH Connection Error: {err}"
            ) from err

    async def open(self, host: str, port: int, credentials: Dict, **kwargs):
        """
            init an SSH connection
        """
        algorithms = self.algorithms
        if 'algorithms' in self._clientargs and len(self._clientargs['algorithms']) > 0:
            try:
                algorithms = algorithms.append(self._clientargs['algorithms'])
                del self._clientargs['algorithms']
            except KeyError:
                pass
        self._clientargs["server_host_key_algs"] = algorithms
        if 'client_keys' in self._clientargs:
            file = Path(self._clientargs['client_keys'])
            del self._clientargs['client_keys']
            if not file.exists() or not file.is_file():
                client_key = os.path.expanduser('~/.ssh/id_rsa')
            else:
                client_key = str(file)
            self._clientargs["client_keys"] = client_key

        if 'known_hosts' not in self._clientargs:
            if 'known_hosts' not in credentials:
                self._clientargs['known_hosts'] = None
        if self.tunnel:
            self._clientargs = {**self._clientargs, **self.tunnel['credentials']}
            if 'known_hosts' not in self._clientargs:
                self._clientargs["known_hosts"] = None
        try:
            if self.tunnel:
                tnl = await asyncssh.connect(
                    host=self.tunnel['host'],
                    port=int(self.tunnel['port']),
                    **self._clientargs
                )
                h = self.tunnel['host']
                result = await tnl.run(
                    f'echo "SSH tunnel connection to {h} successful"', check=False
                )
                print(result.stdout, end='')
                try:
                    del self._clientargs['username']
                    del self._clientargs['password']
                    del self._clientargs['known_hosts']
                except KeyError:
                    pass
                try:
                    del self._clientargs['locale']
                except KeyError:
                    pass
                self._connection = await tnl.connect_ssh(
                    host=host,
                    port=int(port),
                    **credentials,
                    **self._clientargs
                )
            else:
                try:
                    del self._clientargs['username']
                    del self._clientargs['password']
                    # del self._clientargs['known_hosts']
                except KeyError:
                    pass
                try:
                    del self._clientargs['locale']
                except KeyError:
                    pass
                self._connection = await asyncssh.connect(
                    host=host,
                    port=int(port),
                    **credentials,
                    **self._clientargs
                )
                try:
                    result = await self._connection.run(
                        f'echo "SSH connection to {host} successful"', check=False
                    )
                    print(result.stderr)
                    if result.stdout == 'This service allows sftp connections only.':
                        self.only_sftp = True
                    print('CONN:: ', result.stdout, end='')
                except Exception as e:
                    logging.error(e)
        except (OSError, asyncssh.Error, asyncssh.misc.PermissionDenied) as err:
            raise ComponentError(
                f"SSH connection failed: {err}"
            ) from err
        except ValueError as err:
            raise ComponentError from err
        except (Exception) as err:
            raise ComponentError(
                f'SSH connection failed: {err!s}'
            ) from err
        return True

    async def set_env(self, lang: str = 'en_US', collate:str = 'C', **kwargs):
        args = {
            "LANG": lang,
            'LC_COLLATE': collate,
            **kwargs
        }
        result = await self._connection.run('env', env=args)
        print(result.stdout, end='')


    async def run_command(self, command, check: bool = True, **kwargs):
        result = await self._connection.run(command, check=check, **kwargs)
        return result

    def err_handler(self, err, **kwargs):
        # TODO: add future handler of many kind of errors
        print(
            f'SSH Error: reason: {err}'
        )
        if isinstance(err, PermissionError):
            raise FileError(
                f"File Error: {err}"
            )
        if (hasattr(err, 'message') and 'No matches found' in err.message) or (hasattr(err, 'reason') and 'No matches found' in err.reason):
            raise FileNotFound(
                f"File Not Found: {err}"
            )
        return False

    async def sftp_client(self):
        """sftp_client.
         Starts a SFTP client connection.
        """
        return self._connection.start_sftp_client()

    def client_progress(self, srcpath, dstpath, bytes_copied, total_bytes):
        print(f'FILE PROCESSED: {srcpath}, {dstpath}')
        self._pb.reset(total=total_bytes)
        self._pb.update(bytes_copied)
        self._pb.refresh()

    async def download_files(
            self,
            file: Union[str,List[PurePath]],
            destination: Union[str, PurePath],
            preserve: bool = False,
            recurse: bool = False
        ):
        """download_file

        Download a File from sFTP based on Path.
        Args:
            path (str): file to be downloaded
        TODO: Support for write_into and Renaming Files.
        """
        try:
            self.start_progress(total=len(file))
            async with self._connection.start_sftp_client() as sftp:
                await sftp.mget(
                    file,
                    localpath=destination,
                    preserve=preserve,
                    recurse=recurse,
                    block_size=self.block_size,
                    max_requests=self.max_requests,
                    progress_handler=self.client_progress,
                    error_handler=self.err_handler
                )
            self.close_progress()
        except OSError as err:
            raise ComponentError(
                f"SSH: Error saving files in local: {err}"
            ) from err
        except asyncssh.sftp.SFTPError as err:
            raise ComponentError(
                f"SSH: Server Error: {err}"
            ) from err
        except Exception as err:
            logging.error(f'sFTP DOWNLOAD ERROR: {err}')

    async def upload_files(
            self,
            file: Union[str,List[PurePath]],
            destination: Union[str, PurePath],
            preserve: bool = False,
            recurse: bool = False
        ) -> bool:
        """upload_files.

        Use can upload one or more files (or directories) recursively.
        Args:
            file (Union[str,List[PurePath]]): Path (purepath) or list of
                paths for files or directories
            destination (Purepath or str): remote destination of upload
            preserve (bool, optional): preserve the original attributes. Defaults to False.
            recurse (bool, optional): copy recursively all directories. Defaults to False.
        Returns:
            bool: file(s) or directorires were uploaded or not.
        """
        try:
            self.start_progress(total=len(file))
            async with self._connection.start_sftp_client() as sftp:
                await sftp.mput(
                    file,
                    remotepath=destination,
                    preserve=preserve,
                    recurse=recurse,
                    block_size=self.block_size,
                    max_requests=self.max_requests,
                    progress_handler=self.client_progress,
                    error_handler=self.err_handler
                )
            self.close_progress()
        except OSError as err:
            raise ComponentError(
                f"SSH: Error reading local files: {err}"
            ) from err
        except asyncssh.sftp.SFTPError as err:
            raise ComponentError(
                f"SSH: Server Error: {err}"
            ) from err
        except Exception as err:
            logging.error(f'sFTP UPLOAD ERROR: {err}')


    async def copy_files(
            self,
            file: Union[str,List[PurePath]],
            destination: Union[str, PurePath],
            preserve: bool = False,
            recurse: bool = False
        ) -> bool:
        """copy_files.

        Use can copy/move one or more files (or directories) in server.
        Args:
            file (Union[str,List[PurePath]]): Path (purepath) or list of
                paths for files or directories
            destination (Purepath or str): remote destination of upload
            preserve (bool, optional): preserve the original attributes. Defaults to False.
            recurse (bool, optional): copy recursively all directories. Defaults to False.
        Returns:
            bool: file(s) or directorires were uploaded or not.
        """
        try:
            self.start_progress(total=len(file))
            async with self._connection.start_sftp_client() as sftp:
                await sftp.mcopy(
                    file,
                    dstpath=destination,
                    preserve=preserve,
                    recurse=recurse,
                    block_size=self.block_size,
                    max_requests=self.max_requests,
                    progress_handler=self.client_progress,
                    error_handler=self.err_handler
                )
            self.close_progress()
        except Exception as err:
            logging.error(f'sFTP DOWNLOAD ERROR: {err}')

    async def get_mtime_files(self, sftp, filename: str, mod_date: str) -> List:
        filelist = []
        for file in (await sftp.glob(filename)):
            mstat = (await sftp.getmtime(file))
            mdate = datetime.fromtimestamp(mstat).strftime('%Y-%m-%d')
            if mdate == mod_date:
                filelist.append(file)
        return filelist
