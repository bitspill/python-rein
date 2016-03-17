from sqlalchemy import Column, Integer, String, Boolean, and_
from sqlalchemy.ext.declarative import declarative_base
import requests
import requesocks
import hashlib

Base = declarative_base()


class Placement(Base):
    __tablename__ = 'placement'

    id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, nullable=False)
    url = Column(String(250), nullable=False)
    remote_key = Column(String(64), nullable=False)
    verified = Column(Integer, nullable=False)
    testnet = Column(Boolean, nullable=False)

    def __init__(self, doc_id, url, remote_key, verified=0, testnet=True):
        self.doc_id = doc_id
        self.url = url
        self.remote_key = remote_key
        self.verified = verified
        self.testnet = testnet

    def set_verified(self):
        self.verified = 1

    def clear_verified(self):
        self.verified = 0

    @staticmethod
    def get_placements(rein, url, doc_id):
        return rein.session.query(Placement).filter(and_(Placement.url == url,
                                                         Placement.doc_id == doc_id,
                                                         Placement.testnet == rein.testnet)).all()

    @staticmethod
    def get_remote_document_hash(rein, plc):
        sel_url = "{0}get?key={1}"
        answer = rein.requester.get(url=sel_url.format(plc.url, plc.remote_key))
        if answer.status_code == 404:
            rein.log.error("%s not found at %s" % (str(plc.doc_id), plc.url))
            return False
        else:
            text = answer.json()['value']
            text = text.decode('ascii')
            text = text.encode('utf8')
            return hashlib.sha256(text).hexdigest()

    @staticmethod
    def create_placements(engine):
        Base.metadata.create_all(engine)
