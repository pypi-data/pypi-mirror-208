class HC128:
    def __init__(self, key: bytes, iv: bytes):
        if len(key) != 16:
            raise ValueError("Key size must be 16 bytes")
        if len(iv) != 16:
            raise ValueError("IV size must be 16 bytes")

        self.key = key
        self.iv = iv

        self.w = [0] * 1024
        self.p = [0] * 512
        self.q = [0] * 512
        self.s = [0] * 512

        self.idx_i, self.idx_j = 0, 0

        self._initialize()

    def set_iv(self, iv: bytes):
        self.iv = iv + b'\x00' * (16 - len(iv))
        self._initialize()

    def _initialize(self):
        self.idx_i, self.idx_j = 0, 0

        for i in range(16):
            self.w[i] = int.from_bytes(self.key[4*i:4*(i+1)], 'big')
        for i in range(16, 256):
            self.w[i] = self.rotate_left(
                self.sigma1(self.w[i-2])
                + self.w[i-7]
                + self.sigma0(self.w[i-15])
                + self.w[i-16], 32
            )
        for i in range(256, 1024):
            self.w[i] = self.rotate_left(
                self.gamma1(self.w[i-2])
                + self.w[i-7]
                + self.gamma0(self.w[i-15])
                + self.w[i-16], 32
            )

        for i in range(0, 256):
            self.p[i] = self.w[i+256]
            self.q[i] = self.w[i+256+256]

        for i in range(512):
            self.s[i] = (
                self.p[(i-3) % 256]
                + self.q[(i-3) % 256]
                + self.s[i-12]
                + self.s[i-256]
            ) & 0xFFFFFFFF

        for i in range(512):
            self.s[i] = self.rotate_left(self.s[i], 8)

    @staticmethod
    def rotate_left(num: int, cnt: int) -> int:
        return ((num << cnt) | (num >> (32 - cnt))) & 0xFFFFFFFF

    def sigma0(self, x: int) -> int:
        return self.rotate_left(x, 7) ^ self.rotate_left(x, 18) ^ (x >> 3)

    def sigma1(self, x: int) -> int:
        return self.rotate_left(x, 17) ^ self.rotate_left(x, 19) ^ (x >> 10)

    def gamma0(self, x: int) -> int:
        return self.rotate_left(x, 7) ^ self.rotate_left(x, 18) ^ (x >> 3)

    def gamma1(self, x: int) -> int:
        return self.rotate_left(x, 17) ^ self.rotate_left(x, 19) ^ (x >> 10)

    def generate_keystream(self) -> None:
        t = self.s[self.idx_i] + self.s[(self.idx_i + 10) % 512]
        self.s[self.idx_i] = self.rotate_left((self.s[(self.idx_j + self.s[self.idx_i]) & 0x1ff] ^ t), 11)
        self.idx_i = (self.idx_i + 1) % 512
        self.idx_j = (self.idx_j + self.s[self.idx_i]) & 0x1ff
        self.s[self.idx_j], self.s[self.idx_i] = self.s[self.idx_i], self.s[self.idx_j]

    def generate_keystream_bytes(self, nbytes: int) -> bytes:
        result = bytearray(nbytes)
        for i in range(nbytes):
            result[i] = self.generate_keystream_byte()
        return bytes(result)

    def generate_keystream_byte(self) -> int:
        if self.idx_i == self.idx_j:
            self.generate_keystream()
        res = self.s[self.idx_i] + self.s[(self.idx_j + self.s[self.idx_i]) & 0x1ff]
        res = self.rotate_left((self.s[(res >> 10) & 0x1ff] ^ self.s[res & 0x1ff]), 11)
        self.idx_i = (self.idx_i + 1) % 512
        return res & 0xFF

    def encrypt(self, data: bytes) -> bytes:
        keystream_bytes = self.generate_keystream_bytes(len(data))
        encrypted_data = bytearray(data)
        for i in range(len(data)):
            encrypted_data[i] ^= keystream_bytes[i]
        return bytes(encrypted_data)

    def decrypt(self, data: bytes) -> bytes:
        # Todo: Optimization, extend and drink coffee
        return self.encrypt(data)
