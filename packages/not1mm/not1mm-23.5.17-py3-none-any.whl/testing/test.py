"""doc"""

from xmlrpc.client import ServerProxy

with ServerProxy("http://127.0.0.1:8000") as proxy:
    response = proxy.system.listMethods()
    print(f"list methods: {response}")
    proxy.setspeed(10)
