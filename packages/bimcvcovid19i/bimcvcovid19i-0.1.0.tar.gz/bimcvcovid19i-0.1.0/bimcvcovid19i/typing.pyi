import numpy as np
import typing as tp
from _typeshed import Incomplete
from pathlib import Path

LikePath: Incomplete

class DatasetRoot:
    def __init__(self, root: tp.Optional[LikePath] = ..., original: tp.Optional[LikePath] = ..., prepared: tp.Optional[LikePath] = ...) -> None: ...
    @property
    def original(self) -> Path: ...
    @property
    def prepared(self) -> Path: ...

class Test:
    subject_id: str
    date: str
    test: str
    result: str
    def to_dict(self): ...
    def __init__(self, subject_id, date, test, result) -> None: ...

class Subject:
    uid: str
    age: tp.Optional[float]
    gender: tp.Optional[str]
    tests: tp.Optional[tp.List[Test]]
    sessions_ids: tp.Set[str]
    series_ids: tp.Set[str]
    series_modalities: tp.Set[str]
    def save(self, root: LikePath): ...
    def __init__(self, uid, age, gender, tests, sessions_ids, series_ids, series_modalities) -> None: ...

class Labels:
    subject_id: str
    session_id: str
    report: str
    labels: tp.List[str]
    localizations: tp.List[str]
    labels_localizations_by_sentence: tp.List[str]
    label_CUIS: tp.List[str]
    localizations_CUIS: tp.List[str]
    def to_dict(self): ...
    def __init__(self, subject_id, session_id, report, labels, localizations, labels_localizations_by_sentence, label_CUIS, localizations_CUIS) -> None: ...

class Session:
    uid: str
    subject_id: str
    study_date: tp.Optional[str]
    medical_evaluation: tp.Optional[str]
    series_modalities: tp.Set[str]
    series_ids: tp.Set[str]
    labels: tp.Optional[Labels]
    def save(self, root: LikePath): ...
    @classmethod
    def load(cls, root: LikePath): ...
    def __init__(self, uid, subject_id, study_date, medical_evaluation, series_modalities, series_ids, labels) -> None: ...

class Series:
    uid: str
    image: tp.Optional[np.ndarray]
    spacing: tp.Optional[tp.Tuple[float, ...]]
    tags: tp.Optional[tp.Dict]
    subject_id: str
    session_id: str
    modality: str
    def save(self, root: LikePath): ...
    @classmethod
    def load(cls, root: LikePath) -> Series: ...
    def __init__(self, uid, image, spacing, tags, subject_id, session_id, modality) -> None: ...

class EmptyFileError(RuntimeError): ...

class SeriesRawPath:
    uid: str
    image_path: tp.Optional[Path]
    tags_path: tp.Optional[Path]
    def read_item(self) -> Series: ...
    def __init__(self, uid, image_path, tags_path) -> None: ...
