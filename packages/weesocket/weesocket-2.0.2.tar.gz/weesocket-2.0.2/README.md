# weesocket
Python socket library


## About
This library is intended to be used as simple wrapper for working with python low level sockets.


## Installing weesocket

```sh
# install weesocket library
$ pip install weesocket

# dev version for development:
$ pip install weesocket[dev] # install developer requirements
```


## Using
Use following objects as parents for your custom processing objects.<br> `Server` and `Client` objects inherits `threading.Thread` module and works in thread mode.


### Server socket wrapper
<b>Initialize parameters:</b>
- `id` - server identification name (type: str | default value: `server`)
- `socket_file` - unix socket file (type: str | default value: <i>empty string</i>)
- `host` - host ip (type: str | default value: <i>empty string</i>)
- `port` - host port (type: int | default value: `0`)
- `buffer_size` - buffer size for message receiver (type: int | default value: `4096`)
- `proxy` - specifying whether server can be used as proxy to send messages between clients (type: bool | default value: `True`)
- `secret` - secret to prove server identity (type: bytearray | default value: <i>empty bytearray</i>)
- `remotes` - list of client secrets to check their identities - (type: list of bytearrays | default value: <i>empty list</i>)
- `encrypt` - specifying whether encryption will be enabled (type: bool | default value: `True`)
- `rsa_length` - rsa key length - not used if keys given in parameters (type: int | default value: `2048`)
- `public_key` - private key string -generated if not given (type: str | default value: <i>empty string</i>)
- `private_key` - private key string - generated if not given (type: str | default value: <i>empty string</i>)
- `daemon` - variable specyfing if thread is daemonized (type: bool | default value: `True`)
- `logger` - python logger object (or `None` to disable logging) (type: logger | default value: `None`)

<i>Note: one of type parameters `socket_file` or `host` and `port` must be given, if both are given unix socket file is preferred.<br>Remotes are not used if not given.</i>

<b>Methods:</b>
- `send` - disconnect from server (<i>data</i>:`dict`, <i>target</i>:`str`)
- `disconnect` - disconnect client from server (<i>client_id</i>: `str`)
- `stop` - stop server listening ()

<i>Note: `target` parameter is optional, empty target is processed by server, `*` is intended to be used for broadcast to all other clients.</i>

<b>Properties:</b>
- `id` - id of connection | type: `str`
- `enabled` - status of connection | type: `bool`

### Client socket wrapper
<b>Initialize parameters:</b>
- `id` - server identification name (type: str | default value: `server`)
- `socket_file` - unix socket file to connect (type: str | default value: <i>empty string</i>)
- `host` - server host ip to connect (type: str | default value: <i>empty string</i>)
- `port` - server host port to connect (type: int | default value: `0`)
- `buffer_size` - buffer size for message receiver (type: int | default value: `4096`)
- `secret` - secret code to prove identity (type: bytearray | default value: <i>empty bytearray</i>)
- `remote_secret` - secret code to check server identity (type: list of strings | default value: <i>empty list</i>)
- `encrypt` - specifying whether encryption will be enabled (type: bool | default value: `True`)
- `rsa_length` - rsa key length - not used if keys given in parameters (type: int | default value: `2048`)
- `public_key` - private key string -generated if not given (type: str | default value: <i>empty string</i>)
- `private_key` - private key string - generated if not given (type: str | default value: <i>empty string</i>)
- `daemon` - variable specyfing if thread is daemonized (type: bool | default value: `True`)
- `logger` - python logger object (or `None` to disable logging) (type: logger | default value: `None`)

<i>Note: one of type parameters `socket_file` or `host` and `port` must be given, if both are given unix socket file is preferred.<br>Remotes are not used if not given.</i>


<b>Methods:</b>
- `send` - disconnect from server (<i>data</i>:`dict`, <i>target</i>:`str`)
- `disconnect` - disconnect from server ()

<i>Note: `target` parameter is optional, empty target is processed by server, `*` is intended to be used for broadcast to all other clients and `**` is intended to be used for broadcast to all other clients and process by server.</i>

<b>Properties:</b>
- `id` - id of connection | type: `str`
- `enabled` - status of connection | type: `bool`


### Example
Simple examples of server and client socket wrappers.

<b>Server example:</b>
```py
from weesocket import ServerWrapper


class ServerWrapper(Server):
	def _trigger(self, payload, sender):
		print("sender:", sender)
		print("payload:", payload)


server = ServerWrapper(socket_file="/tmp/socket_file.sock")
```

<b>Client example:</b>
```py
from weesocket import client


class ClientWrapper(Client):
	def _trigger(self, payload, sender):
		print("sender:", sender)
		print("payload:", payload)


client = ClientWrapper(socket_file="/tmp/socket_file.sock")
```

More examples in [tests folder](https://gitlab.com/katry/weesocket/-/blob/master/tests/test_all.py).
