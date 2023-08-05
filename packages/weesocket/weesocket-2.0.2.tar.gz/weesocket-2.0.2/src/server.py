from os import path, remove
from socket import (
	socket,
	AF_UNIX, AF_INET, SOCK_STREAM,
	SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR
)
from threading import Thread
from typing import List
from rsa import PublicKey
from .abstract import SocketAbstract


class Server(SocketAbstract):
	def __init__(
		self, id="server", socket_file: str = "", host: str = "", port: int = 0,
		encrypt: bool = True, secret: bytes = b"", remotes: List[bytes] = [],
		proxy: bool = True, buffer_size: int = 4096, public_key="", private_key="",
		rsa_length: int = 2048, daemon: bool = True, logger=None
	):
		if not socket_file and (not host or port < 1 or port > 65535):
			raise OSError("Invalid server settings")
		self._id = id
		self._file = socket_file
		self._host = host
		self._port = port
		self._buffer_size = buffer_size
		self._remotes = remotes
		self._is_proxy = proxy

		self._enabled = False
		self._connections = {}
		self._counter = 0

		super().__init__(
			encrypt=encrypt, secret=secret, logger=logger,
			public_key=public_key, private_key=private_key,
			rsa_length=rsa_length, daemon=daemon
		)

	def run(self):
		self._enabled = True
		if self._file:
			self._socket = socket(AF_UNIX, SOCK_STREAM)
			try:
				if path.isfile(self._file):
					remove(self._file)
			except OSError:
				pass
			self._socket.bind(self._file)
		else:
			self._socket = socket(AF_INET, SOCK_STREAM)
			self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
			self._socket.bind((self._host, self._port))
		self._socket.settimeout(2)
		self._socket.listen(1)
		self._listen()

	def send(self, payload: dict, target: str = "*"):
		self._proxy({
			"payload": payload,
			"target": target,
			"sender": self._id
		})

	def stop(self):
		if not self._enabled:
			return
		for connection in self._connections.values():
			connection.close(False)
		self._connections = {}
		self._socket.close()
		if self._file:
			remove(self._file)
		self._enabled = False

	def disconnect(self, client_id):
		if client_id in self._connections:
			self._connections[client_id].close()
			self._connections.pop(client_id, None)

	def _listen(self):
		while self._enabled:
			try:
				conn, addr = self._socket.accept()
			except Exception:
				continue
			self._counter += 1
			client_id = "client_%d" % self._counter
			connection = Connection(self, client_id, conn, addr, self._buffer_size)
			self._connections[client_id] = connection

	def _proxy(self, parsed):
		target = parsed.pop("target")
		sender = parsed.get("sender")
		if target[0] == "*":
			for client_id, connection in self._connections.items():
				if client_id != sender:
					connection.send(parsed["payload"], sender)
			if target == "**" and "payload" in parsed and sender != self._id:
				self._trigger(parsed["payload"], sender)
		elif target in self._connections:
			self._connections[target].send(parsed["payload"], sender)

	@property
	def enabled(self):
		return self._enabled

	@property
	def id(self):
		return self._id


class Connection(Thread):
	def __init__(self, server, client_id, conn, addr, buffer_size):
		super().__init__()
		self._server = server
		self._conn = conn
		self._addr = addr
		self._open = False
		self._id = client_id
		self._buffer_size = buffer_size
		self._remote_secret = b""
		self._remote_key = None
		self._queue = []
		self.daemon = True
		super().start()

	def send(self, payload, sender):
		if self._open:
			self._send(payload, sender)
		else:
			self._queue.append((payload, sender))

	def _send(self, payload, sender):
		self._conn.sendall(self._server._dump({
			"payload": payload,
			"sender": sender
		}, remote_key=self._remote_key))

	def run(self):
		auth = {
			"client_id": self._id,
			"sender": self._server.id
		}
		if self._server.is_encrypted:
			auth["key"] = self._server._public_key
		self._conn.sendall(self._server._dump(auth))

		bytes = b""
		while self._server.enabled:
			try:
				bytes += self._conn.recv(self._buffer_size)
			except Exception:
				continue
			if not bytes:
				break
			data, overload = self._server._check(bytes)
			try:
				parsed = self._server._load(data, self._remote_secret)
			except Exception as e:
				self._server._log("ParseError: invalid network data\n%s" % str(e), level=30)
				parsed = {}

			if self._server._is_proxy and parsed.get("target", "") not in ("", self._server.id):
				self._server._proxy(parsed)
			elif "payload" in parsed:
				self._server._trigger(parsed["payload"], parsed.get("sender"))
			elif "secret" in parsed:
				self._auth(parsed)
			bytes = overload
		self.close()

	def close(self, disconnect_call=True):
		if self._open:
			self._open = False
			self._conn.shutdown(SHUT_RDWR)
			self._conn.close()
			if disconnect_call:
				self._server.disconnect(self._id)

	def _auth(self, parsed: dict):
		if self._server._remotes and parsed["secret"].encode() not in self._server._remotes:
			self._conn.shutdown(SHUT_RDWR)
			self._conn.close()
			return
		self._remote_secret = parsed["secret"].encode()
		key = parsed.get("key")
		if key:
			self._remote_key = PublicKey.load_pkcs1(key)
		self._conn.sendall(self._server._dump({
			"secret": self._server.secret.decode(),
			"sender": self._server.id,
			"key": self._server._public_key,
		}, remote_key=self._remote_key))
		while len(self._queue):
			self._send(*self._queue.pop(0))
		self._open = True
