from peewee import Model, PostgresqlDatabase, ForeignKeyField, TimestampField, DecimalField, FloatField, SmallIntegerField, BigIntegerField, BlobField, PrimaryKeyField
#Para usar arrays
from playhouse.postgres_ext import *

# Configuración de la base de datos
db = PostgresqlDatabase('iotdb', host='localhost', port=5432, user='postgres', password='wena4321')

# Definición de un modelo
class BaseModel(Model):
    class Meta:
        database = db

class Datos(BaseModel):
    batt_level = DecimalField(null=True)
    timestamp = TimestampField(utc=True,null=False)
    temp = DecimalField(null=True) #5-30
    press = DecimalField(null=True) #1000-1200
    hum = DecimalField(null=True) #30-80
    co = FloatField(null=True) #30-200
    ampx = FloatField(null=True)
    ampy = FloatField(null=True)
    ampz = FloatField(null=True)
    frecx = FloatField(null=True)
    frecy = FloatField(null=True)
    frecz = FloatField(null=True)
    rms = FloatField(null=True)
    accx = ArrayField(FloatField, dimensions=8000,null=True)
    accy =  ArrayField(FloatField, dimensions=8000,null=True)
    accz =  ArrayField(FloatField, dimensions=8000,null=True)
    rgyrx =  ArrayField(FloatField, dimensions=8000,null=True)
    rgyry =  ArrayField(FloatField, dimensions=8000,null=True)
    rgyrz =  ArrayField(FloatField, dimensions=8000,null=True)
    MAC = BigIntegerField(null=True)
    id_device = BigIntegerField(null=True)
    id_mensaje = BigIntegerField(null=True)

class Configuracion(BaseModel):
    id_protocol = IntegerField()
    transport_layer = IntegerField()

class Logs(BaseModel):
    id_device = BigIntegerField() #no toi del todo seguro
    llave_foranea_hacia_conf = ForeignKeyField( Configuracion, backref="ID_protocol")
    timestamp = TimestampField(utc=True)

class Loss(BaseModel):
    dif_timestamp = TimestampField(utc=True)
    packet_loss = BlobField()


def create_tables():
    db.connect()
    db.create_tables([Loss,Logs,Configuracion,Datos])
    db.close()
    return

if __name__ == '__main__':
    create_tables(