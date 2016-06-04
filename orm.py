from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func


Base = declarative_base()

class Doctor(Base):
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True)
    co_colegiado = Column(Integer)
    no_nombre = Column(String)
    no_apellido1 = Column(String)
    no_apellido2 = Column(String)
    no_email = Column(String)
    nu_telefono = Column(String)
    co_provincia_cole = Column(String)
    no_provincia_cole = Column(String)
    no_especialidad_list = Column(String)
    fl_estado = Column(Integer)
    fl_publico = Column(Integer)
    fl_privado = Column(Integer)
    ca_puntos = Column(String)
    no_modi_usr = Column(String)
    no_crea_usr = Column(String)
    dt_modi_reg = Column(DateTime)
    dt_creat_reg = Column(DateTime)
    fl_off_reg = Column(Integer)


class Dataset(object):
    def __init__(self, infos):
        self.user = infos['user']
        self.pwd = infos['pass']
        self.ip = infos['ip']
        self.schema = infos['schema']
        self.eng = self._create_eng()
        Base.metadata.bind = self.eng
        Base.metadata.create_all()
        Session = sessionmaker(bind=self.eng)
        self.ses = Session()

    def insert(self, dr):
        ses = None
        try:
            ses = self._create_session()
            ses.add(dr)
        except Exception as err:
            raise Exception(err)
        finally:
            if ses:
                ses.commit()
                ses.close()

    def _create_eng(self):
        return create_engine('mysql://{}:{}@{}/{}'.format(
                self.user, self.pwd, self.ip, self.schema
        ))

    def _create_session(self):
        return sessionmaker(bind=self.eng)()

    def get_last_nb_col(self, prov):
        ses = None
        max_value = int(str(prov).zfill(2)*2 + '9'*5)
        min_value = int(str(prov).zfill(2)*2 + '0'*5)
        try:
            ses = self._create_session()
            qry = ses.query(func.max(Doctor.co_colegiado))\
                .filter(Doctor.co_colegiado < max_value)\
                .filter(Doctor.co_colegiado >= min_value)
            co_colegiado = qry.one()[0]
        except Exception as err:
            raise Exception(err)
        finally:
            if ses:
                ses.close()
        return co_colegiado

