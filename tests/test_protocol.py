import unittest

RADIO_ADDRESS = bytes.fromhex("9C EA BB 86")


def halo_crc(pcf: int, payload: bytes) -> int:
    crc = 0xEFDF
    for byte in (*reversed(RADIO_ADDRESS), pcf, *payload):
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


class ProtocolVectors(unittest.TestCase):
    def test_stock_request(self):
        payload = bytes.fromhex("04 10 0C 0F 55 5B 0F 55 01 02")
        self.assertEqual(halo_crc(0x54, payload), 0x20B9)

    def test_direct_on(self):
        payload = bytes.fromhex("02 11 0C 0F 55 5B 0F 55 01 02")
        self.assertEqual(halo_crc(0x50, payload), 0xE962)

    def test_direct_off(self):
        payload = bytes.fromhex("02 10 0C 0F 55 5B 0F 55 01 02")
        self.assertEqual(halo_crc(0x50, payload), 0x0241)


if __name__ == "__main__":
    unittest.main()
