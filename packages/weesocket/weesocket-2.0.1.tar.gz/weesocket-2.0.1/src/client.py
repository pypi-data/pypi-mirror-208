from rsa import PublicKey
from .abstract import SocketAbstract
from socket import (
	socket,
	AF_UNIX, AF_INET,
	SOCK_STREAM, SHUT_RDWR
)


class Client(SocketAbstract):
	def __init__(
		self, socket_file: str = "", host: str = "", port: int = 0,
		encrypt: bool = True, secret: bytes = b"", remote_secret: bytes = b"",
		buffer_size: int = 4096, public_key="", private_key="",
		rsa_length: int = 2048, daemon: bool = True, logger=None
	):
		if not socket_file and (not host or port < 1 or port > 65535):
			raise OSError("Invalid connection settings")
		self._socket = socket()
		self._id = None
		self._file = socket_file
		self._host = host
		self._port = port
		self._buffer_size = buffer_size
		self._remote_secret = remote_secret
		self._open = False
		self._queue = []
		super().__init__(
			encrypt=encrypt, secret=secret, logger=logger,
			public_key=public_key, private_key=private_key,
			rsa_length=rsa_length, daemon=daemon
		)

	def run(self):
		if self._file:
			self._socket = socket(AF_UNIX, SOCK_STREAM)
			self._socket.connect(self._file)
		else:
			self._socket = socket(AF_INET, SOCK_STREAM)
			self._socket.connect((self._host, self._port))
		self._socket.settimeout(2)
		self._listen()

	def send(self, data: dict, target=""):
		if self._open:
			self._send(data, target)
		else:
			self._queue.append((data, target))

	def disconnect(self):
		if self.enabled:
			self._socket.shutdown(SHUT_RDWR)
			self._socket.close()
			self._open = False

	def _listen(self):
		data = None
		bytes = b""
		while self.enabled:
			try:
				bytes += self._socket.recv(self._buffer_size)
			except Exception:
				continue
			if not bytes:
				break
			data, overload = self._check(bytes)
			try:
				parsed = self._load(data, self._remote_secret)
			except Exception as e:
				self._log("ParseError: invalid network data\n%s" % str(e), level=30)
				parsed = {}
			if "payload" in parsed:
				self._trigger(parsed["payload"], parsed.get("sender"))
			elif "client_id" in parsed:
				self._id = parsed["client_id"]
				key = parsed.get("key")
				if key:
					self._remote_key = PublicKey.load_pkcs1(key)
				self._socket.sendall(self._dump({
					"secret": self.secret.decode(),
					"key": self._public_key,
					"sender": self._id
				}))
				if not self._remote_secret:
					self._ready()
			elif not self._open and "secret" in parsed:
				if parsed["secret"].encode() == self._remote_secret:
					self._ready()
			bytes = overload
		self.disconnect()

	def _send(self, data: dict, target: str):
		self._socket.sendall(self._dump({
			"payload": data,
			"target": target,
			"sender": self._id
		}))

	def _ready(self):
		while len(self._queue):
			self._send(*self._queue.pop(0))
		self._open = True

	@property
	def id(self):
		return self._id

	@property
	def enabled(self):
		return not self._socket._closed
