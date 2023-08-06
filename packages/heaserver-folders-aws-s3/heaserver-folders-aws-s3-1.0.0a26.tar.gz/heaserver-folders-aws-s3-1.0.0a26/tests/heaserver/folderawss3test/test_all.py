from .folderawss3testcase import AWSS3FolderTestCase, AWSS3ItemTestCase
from heaserver.service.testcase.mixin import GetOneMixin, GetAllMixin, PostMixin, PutMixin, DeleteMixin


class TestGetAWSS3Folder(AWSS3FolderTestCase, GetOneMixin):  # type: ignore
    pass


class TestGetAllAWSS3Folders(AWSS3FolderTestCase, GetAllMixin):  # type: ignore
    pass


class TestPostAWSS3Folder(AWSS3FolderTestCase, PostMixin):  # type: ignore
    pass


class TestPutAWSS3Folder(AWSS3FolderTestCase, PutMixin):  # type: ignore
    pass


class TestDeleteAWSS3Folder(AWSS3FolderTestCase, DeleteMixin):  # type: ignore
    pass


class TestGetAWSS3Item(AWSS3ItemTestCase, GetOneMixin):  # type: ignore
    async def test_get_by_name(self) -> None:
        self.skipTest('folder items do not support get by name')

    async def test_get_by_name_invalid_name(self):
        self.skipTest('GET by name not supported for AWS S3 folder items')


class TestGetAllAWSS3Items(AWSS3ItemTestCase, GetAllMixin):  # type: ignore
    pass


class TestPostAWSS3Item(AWSS3ItemTestCase, PostMixin):  # type: ignore
    pass


class TestPutAWSS3Item(AWSS3ItemTestCase, PutMixin):  # type: ignore
    pass


class TestDeleteAWSS3Item(AWSS3ItemTestCase, DeleteMixin):  # type: ignore
    pass
