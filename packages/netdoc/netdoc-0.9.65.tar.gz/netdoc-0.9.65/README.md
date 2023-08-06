# NetDoc

NetDoc is an automatic network documentation plugin for NetBox. NetDoc aims to discover a partially known network populating netbox and drawing L2 and L3 diagrams.

NetDoc:

* Discovers, via nornir+netmiko, network devices fetching information (routing, adjacencies, configuration...).
* Populate netbox (devices, cables, IPAM).

Network diagrams are currently provided by netbox-topology-views plugin. See [my blog post](https://www.adainese.it/blog/2022/08/28/netdoc-automated-network-discovery-and-documentation/ "NetDoc: automated network discovery and documentation") for more information.

## Assumptions

Correlate data from different sources requires some assumptions:

* Device names are assumed unique and uppercase. Hostnames are not updated by NetDoc.
* Interface labels are used to correlate interfaces from different sources/output (e.g. `show interfaces`, `show cdp neighbors`...). Labels are built from interface name or shortname using the `short_interface_name` function.
* Interface level VRFs have a local scope. Prefix and IP address level VRFs are used to globally track VRF. Because discovery scripts are not aware about global VRF, they set interface level VRF only. Discovery scripts do not modify IP address level VRF if IP address is already set. Users must manually update IP address and prefix level VRFs.
* Netbox don't have network objects. To draw L3 diagrams, NetDoc uses prefixes and IP addresses. Because there is no hard association between prefixes and IP addresses, mind that IP addresses are part of a specific prefix if they both have the same VRF.
* IP addresses of discoverable devices must be unique. They are used to correlate outputs and discoverables.
* A method to get the hostname of discoverable devices exists. This hostname is used to create Netbox devices associated to discoverables.
* Templates are used to parse hostnames and to select the right ingestor. If Netmiko can understand that "show ip arp" and "show ip arp vrf red" need the same template, ingestors must be aware of the specific VRF that can be found in the command line.
* L2 neighbors (LLDP/CDP) are used to guess L1 cabling. Interfaces with multiple netibhors are silently skipped.

## Installing netbox

You should follow the offical documentation, but just in case here is how I install netbox:

~~~
sudo apt install -y apache2 python3 python3-pip python3-venv python3-dev build-essential libxml2-dev libxslt1-dev libffi-dev libpq-dev libssl-dev zlib1g-dev postgresql redis
sudo useradd -M -U -d /opt/netbox netbox
sudo git clone -b v3.4.4 https://github.com/netbox-community/netbox /opt/netbox
sudo chown netbox:netbox /opt/netbox/ -R
~~~

## Installing NetDoc prerequisites

~~~
sudo git clone --depth=1 https://github.com/networktocode/ntc-templates /opt/ntc-templates
sudo chown netbox:netbox /opt/ntc-templates -R
~~~

NetDoc must be included in netbox plugins and configured in the main netbox configuration file (see below).

## Creating the netbox database

~~~
sudo -u postgres psql
create database netbox;
create user netbox with password '0123456789abcdef';
grant all privileges on database netbox to netbox;
~~~

## Configuring netbox

You should follow offical documentation, but just in case here is how I configure netbox:

~~~
sudo -u netbox cp -a /opt/netbox/netbox/netbox/configuration_example.py /opt/netbox/netbox/netbox/configuration.py
sudo -u netbox cp /opt/netbox/contrib/gunicorn.py /opt/netbox/gunicorn.py
sudo -u netbox chmod 600 /opt/netbox/netbox/netbox/configuration.py
sudo openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/netbox.key -nodes -out /etc/ssl/certs/netbox.crt -sha256 -days 3650
sudo cp /opt/netbox/contrib/apache.conf /etc/apache2/sites-available/001-netbox.conf
sudo a2enmod proxy ssl headers proxy_http
sudo a2dissite 000-default
sudo a2ensite 001-netbox
sudo find /opt/netbox/netbox/static/ -type f -exec chmod a+r {} \;
sudo find /opt/netbox/ -type d -exec chmod a+xr {} \;
~~~

Edit the configuration file (`configuration.py`) as following:

~~~
ALLOWED_HOSTS = ['*']
DEVELOPER = False # True for developers
DATABASE = {
    'NAME': 'netbox',
    'USER': 'netbox',
    'PASSWORD': '0123456789abcdef',
    'HOST': 'localhost',
    'PORT': '',
    'CONN_MAX_AGE': 300,
}
REDIS = {
    'tasks': {
        'HOST': 'localhost',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 0,
        'SSL': False,
    },
    'caching': {
        'HOST': 'localhost',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 1,
        'SSL': False,
    }
}
PLUGINS = ['netdoc']
PLUGINS_CONFIG = {
    'netdoc': {
        'NTC_TEMPLATES_DIR': '/opt/ntc-templates/ntc_templates/templates',
        'NORNIR_LOG': '/tmp/nornir.log',
        'NORNIR_TIMEOUT': 300,
        'NORNIR_SKIP_LIST': [
            r'show ver',
            r'.* bgp .*',
        ],
        "RAISE_ON_CDP_FAIL": True,
        "RAISE_ON_LLDP_FAIL": True,
    },
}
RQ_DEFAULT_TIMEOUT = 600
SECRET_KEY = '01234567890123456789012345678901234567890123456789'
~~~

Upgrade and install dependencies for netbox:

~~~
sudo -u netbox echo netdoc >> /opt/netbox/local_requirements.txt
sudo -u netbox /opt/netbox/upgrade.sh
~~~

Create first administrative user:

~~~
sudo -u netbox /opt/netbox/venv/bin/python3 /opt/netbox/netbox/manage.py createsuperuser
~~~

## Starting netbox

Under `/opt/netbox/contrib/` you can find startup scripts for both netbox and scheduler (`netbox-rq`).

~~~
sudo cp -v /opt/netbox/contrib/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable netbox netbox-rq apache2
sudo systemctl start netbox netbox-rq apache2
~~~

Netbox is listening by default on localhost:8001 (see `/opt/netbox/contrib/gunicorn.py`). Apache is serving as a reverse proxy.

## Usint NetDoc on an existing netbox installation

NetDoc uses interface labels as a primary key for interfaces. Labels are populated with a interface shortname. The reason is simple: based on different outputs (especially on Cisco devices), interface name can be shortened. To correlate the interface name between many outputs, a shotname is created.

Moreover NetDoc uses uppercase Device names.

If you are using NetDoc on an existing netbox installation, you need to rename Devic names and generate interface labels (shortnames) for each interface in the database. You can do that with the provided scripts: go to Netbox Web UI -> Other -> Scripts -> NetDoc -> Fix Netbox data -> Run Script.

## Developing NetDoc

Install NetDoc as a development module:

~~~
mkdir ~/src
git clone https://github.com/dainok/netdoc ~/src/netdoc
~~~

Starting netbox:

~~~
cd ~/src/netdoc
/opt/netbox/venv/bin/python3 setup.py develop
/opt/netbox/venv/bin/python3 manage.py runserver 0.0.0.0:8000 --insecure
/opt/netbox/venv/bin/python3 manage.py rqworker high default low
~~~

### Testing

Install pre-commit:

~~~
pip install pre-commit
~~~

Test:

~~~
pre-commit run --all-files
~~~

Test Django scenario:

~~~
/opt/netbox/venv/bin/python3 /opt/netbox/netbox/manage.py test netdoc --keepdb
~~~

## Debugging

Discover script:

~~~
from netdoc import tasks

tasks.discovery(["172.25.82.34","172.25.82.39","172.25.82.40"])
~~~

NTC template:

~~~
import textfsm
import pprint

template_file = 'ntc_templates/templates/cisco_xr_show_ipv4_interface.textfsm'
raw_output_file = 'tests/cisco_xr/show_ipv4_interface/cisco_xr_show_ipv4_interface.raw'

with open(template_file) as fd_t, open(raw_output_file) as fd_o:
    re_table = textfsm.TextFSM(fd_t)
    parsed_header = re_table.header
    parsed_output = re_table.ParseText(fd_o.read())

pprint.pprint(parsed_header)
pprint.pprint(parsed_output)
~~~

Parsers:

~~~
from netdoc import models
import importlib
from netdoc import functions
import logging
import pprint

request = "show vrf"
mode = "netmiko_cisco_nxos"
request = "show ip interface"
mode = None

logs = models.DiscoveryLog.objects.all()

request = None # or "show vrf"
mode = None    # or "netmiko_cisco_nxos"

if mode:
    logs = logs.filter(discoverable__mode=mode)
if request:
    logs = logs.filter(request=request)
logs = logs.filter(success=True)

for log in logs:
    try:
        functions.log_parse(log)
    except:
        pass
	print('Command: ', log.command)
	print('ID: ', log.id)
    print('Address: ', log.discoverable.address)
	print('Device: ', log.discoverable.device)
    print('Parsed: ', log.parsed)
    print('Items: ', len(log.parsed_output))
    pprint.pprint(log.parsed_output)
    print('-' * 70)
~~~

Ingest scripts:

~~~
from netdoc import models
import importlib
from netdoc.ingestors import functions
import logging

request = None # or "show vrf"
mode = None    # or "netmiko_cisco_nxos"

logs = models.DiscoveryLog.objects.all()
if mode:
    logs = logs.filter(discoverable__mode=mode)
if request:
    logs = logs.filter(request=request)
logs = logs.filter(parsed=True)

for log in logs:
        try:
            functions.log_ingest(log)
        except functions.NoIngestor:
            pass
        except functions.Postponed as err:
            print(err)
~~~

## ToDo list

* Implement diff and approve model for discovered objects (use the JSON validators).
* Encrypt passwords and use select credentials in discovery script.
* Implement a deny list to skip commands.

## Known issues

* Renaming credentials blanks passwords.
* Cabling fails if neighbors are sending LLDP packets on subinterfaces (Check if the interface is physical).

## References

* [PostgreSQL Database Installation](https://docs.netbox.dev/en/stable/installation/1-postgresql/ "PostgreSQL Database Installation")
* [Redis Installation](https://docs.netbox.dev/en/stable/installation/2-redis/ "Redis Installation")
* [NetBox Installation](https://docs.netbox.dev/en/stable/installation/3-netbox/ "NetBox Installation")
* [Gunicorn](https://docs.netbox.dev/en/stable/installation/4-gunicorn/ "Gunicorn")
* [HTTP Server Setup](https://docs.netbox.dev/en/stable/installation/5-http-server/ "HTTP Server Setup")
