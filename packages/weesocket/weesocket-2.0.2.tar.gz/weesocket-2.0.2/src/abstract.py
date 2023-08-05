from threading import Thread
from base64 import b64encode, b64decode
from orjson import loads, dumps
from hashlib import sha256
from hmac import new
from rsa import PrivateKey, newkeys, encrypt, decrypt


class SocketAbstract(Thread):
	def __init__(
		self, encrypt: bool = False, secret: bytes = b"",
		public_key: str = "", private_key: str = "",
		rsa_length: int = 2048, daemon: bool = True, logger=None
	):
		super().__init__()
		self.daemon = daemon
		self.__encrypt = encrypt
		if encrypt:
			if public_key and private_key:
				self._public_key = public_key
				self._local_key = PrivateKey.load_pkcs1(private_key.encode())
			else:
				key = newkeys(rsa_length)
				self._public_key = key[0].save_pkcs1().decode()
				self._local_key = key[1]
		else:
			self._public_key = None
			self._local_key = None
		self.__secret = secret
		self.__logger = logger
		super().start()

	@staticmethod
	def _check(raw: bytes):
		parts = raw.split(b"|")
		try:
			length = int(parts[0])
		except Exception:
			return b"", b""
		offset = len(parts[0]) + 1
		actual = raw[offset:offset + length]
		if len(actual) == length:
			return actual, raw[offset + length:]
		else:
			return b"", raw

	def _load(self, raw: bytes, remote_secret: bytes = b""):
		if not raw:
			return {}
		parts = raw.split(b"|")
		if remote_secret:
			if len(parts) < 2 or parts[1] != self._sign(parts[0], remote_secret):
				raise IOError("Network message: invalid signature")
		if self.__encrypt and self._local_key:
			try:
				payload = self._decrypt(parts[0], self._local_key)
			except Exception:
				payload = b64decode(parts[0])
		else:
			payload = b64decode(parts[0])
		payload = loads(payload)
		return payload

	def _dump(self, data: dict, remote_key=None):
		payload = dumps(data)
		if self.__encrypt and remote_key:
			payload = self._encrypt(payload, remote_key)
		else:
			payload = b64encode(payload)
		if self.__secret:
			signature = self._sign(payload, self.__secret)
			raw = b"%d|%s|%s" % (
				len(payload) + len(signature) + 1,
				payload,
				signature
			)
		else:
			raw = b"%d|%s" % (len(payload), payload)
		return raw

	@staticmethod
	def _encrypt(data: bytes, public_key, chunk_size: int = 245) -> bytes:
		chunks = []
		seek = 0
		while data[seek:seek + chunk_size]:
			chunks.append(
				b64encode(encrypt(data[seek:seek + chunk_size], public_key)).decode()
			)
			seek += chunk_size
		return dumps(chunks)

	@staticmethod
	def _decrypt(encrypted: bytes, private_key) -> bytes:
		chunks: list = loads(encrypted)
		buffer = b""
		for d in chunks:
			buffer += decrypt(b64decode(d.encode()), private_key)
		return buffer

	@staticmethod
	def _sign(data: bytes, secret: bytes):
		return new(secret, data, sha256).hexdigest().encode()

	def _log(self, msg, *args, level=20, **kwargs):
		if self.__logger:
			self.__logger.log(level, msg, *args, **kwargs)

	def _trigger(self, payload, sender):
		raise NotImplementedError("Trigger not implemented!")

	@property
	def is_encrypted(self):
		return self.__encrypt

	@property
	def secret(self):
		return self.__secret
