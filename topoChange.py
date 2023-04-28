#from couchdb import Server
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch, DefaultController
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from multiprocessing import Process
import time
from mininet.topo import Topo
from mininet.link import TCLink

class TutorialTopologyAdvanced(Topo):

    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
       
        # Add left switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
       
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s1, s4)

        self.addLink(s2, s3)
        self.addLink(s2, s4)
        
        self.addLink(s3, s4)
        
       
        # self.addLink(s4, s5)
        # self.addLink(s4, s5)
        # self.addLink(s4, s5)
        # self.addLink(s4, s5)
        # self.addLink(s4, s5)
        # self.addLink(s4, s5)
        # self.addLink(s4, s5)

    
        self.addLink(s1, h1, cls=TCLink, bw=1000, delay='10ms')
        self.addLink(s2, h2, cls=TCLink, bw=1000, delay='10ms')
        self.addLink(s3, h3, cls=TCLink, bw=1000, delay='10ms')
        self.addLink(s4, h4, cls=TCLink, bw=1000, delay='10ms')
        

# the topologies accessible to the mn tool's `--topo` flag
# note: if using the Dockerfile, this must be the same as in the Dockerfile
topos = {
    'tutorialTopologyAdvanced': (lambda: TutorialTopologyAdvanced())
}

   
# remove this part if mininet is to be used on console only.
# the command line entry point
    
if __name__ == "__main__":
        topology = TutorialTopologyAdvanced() # Everytime for a new topology.
        controller_ip = "127.0.0.1"  # localhost
        controller_port = 6653
        
        print(" The Topology is Established Successfully !")

        net = Mininet(topo=topology, controller=None, host=CPULimitedHost, link=TCLink, switch=OVSSwitch, autoSetMacs=True)
        net.addController('c1', controller=RemoteController, ip=controller_ip, port=controller_port)
        net.start()
        # net.pingAll()

        # net.pingAll()
        if 18>16 : 
            # time.sleep(1)
            #net link down
            net.configLinkStatus('s1', 's4', 'down')
            # # time.sleep(1)
            net.configLinkStatus('s1', 's3', 'down')
            # # time.sleep(1)
            net.configLinkStatus('s2', 's4', 'down')
            # # time.sleep(1)
            
            CLI(net)
             











