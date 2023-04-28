from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
import requests

class BandwidthMonitor(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(BandwidthMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == ofp_event.EventOFPPortStateChange:
            self.datapaths[datapath.id] = datapath

    def _monitor(self):
        while True:
            for datapath in self.datapaths.values():
                self._request_stats(datapath)
            hub.sleep(1)

    def _request_stats(self, datapath):
        url = 'http://127.0.0.1:8080/stats/port/%s' % datapath.id
        response = requests.get(url)
        if response.status_code == 200:
            for stat in response.json():
                if stat['port_no'] == 1:  # change to the port you want to monitor
                    rx_bytes = stat['rx_bytes']
                    tx_bytes = stat['tx_bytes']
                    bandwidth = (rx_bytes + tx_bytes) * 8 / 1000000  # in Mbps
                    print('Link bandwidth: %.2f Mbps' % bandwidth)
