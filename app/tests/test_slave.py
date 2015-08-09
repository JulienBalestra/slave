import unittest
import re

from app import slave


class TestSlave(unittest.TestCase):
	is_ip = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

	@classmethod
	def setUpClass(cls):
		cls.slave = slave.Slave()

	def test_00_get_my_public_ip(self):
		self.slave.get_my_public_ip()
		self.assertTrue(self.is_ip.match(self.slave.my_public_ip))

	def test_01_get_registered_ip(self):
		self.slave.get_registered_ip()
		self.assertTrue(self.is_ip.match(self.slave.registered_ip))

	def test_02_check_and_update(self):
		def create_closure(instance):
			def fake_registered_ip():
				instance.registered_ip = "1.2.3.4"

			return fake_registered_ip

		self.slave.get_registered_ip = create_closure(self.slave)
		self.slave.check_and_update()