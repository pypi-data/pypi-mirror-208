from sqlalchemy import DateTime, String, ForeignKey, Column
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from typing import Tuple, List
import json
from ssb_altinn3_util.models.altinn3_cloud_event import Altinn3CloudEvent

from ssb_altinn3_util.database.altinn_mottak_db_adapter import AltinnMottakDbAdapter


class AltinnEvent(AltinnMottakDbAdapter.Base):
    __tablename__ = "altinn_event"

    db_id = Column("id", String(length=36), primary_key=True, index=True)
    id = Column("event_id", String, unique=True, index=True)
    time = Column(DateTime)
    source = Column(String)
    type = Column(String)
    subject = Column(String)
    alternativesubject = Column(String)
    data = Column(String)
    specversion = Column(String)
    datacontenttype = Column(String)

    process = relationship("AltinnEventProcess", uselist=False)
    event_data = relationship("AltinnEventData", uselist=False)

    @hybrid_property
    def ids_from_source(self) -> Tuple[str, int, str]:
        """Extracts app_id, instance_owner_id and instance_guid from source field"""
        if not self.source:
            return "", 0, ""

        ids = self.source.split(sep="/")
        if len(ids) < 4:
            return "", 0, ""

        return ids[-4], int(ids[-2]), ids[-1]

    def __init__(
        self,
        alternativesubject,
        data,
        datacontenttype,
        id,
        source,
        specversion,
        subject,
        time,
        type,
    ):
        self.alternativesubject = alternativesubject
        self.datacontenttype = datacontenttype
        self.id = id
        self.source = source
        self.specversion = specversion
        self.subject = subject
        self.time = time
        self.type = type
        self.data = data


class AltinnEventProcess(AltinnMottakDbAdapter.Base):
    __tablename__ = "altinn_event_process"

    id = Column("id", String(length=36), primary_key=True, index=True)
    event_id = Column(
        String(length=36), ForeignKey("altinn_event.id"), unique=True, index=True
    )
    received_at = Column(DateTime)
    data_fetched_at = Column(DateTime)
    confirmed_altinn_at = Column(DateTime)
    confirmed_ssb_at = Column(DateTime)
    shared_at = Column(DateTime)
    deadlettered = Column(DateTime)


class AltinnEventData(AltinnMottakDbAdapter.Base):
    __tablename__ = "altinn_event_data"

    id = Column("id", String(length=36), primary_key=True, index=True)
    event_id = Column(
        String(length=36), ForeignKey("altinn_event.id"), unique=True, index=True
    )
    instance = Column(String)
    data_base_url = Column(String)

    def __init__(self, event_id: str, instance: str, data_base_url: str):
        self.event_id = event_id
        self.instance = instance
        self.data_base_url = data_base_url

    @hybrid_property
    def data_ids(self) -> List[str]:
        ids: List[str] = []

        instance_json = json.loads(self.instance)
        if "data" not in instance_json:
            return ids

        for element in instance_json["data"]:
            ids.append(element["id"])

        return ids
