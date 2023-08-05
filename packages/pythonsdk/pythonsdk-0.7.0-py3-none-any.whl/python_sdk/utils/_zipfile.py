import os
import zipfile


class ZipFileWithPermissions(zipfile.ZipFile):
    """
    ZipFile by default strips away executable bits from binaries it extracts as it uses shutil.copyfileobj, which
    writes the output without any execute bits.
    This class fixes that behaviour.
    https://stackoverflow.com/questions/39296101/python-zipfile-removes-execute-permissions-from-binaries
    """

    def _extract_member(self, member: zipfile.ZipInfo | str, targetpath: str, pwd: bytes) -> str:
        if not isinstance(member, zipfile.ZipInfo):
            member = self.getinfo(member)
        path: str = super()._extract_member(member, targetpath, pwd)  # type: ignore

        if member.external_attr > 0xFFFF:
            os.chmod(path, member.external_attr >> 16)
        return path
