# Copyright (C) 2016 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import requests
from operator import attrgetter
from ryu.controller import handler
from ryu.controller import event
from ryu.base import app_manager

from ryu.topology import event, switches, api
from ryu.ofproto import ofproto_v1_0, ofproto_v1_3


from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

temp_list = []
url = "http://127.0.0.1:5000/"
add_update = {'Source': "s1", 'Destination': "s3", 'update_type': "add"}

delete_update = {'Source': "s3", 'Destination': "s4", 'update_type': "delete"}

class SimpleMonitor13(simple_switch_13.SimpleSwitch13):
    
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                # self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                # self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)

    def _request_stats(self, datapath):
        # self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
        if len(body) == 1:
            print("No flow entry found",ev.msg.datapath.id)
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            dpid = ev.msg.datapath.id
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             dpid,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)
            if stat.byte_count > 346780:
                if dpid in temp_list:

                    temp_list.sort()
                    if (temp_list[0] != temp_list[-1]) and (len(temp_list) > 2):
                        print(" The congession happened ",temp_list[0],temp_list[-1])

                        TopologyUpdate_req = requests.get(url, params=add_update)
                        if TopologyUpdate_req.status_code == 200:
                            print('Request successful')
                            # print(TopologyUpdate_req.content)
                        else:
                            print('Request failed with status code: ' + str(TopologyUpdate_req.status_code))    
                        temp_list.clear()
                else:
                    temp_list.append(dpid)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)

class TopologyUpdater(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(TopologyUpdater, self).__init__(*args, **kwargs)
        self.topo_api = api.get_topology(self)

    @set_ev_cls(event.EventLinkAdd)
    def link_add_handler(self, ev):
        self.topo_api.refresh()   

    @set_ev_cls(event.EventLinkDelete)
    def link_add_handler(self, ev):
        self.topo_api.refresh()      

    @set_ev_cls(event.EventLinkBase)
    def link_add_handler(self, ev):
        self.topo_api.refresh()     
          

