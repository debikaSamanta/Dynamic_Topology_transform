# from couchdb import Server
# localhost:5984/_utils/
# docker-compose stop
# sudo netstat -lpn |grep :5984
# sudo kill -9 2058
## Launch Topology
>python3 topoChange.py       
>
## visualise Topology
>ryu-manager --observe-links ryu.app.gui_topology.gui_topology

## run remote controller
>ryu-manager controller.py

## update python
>sudo update-alternatives --config python3

>sudo mn --custom ./topology.py --topo=test --controller remote --switch ovsk,protocols=OpenFlow13

## python dependencies
>pip install matplotlib
>pip install Pillow

key stored in drive
