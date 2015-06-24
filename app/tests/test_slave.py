import unittest
import os
import time

from app.slave import PublicIp


class TestPublicIp(unittest.TestCase):
	@classmethod
	def tearDownClass(cls):
		os.remove("current_ip")	
	
	def test_update_public_ip_0(self):
		slave = PublicIp()
		self.assertFalse(os.path.isfile("current_ip"))
		slave.update_public_ip()
		self.public = str(slave)
		ip = str(slave).split(".")
		self.assertEqual(len(ip), 4)
		self.assertTrue(os.path.isfile("current_ip"))
		
	def test_update_public_ip_1(self):
		self.assertTrue(os.path.isfile("current_ip"))
		stat = os.stat("current_ip")
		slave = PublicIp()
		slave.update_public_ip()
		ip = str(slave).split(".")
		self.assertEqual(len(ip), 4)
		self.assertTrue(stat == os.stat("current_ip"))	
		
	def test_update_public_ip_2(self):
		self.assertTrue(os.path.isfile("current_ip"))
		stat = os.stat("current_ip")
		time.sleep(1)
		os.remove("current_ip")
		slave = PublicIp()
		slave.update_public_ip()
		ip = str(slave).split(".")
		self.assertEqual(len(ip), 4)		
		self.assertFalse(stat == os.stat("current_ip"))