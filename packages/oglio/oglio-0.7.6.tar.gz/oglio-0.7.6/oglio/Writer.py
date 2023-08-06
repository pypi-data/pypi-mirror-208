
from logging import Logger
from logging import getLogger

from zlib import compress
from zlib import ZLIB_VERSION

from oglio.Types import OglProject

from oglio.toXmlV10.OglToDom import OglToDom as OglToMiniDomV10


class Writer:
    """
    A shim on top of the OGL serialization layer;  Allows me to one day replace
    the heavy-duty Python core xml minidom implementation
    Or even replace XML with JSON
    """

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

    def writeFile(self, oglProject: OglProject, fqFileName: str):
        """
        Writes to a compressed Pyut file

        Args:
            oglProject:     The project we have to serialize
            fqFileName:     Where to write the XML;  Should be a full qualified file name

        """
        if fqFileName.endswith('.put') is False:
            fqFileName = f'{fqFileName}.put'

        oglToMiniDom: OglToMiniDomV10 = OglToMiniDomV10(projectVersion=oglProject.version, projectCodePath=oglProject.codePath)

        for oglDocument in oglProject.oglDocuments.values():
            oglToMiniDom.serialize(oglDocument=oglDocument)

        rawXml: str = oglToMiniDom.xml

        self.logger.info(f'{ZLIB_VERSION=}')
        byteText:        bytes  = rawXml.encode()
        compressedBytes: bytes = compress(byteText)

        with open(fqFileName, "wb") as binaryIO:
            binaryIO.write(compressedBytes)

    def writeXmlFile(self, oglProject: OglProject, fqFileName: str):
        """
        Writes to an XML file
        Args:
            oglProject:     The project we have to serialize
            fqFileName:     Where to write the XML;  Should be a full qualified file name
        """
        if fqFileName.endswith('.xml') is False:
            fqFileName = f'{fqFileName}.xml'

        oglToMiniDom: OglToMiniDomV10 = OglToMiniDomV10(projectVersion=oglProject.version, projectCodePath=oglProject.codePath)

        for oglDocument in oglProject.oglDocuments.values():
            oglToMiniDom.serialize(oglDocument=oglDocument)

        oglToMiniDom.writeXml(fqFileName=fqFileName)

