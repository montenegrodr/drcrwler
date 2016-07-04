from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, asc
from sqlalchemy.orm.session import make_transient


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
    dt_last_check = Column(DateTime)


class Dataset(object):
    def __init__(self, infos):
        self.user = infos['user']
        self.pwd = infos['pass']
        self.ip = infos['ip']
        self.schema = infos['schema']
        self.eng = self._create_eng()
        Base.metadata.bind = self.eng
        Base.metadata.create_all()

    def insert(self, dr):
        ses = None
        try:
            ses = self._create_session()
            ses.add(dr)
            ses.commit()
        except Exception as err:
            raise Exception(err)
        finally:
            if ses:
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

    def next_dr_check(self):
        ses = None
        try:
            ses = self._create_session()
            qry = ses.query(Doctor) \
                .filter(Doctor.co_colegiado == '010100895')
            # qry = ses.query(Doctor) \
            #     .filter(Doctor.fl_estado == 1) \
            #     .order_by(asc(Doctor.dt_last_check)) \
            #     .order_by(asc(Doctor.co_colegiado))
            dr = qry.first()
        except Exception as err:
            raise Exception(err)
        finally:
            if ses:
                ses.close()
        return dr

    def update(self, dr):
        ses = None
        try:
            ses = self._create_session()
            ses.merge(dr)
            ses.commit()
        except Exception as err:
            raise Exception(err)
        finally:
            if ses:
                ses.close()

    def insert_transient(self, dr, new_co_colegiado, date):
        ses = None
        try:
            ses = self._create_session()
            dr = ses.query(Doctor) \
                .filter(Doctor.id == dr.id).first()
            ses.expunge(dr)
            make_transient(dr)
            dr.dt_modi_reg = None
            dr.no_modi_usr = None
            dr.id = None
            dr.fl_estado = 1
            dr.co_colegiado = new_co_colegiado
            dr.dt_creat_reg = date
            dr.dt_last_check = date
            ses.add(dr)
            ses.commit()
        except Exception as err:
            raise Exception(err)
        finally:
            if ses:
                ses.close()