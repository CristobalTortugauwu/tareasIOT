import socket
from dataclasses import dataclass
import struct
from datetime import datetime
import threading
from modelosv3 import *

id_device = 1

def int_to_mac(int_val: int):
    hex_str = '{:012x}'.format(int_val)
    mac = ":".join(hex_str[i:i+2] for i in range(0, 12, 2))
    return mac



@dataclass
class Headers:
    idx: int
    devmac: int
    tpl: bool
    idp: int
    length: int

    def __str__(self) -> str:
        return f"Headers:\n\tID_MSG: {self.idx},\n\tMAC: {int_to_mac(self.devmac)}\n\ttp_layer: {self.tpl}\n\tPROTOCOL: {self.idp}\n\tSIZE: {self.length}"


@dataclass
class Proto0:
    batt: int
    #TODO prio -1: hacer sl print

@dataclass
class Proto1:
    batt: int
    timestamp: int #que sea timestamp

@dataclass
class Proto2:
    batt: int
    timestamp: int
    temp: int
    press: int
    hum: int
    co: int

@dataclass
class Proto3:
    batt: int
    timestamp: int
    temp: int
    press: int
    hum: int
    co: int
    rms: int
    ampx: int
    frecx: int
    ampy: int
    frecy: int
    ampz: int
    frecz: int

@dataclass
class Proto4:
    batt: int
    timestamp: int
    temp: int
    press: int
    hum: int
    co: int
    accx :list[float]
    accy :list[float]
    accz :list[float]
    rgyrx :list[float]
    rgyry :list[float]
    rgyrz :list[float]

def parse_headers(data: bytes) -> Headers:
    idx = (data[1] << 8) | data[0]
    devmac = (data[7] << 40) | (data[6] << 32) | (data[5] << 24) | (data[4] << 16) | (data[3] << 8) | data[2]
    #devmac = (data[2] << 40) | (data[3] << 32) | (data[4] << 24) | (data[5] << 16) | (data[6] << 8) | data[7]
    tpl = data[8]
    idp = data[9]
    length = data[11] << 8 | data[10]
    return Headers(idx, devmac, tpl, idp, length)


HOST = '192.168.4.1'  # Escucha en esa ip en particular
PORT = 8888           # Puerto en el que se escucha
BUFFSIZE = {0:13, 1:17, 2:27, 3:55, 4:48027}

def data_formatted(data, idp, id_device):
    if idp == 0:
        bat, = struct.unpack("<b", data)
        datos = Proto0(bat)
        print(f"[INFO - {id_device}] ",datos)
        return datos
    elif idp == 1:
        bat, tstamp = struct.unpack("<bI", data)
        datos = Proto1(bat,tstamp)
        print(f"[INFO - {id_device}] ",datos)
        return datos
    elif idp == 2:
        bat, tstamp, temp, press, hum, co= struct.unpack("<bIbIbf", data)
        datos = Proto2(bat,tstamp,temp,press,hum,co)
        print(f"[INFO - {id_device}] ",datos)
        return datos
    elif idp == 3:
        bat, tstamp, temp, press, hum, co, rms, ampx, frecx, ampy, frecy, ampz, frecz = struct.unpack("<bIbIbffffffff", data)
        datos =  Proto3(bat, tstamp, temp, press, hum, co, rms, ampx, frecx, ampy, frecy, ampz, frecz)
        print(f"[INFO - {id_device}] ",datos)
        return datos
    elif idp == 4:
        bat, tstamp, temp, press, hum, co, accx, accy, accz, rgyrx, rgyry, rgyrz = struct.unpack(f"<bIbIbf{2000}f{2000}f{2000}f{2000}f{2000}f{2000}f",data)
        print(bat, tstamp, temp, press, hum, co, accx, accy, accz, rgyrx, rgyry, rgyrz)
        return Proto4(bat, tstamp, temp, press, hum, co, accx, accy, accz, rgyrx, rgyry, rgyrz)
    else:
        print(f"No hay para ese idp! {idp}")


def sendinfo(sockettcp,socketudp,curr_tp_id,data,address):
    if curr_tp_id == 0:
        #enviar con TCP
        sockettcp.send(data)
    elif curr_tp_id == 1 and address != None:
        #enviar con UDP
        socketudp.sendto(data, address)


def recvinfo(sockettcp,socketudp,buff_size,curr_tp_id):
    address = None
    if curr_tp_id == 0:
        data = sockettcp.recv(buff_size)
    elif curr_tp_id == 1:
        data, address = socketudp.recvfrom(buff_size)
    return data, address

def write_data_to_db(data,headers,id_device):
    #la query depende del tipo de protocolo
    proto = headers.idp
    mac = headers.devmac
    batt = data.batt
    id_msg = headers.idx
    if proto == 0:
        datos = Datos.create(batt_level=batt,MAC=mac,id_device=id_device,id_mensaje=id_msg)
        print(f"[INFO - {id_device}]Escribiendo a la base de datos\t{data}")
    elif proto==1:
        timestamp = data.timestamp
        datos = Datos.create(batt_level=batt,MAC=mac,id_device=id_device,timestamp=timestamp,id_mensaje=id_msg)
        print(f"[INFO - {id_device}]Escribiendo a la base de datos\t{data}")
    elif proto==2:
        timestamp = data.timestamp
        temp= data.temp
        press= data.press
        hum= data.hum
        co= data.co
        datos = Datos.create(MAC= mac, id_device= id_device, id_mensaje= id_msg,
                             temp= temp, press= press, hum= hum, co= co, timestamp=timestamp)
        print(f"[INFO - {id_device}]Escribiendo a la base de datos\t{data}")
    elif proto==3:
        timestamp = data.timestamp
        temp= data.temp
        press= data.press
        hum= data.hum
        co= data.co
        rms= data.rms
        ampx= data.ampx
        frecx= data.frecx
        ampy= data.ampy
        frecy= data.frecy
        ampz= data.ampz
        frecz= data.frecz
        datos= Datos.create(MAC= mac, id_device= id_device, id_mensaje= id_msg, timestamp=timestamp,
                            temp= temp, press= press, hum= hum, co= co, rms= rms,
                            ampx= ampx, frecx= frecx, ampy= ampy, frecy= frecy,
                            ampz= ampz, frecz= frecz)
        print(f"[INFO - {id_device}]Escribiendo a la base de datos\t{data}")
    elif proto==4:
        timestamp = data.timestamp
        temp=data.temp
        press=data.press
        hum = data.hum
        co = data.co
        accx = data.accx
        accy = data.accy
        accz = data.accz
        rgyrx = data.rgyrx
        rgyry = data.rgyry
        rgyrz = data.rgyrz
        datos = Datos.create(MAC=mac, id_device= id_device, id_mensaje=id_msg, timestamp=timestamp,
                            temp=temp, press= press, hum= hum, co= co, accx= accx, accy = accy,
                            accz = accz, rgyrx = rgyrx, rgyry= rgyry, rgyrz= rgyrz)
        print(f"[INFO - {id_device}]Escribiendo a la base de datos\t{data}")
    else:
        print(f"[INFO - {id_device}]¡este protocolo no existe!")
#Tampoco este
def initConf(proto,tl,id_device):
    db.create_tables(Configuracion)
    Configuracion.create(id_protocol=proto,Transport_Layer=tl)
    print(f"[INFO-{id_device}]\tSe ha inicializado correctamente la base de datos")

def get_protocol():
    rows = Configuracion.select()
    proto = 0
    for row in rows:
        proto=row.id_protocol
    return proto

def get_transport_layer():
    rows = Configuracion.select()
    tl = 0
    for row in rows:
        tl = row.transport_layer
    return tl


#no lo usen
def changeConf(proto,tl,id_device):
    newconf = Configuracion.select()
    newconf.save()
    print(f"[INFO-{id_device}]\tSe han modificado los datos de la configuración")

def handle_connection(conn: socket.socket, addr, id_device: int):
    conn_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address_udp = (HOST, PORT + 200 + id_device)
    conn_udp.bind(server_address_udp)
    print(f"[INFO - {id_device}]\tManejando conexión, el server udp es {server_address_udp}")
    _, puerto = server_address_udp
    with conn:
        #-- Secuencia de inicio
        curr_ip_proto = get_protocol()
        curr_tp_id = get_transport_layer()
        data = struct.pack("<bbI", curr_ip_proto, curr_tp_id, puerto)
        print(f"[INFO - {id_device}]\tEnviando secuencia de inicio IDP={curr_ip_proto}, TPID={curr_tp_id}")
        #sendinfo(conn, conn_udp, curr_tp_id, data,addr)
        conn.send(data)
        #-----------------------
        while True:
            print(f"[INFO - {id_device}]\tEsperando datos con el socket {'udp' if curr_tp_id == 1 else 'tcp'}")
            data, esp_addr = recvinfo(conn, conn_udp,BUFFSIZE[curr_ip_proto], curr_tp_id)
            #data = conn.recv(BUFFSIZE[curr_ip_proto])
            if data:
                headers = parse_headers(data[0:12])
                print(f"[INFO - {id_device}]\n\t{headers}")
                # LLego un request message! 
                if headers.idp == 20:
                    print(f"[INFO - {id_device}]  Me pidieron un req!")
                    old_tp_id = curr_tp_id
                    curr_tp_id = get_transport_layer()
                    curr_ip_proto = get_protocol()
                    data = struct.pack("<bb", curr_ip_proto, curr_tp_id)
                    sendinfo(conn, conn_udp, old_tp_id, data, esp_addr)
                    continue
                else:
                    data_prot= data_formatted(data[12:], headers.idp, id_device)
                    write_data_to_db(data_prot,headers,id_device)
                    print(f"[INFO - {id_device}]\n\t{data_prot}")
            
            #old_tp_id = curr_tp_id
            #curr_tp_id = get_transport_layer()
            #curr_ip_proto = get_protocol()
            #data = struct.pack("<bb", curr_ip_proto, curr_tp_id)
            #sendinfo(conn, conn_udp, old_tp_id, data, esp_addr)
            #conn.send(data)


def main():
    global id_device
    # Crea un socket para IPv4 y conexión TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        server_address = (HOST, PORT)
        s.bind(server_address)
        s.listen()
        print("El servidor está esperando conexiones en el puerto", PORT)
        while True:
            print("Esperando conexión...")
            conn, addr = s.accept()
            # Espera una conexión
            #udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #udp_socket.bind(server_address_udp)
            print("Conexión aceptada")
            x = threading.Thread(target=handle_connection, args=(conn, addr, id_device,))
            x.start()
            id_device += 1

if __name__ == "__main__":
    main()