import unittest
import os
from subprocess import check_output
import time
import boto.route53


from app.slave import PublicIp


class TestPublicIp(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.aws_region = os.getenv("AWS_REGION")
		cls.aws_domain = os.getenv("AWS_DOMAIN")
		cls.aws_zone = os.getenv("AWS_ZONE")
	
	@classmethod
	def tearDownClass(cls):
		os.remove("current_ip")	
	
	def test_update_public_ip_0(self):
		slave = PublicIp()
		self.assertFalse(os.path.isfile("current_ip"))
		slave.update_current_ip()
		self.public = str(slave)
		ip = str(slave).split(".")
		self.assertEqual(len(ip), 4)
		self.assertTrue(os.path.isfile("current_ip"))
		
	def test_update_public_ip_1(self):
		self.assertTrue(os.path.isfile("current_ip"))
		stat = os.stat("current_ip")
		slave = PublicIp()
		slave.update_current_ip()
		ip = str(slave).split(".")
		self.assertEqual(len(ip), 4)
		self.assertTrue(stat == os.stat("current_ip"))	
		
	def test_update_public_ip_2(self):
		self.assertTrue(os.path.isfile("current_ip"))
		stat = os.stat("current_ip")
		time.sleep(2)
		os.remove("current_ip")
		slave = PublicIp()
		slave.update_current_ip()
		ip = str(slave).split(".")
		self.assertEqual(len(ip), 4)		
		self.assertFalse(stat == os.stat("current_ip"))
		
	def test_update_route53(self):
		conn = boto.route53.connect_to_region(self.aws_region)
		zone = conn.get_zone(self.aws_zone)
		resource = conn.get_all_rrsets(zone.id)
		
		actual_ip = None
		for rc in resource:
			if rc.name == "%s." % self.aws_domain:
				actual_ip = rc.resource_records[0]
				break
		self.assertIsNot(None, actual_ip)
		slave = PublicIp()
		slave.current_ip = actual_ip
		slave.update_route53(ttl=86400)