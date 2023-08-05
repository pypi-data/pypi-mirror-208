import sqlalchemy as db, os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from deskaone_sdk_scrypt_2023.Exceptions import Error

def declarative():
    return declarative_base()

class Database:
    
    class Connection:
        
        def __init__(self, DATABASE_NAME: str, Base) -> None:
            if os.path.exists('Database') is False:
                os.mkdir('Database')
            __engine      = create_engine(f'sqlite:///Database/{DATABASE_NAME}.db', echo=False)        
            __metadata    = MetaData()
            __engine.connect()
            try:Base.metadata.create_all(__engine)
            except Error as e:pass
            self.Engine      = __engine
            self.Metadata    = __metadata