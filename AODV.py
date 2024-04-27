

from interfaces.IRoutingStrategy import IRoutingStrategy
from networkDevice.INetworkDevice import INetworkDevice
from networkDevice.deviceTimer import DeviceTimer
from util.Property import Property
from util.pack_bytes import pack_bytes
from dataclasses import dataclass
from enum import Enum

class PacketType(Enum):
    DATA = 0
    RREQ = 1
    RREP = 2
    RERR = 3

@dataclass
class RREQ:
    sender_id: int
    originator_id: int
    destination_id: int
    uid: int
    hop_count: int
    originator_seq_number:int
    destination_seq_number:int

    def get_data(self):
        return [PacketType.RREQ.value,
        self.sender_id,
        self.originator_id,
        self.destination_id,
        self.uid,
        self.hop_count,
        self.originator_seq_number,
        self.destination_seq_number]

@dataclass
class RREP:
    sender_id: int
    originator_id: int
    destination_id: int
    hop_count: int
    destination_seq_number:int

    def get_data(self):
        return [PacketType.RREP.value,
        self.sender_id,
        self.originator_id,
        self.destination_id,
        self.hop_count,
        self.destination_seq_number]

@dataclass
class AODVRoute:
    next_hop:int
    hop_count:int
    status:int
    destination_seq_number:int

class AODVProtocol(IRoutingStrategy):
    
    

    def __init__(self,device: INetworkDevice):
        self.id= device.get_property('id',0)

        self.device = device
        self.logger = device.get_logger()

        self.master = device.get_property('master',False)
        self.dest_id = device.get_property('dest_id',0)
        if self.master:
            self.device.add_property("dest_id",Property(self,"dest_id",int))
        self.modem = device.get_modems()[0]
        

        self.device.add_property("id",Property(self,"id",int))
       
        self.device.add_property("master",Property(self,"master",bool))
        self.modem.set_rx_done_callback(self.received)
        self.routes = {}
        self.packet_uid=0

    def get_uid(self):
        self.packet_uid+=1
        return self.packet_uid

    def start(self):
        if self.master:
            route = self.routes.get(self.dest_id,None)
            if route is None:
                self.send_rreq(self.dest_id)
           

    def send_rreq(self,dest):
        pkt = RREQ(self.id,self.id,dest,self.get_uid(),0,0,0)
        self.modem.send(pkt.get_data())

    def process_received(self,data):
        if data[0] == PacketType.RREQ.value:
            self.process_rreq(RREQ(data[1],data[2],data[3],data[4],data[5],data[6],data[7]))
        elif data[0] == PacketType.RREP.value: 
            self.process_rrep(RREP(data[1],data[2],data[3],data[4],data[5]))

    def update_route(self,dest, seq_num, next_hop, hop_count):
        current = self.routes.get(dest,None)

        if current is None or (current is not None and (seq_num > current.destination_seq_number or current.status == 0 or next_hop == dest)):
            route = AODVRoute(next_hop,hop_count,1,seq_num)
            #self.logger.log(route,self.device)
            self.routes[dest] = route

    def process_rreq(self,pkt):
        if  pkt.originator_id != self.id:
            self.logger.log(pkt,self.device)
            self.update_route(pkt.originator_id,pkt.originator_seq_number, pkt.sender_id, pkt.hop_count)
            self.update_route(pkt.sender_id,pkt.originator_seq_number, pkt.sender_id, 0)
            self.logger.log(self.routes,self.device)
            if pkt.destination_id == self.id: # запрос к нам
                resp = RREP(self.id,self.id,pkt.originator_id,0,0)
                self.logger.log(f"received RREQ from {pkt.originator_id}",self.device)
                self.modem.send(resp.get_data())
            else: # запрос не к нам
                # проверяем есть ли у нас амршрут
                route = self.routes.get(pkt.destination_id,None)
                if route is not None and route.status == 1:
                    # есть маршрут, отправляем ответ
                    self.logger.log("received RREQ, route found, sending RREP",self.device)
                    resp = RREP(self.id,self.id,pkt.originator_id,route.hop_count,route.destination_seq_number)
                    self.modem.send(resp.get_data())
                else:
                    # нет маршрут, отправляем дальше
                    self.logger.log("received RREQ, no route found, forwarding",self.device)
                    pkt = RREQ(self.id,pkt.originator_id,pkt.destination_id,pkt.uid,pkt.hop_count+1,pkt.originator_seq_number,pkt.destination_seq_number)
                    self.modem.send(pkt.get_data())

    def process_rrep(self,pkt):
        if pkt.originator_id != self.id:
            self.logger.log(pkt,self.device)
            self.update_route(pkt.originator_id,pkt.destination_seq_number, pkt.sender_id, pkt.hop_count)
            self.update_route(pkt.sender_id,pkt.destination_seq_number, pkt.sender_id, 0)
            # ответ к нам
            if pkt.destination_id == self.id:
                self.logger.log(f"received RREP from {pkt.originator_id}",self.device)
                self.logger.log(self.routes,self.device)
            else:
                self.logger.log("forwarding RREP",self.device)
                pkt.hop_count+=1
                pkt.sender_id = self.id
                self.modem.send(pkt.get_data())

    def received(self,data):
        #self.logger.log(data,self.device)
        self.process_received(data[0][0])
