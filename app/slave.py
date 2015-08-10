from subprocess import check_output
import os

import boto.route53

import logger

LOGGER = logger.get_logger(__name__)


class Slave(object):
	dig_server = "myip.opendns.com"
	dig_resolver = "resolver1.opendns.com"
	aws_region = os.getenv("AWS_REGION")
	aws_domain = os.getenv("AWS_DOMAIN")
	aws_zone = os.getenv("AWS_ZONE")

	def __init__(self):
		self.my_public_ip = ""
		self.registered_ip = ""

	def get_my_public_ip(self):
		dig_command = ["dig", "+short", self.dig_server, "@%s" % self.dig_resolver]
		try:
			self.my_public_ip = check_output(dig_command).replace("\n", "")
			LOGGER.debug("<%s> [%s] my public ip" % (Slave.get_my_public_ip.__name__, self.my_public_ip))
			return self.my_public_ip
		except Exception as e:
			LOGGER.error("<%s> failed: [%s] -> %s" % (Slave.get_my_public_ip.__name__, self.registered_ip, e))

	def get_registered_ip(self):
		dig_command = ["dig", "+short", "%s" % self.aws_domain]
		try:
			self.registered_ip = check_output(dig_command).replace("\n", "")
			LOGGER.debug(
				"<%s> [%s] the zone %s ip" % (Slave.get_registered_ip.__name__, self.aws_zone, self.registered_ip))
			return self.registered_ip
		except Exception as error:
			LOGGER.error("<%s> failed: [%s] -> %s" % (Slave.get_registered_ip.__name__, self.registered_ip, error))

	def update_registered_ip(self, ttl=120):
		try:
			conn = boto.route53.connect_to_region(self.aws_region)
			zone = conn.get_zone(self.aws_zone)
			change_set = boto.route53.record.ResourceRecordSets(conn, zone.id)
			upsert = change_set.add_change("UPSERT", "%s." % self.aws_domain, "A", ttl=ttl)
			upsert.add_value(self.my_public_ip)
			ret = change_set.commit()
			LOGGER.info(
				"<%s> route53 updated: [%s] in %s" % (
				Slave.update_registered_ip.__name__, self.my_public_ip, self.aws_zone))
			return ret["ChangeResourceRecordSetsResponse"]["ChangeInfo"]["Status"] == u"PENDING"
		except Exception as e:
			LOGGER.error("<%s> route53 update failed: %s" % (Slave.update_registered_ip.__name__, e))

	def compare_ip(self):
		return self.get_my_public_ip() == self.get_registered_ip()

	def query_update_check(self):
		if self.compare_ip() is False:
			LOGGER.info("<%s> %s != %s" % (Slave.query_update_check.__name__, self.my_public_ip, self.registered_ip))
			self.update_registered_ip()

		else:
			LOGGER.info("<%s> %s == %s" % (Slave.query_update_check.__name__, self.my_public_ip, self.registered_ip))


if __name__ == "__main__":
	slave = Slave()
	slave.query_update_check()