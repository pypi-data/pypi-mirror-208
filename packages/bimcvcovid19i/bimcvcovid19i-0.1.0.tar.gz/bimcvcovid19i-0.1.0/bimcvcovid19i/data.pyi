import typing as tp
from .typing import DatasetRoot, Labels, Series, Session, Subject, Test
from pathlib import Path

class BIMCVCOVID19Root(DatasetRoot):
    @property
    def prepared_series(self) -> Path: ...
    @property
    def prepared_sessions(self) -> Path: ...
    @property
    def prepared_subjects(self) -> Path: ...

class BIMCVCOVID19Data(BIMCVCOVID19Root):
    webdav_hostname: str
    webdav_login: str
    webdav_password: str
    subjects_tarfile_name: str
    subjects_tarfile_subpath: str
    sessions_tarfile_name: str
    tests_tarfile_name: str
    tests_tarfile_subpath: str
    labels_tarfile_name: str
    labels_tarfile_subpath: str
    def download(self): ...
    def sessions_iter(self) -> tp.Iterator[Path]: ...
    def series_iter(self) -> tp.Iterator[Series]: ...
    def subjects(self) -> tp.List[Subject]: ...
    def sessions(self) -> tp.List[Session]: ...
    def tests(self) -> tp.Dict[str, tp.List[Test]]: ...
    def labels(self) -> tp.Dict[str, Labels]: ...
    def prepare(self) -> None: ...

class BIMCVCOVID19positiveData_12(BIMCVCOVID19Data):
    webdav_hostname: str
    webdav_login: str
    webdav_password: str
    subjects_tarfile_name: str
    subjects_tarfile_subpath: str
    sessions_tarfile_name: str
    tests_tarfile_name: str
    tests_tarfile_subpath: str
    labels_tarfile_name: str
    labels_tarfile_subpath: str

class BIMCVCOVID19positiveData_123(BIMCVCOVID19Data):
    webdav_hostname: str
    webdav_login: str
    webdav_password: str
    subjects_tarfile_name: str
    subjects_tarfile_subpath: str
    sessions_tarfile_name: str
    tests_tarfile_name: str
    tests_tarfile_subpath: str
    labels_tarfile_name: str
    labels_tarfile_subpath: str

class BIMCVCOVID19negativeData_12(BIMCVCOVID19Data):
    webdav_hostname: str
    webdav_login: str
    webdav_password: str
    subjects_tarfile_name: str
    subjects_tarfile_subpath: str
    sessions_tarfile_name: str
    labels_tarfile_name: str
    labels_tarfile_subpath: str
    def tests(self) -> tp.Dict[str, tp.List[Test]]: ...
