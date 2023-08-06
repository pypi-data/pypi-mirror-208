import io
from pathlib import Path
from lxml import etree
from flowtask.exceptions import (
    ComponentError,
    FileError
)
from .abstract import DtComponent


class OpenXML(DtComponent):
    """
    OpenXML.

    Open an XML file and returned as xml etree Object
    """

    filename = ''
    path:Path = None

    async def start(self, **kwargs):
        """
        start.

            Get if directory exists
        """
        if self.previous:
            if isinstance(self.input, dict):
                try:
                    filenames = list(self.input.keys())
                    if filenames:
                        self.filename = filenames[0]
                except (TypeError, IndexError) as exc:
                    raise FileError(
                        'File is empty or doesn\'t exists'
                    ) from exc
            else:
                self.data = self.input
        if hasattr(self, 'directory'):
            self.path = Path(self.directory).resolve()
            if not self.path.exists() or not self.path.is_dir():
                raise ComponentError(
                    f"Directory not found: {self.directory}",
                    status=404
                )
            # TODO: all logic for opening from File, pattern, etc
            if not self.filename:
                raise ComponentError(
                    "Filename empty",
                    code=404
                )

    async def close(self):
        """
        close.

            close method
        """
        pass

    async def run(self):
        """
        run.

            Open the XML file and return the object
        """
        root = None
        if hasattr(self, 'use_strings') and self.use_strings is True:
            fp = open(self.filename, 'r')
            self.data = fp.read()
            self.filename = None
        if self.filename:
            # open XML from File
            root = etree.parse(str(self.filename))
            if root:
                try:
                    if etree.iselement(root.getroot()):
                        self._result = root
                        return True
                except Exception as err:
                    print(err)
                    return False
            else:
                self._result = None
                return False
        elif self.data:
            if isinstance(self.data, str):
                # open XML from string
                xml = io.BytesIO(self.data.encode('utf-8'))
                parser = etree.XMLParser(recover=True, encoding='utf-8')
                #root = etree.fromstring(xml)
                #root = etree.fromstring(self.data, parser)
                root = etree.parse(xml, parser)
                try:
                    if etree.iselement(root.getroot()):
                        self._result = root
                except Exception as err:
                    print('Error on parsing XML Tree: ', err)
                    return False
            else:
                #TODO: check if data is already an XML element
                try:
                    print(etree.iselement(self.data.getroot()))
                except Exception as err:
                    raise ComponentError(
                        f'Invalid Object lxml, Error: {err}'
                    ) from err
                root = self.data
            self._result = root
            return True
        else:
            return False
