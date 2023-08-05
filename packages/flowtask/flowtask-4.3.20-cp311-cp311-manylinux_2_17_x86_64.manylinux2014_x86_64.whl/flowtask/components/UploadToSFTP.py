import asyncio
from collections.abc import Callable
import logging
import asyncssh

from flowtask.exceptions import ComponentError
from .UploadTo import UploadToBase
from .SSHClient import SSHClient


asyncssh.set_debug_level(1)
asyncssh.set_log_level(logging.INFO)
logging.basicConfig(level='INFO')

class UploadToSFTP(SSHClient, UploadToBase):
    """
        uploadToSFTP.

        Upload a file (or collection of files) to a SSH/SFTP Server.
    """

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop = None,
            job: Callable = None,
            stat: Callable = None,
            **kwargs
    ):
        self.mdate = None
        self.local_name = None
        self.filename: str = ''
        self.whole_dir: bool = False
        self.preserve = True
        self.block_size: int = 65356
        self.max_requests: int = 1
        UploadToBase.__init__(
            self,
            loop=loop,
            job=job,
            stat=stat,
            **kwargs
        )
        tunnel = {}
        if hasattr(self, 'tunnel'):
            tunnel = self.tunnel
            del self._params['tunnel']
        # removing unnecesary elements on params:
        params = self._params.copy()
        SSHClient.__init__(
            self,
            tunnel=tunnel,
            **params
        )

    def start(self):
        """start Method."""
        super(UploadToSFTP, self).start()
        if hasattr(self, 'source'):
            self.whole_dir = self.source['whole_dir'] if 'whole_dir' in self.source else False
        try:
            if self.previous and self.input:
                self.filename = self.input
            elif self.file:
                self.filename = self.process_pattern('file')
        except (NameError, KeyError):
            pass
        return self

    def upload_progress(self, srcpath, dstpath, bytes_copied, total_bytes):
        #self._filenames[dstpath.decode('utf-8')] = srcpath.decode('utf-8')
        self._pb.reset(total=total_bytes)
        self._pb.update(bytes_copied)
        self._pb.refresh()

    async def run(self):
        """Running Download file."""
        self._result = None
        status = False
        try:
            await self.open(
                host=self.host,
                port=self.port,
                tunnel=self.tunnel,
                credentials=self.credentials
            )
        except asyncio.CancelledError:
            logging.info(f'{self.host} CANCELED~')
            # break
        except (asyncio.TimeoutError, ComponentError) as err:
            raise ComponentError from err
        except Exception as err:
            raise ComponentError from err
        async with self._connection.start_sftp_client() as sftp:
            # check all versions of functionalities
            args = {
                "block_size": self.block_size,
                "max_requests": self.max_requests,
                "progress_handler": self.upload_progress,
                "error_handler": self.err_handler
            }
            if self.whole_dir is True:
                logging.debug(f'Uploading all files on directory {self.source_dir}')
                file = "{}/*".format(self.source_dir)
                p = self.source_dir.glob('**/*')
                self.filename = [x for x in p if x.is_file()]
            else:
                file = self.filename
            args['remotepath'] = self.directory
            if hasattr(self, 'source'):
                args['recurse'] = True if 'recursive' in self.source else False
            self.start_progress(total=len(file))
            try:
                status = await sftp.mput(
                        file,
                        **args
                    )
                self.close_progress()
            except (OSError) as err:
                logging.error(f'Upload SFTP local error: {err}')
                return False
            except (asyncssh.sftp.SFTPError) as err:
                logging.error(f'SFTP UploadTo Server error: {err}')
                return False
            except (asyncssh.Error) as err:
                logging.error(
                    f'Upload 2 SFTP: connection failed: {err}'
                )
            except Exception as err:
                logging.exception(err)
                raise
        if status is False:
            return False
        else:
            self.add_metric('SFTP_FILES', self.filename)
            self._result = self.filename
            return self._result
