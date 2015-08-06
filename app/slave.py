from subprocess import check_output
import re
import boto.route53
import os
import logger

LOGGER = logger.get_logger(__name__)


class PublicIp:
	_dig_server = "myip.opendns.com"
	_dig_resolver = "resolver1.opendns.com"
	_aws_region = os.getenv("AWS_REGION")
	_aws_domain = os.getenv("AWS_DOMAIN")
	_aws_zone = os.getenv("AWS_ZONE")

	def __init__(self):
		self.current_ip = None
		self.new_ip = None

	def update_current_ip(self):
		self.get_public_ip()
		if self.current_ip is None:
			self.load_current_ip()
		if self.current_ip != self.new_ip:
			LOGGER.info("IP address changed from %s to %s" % (str(self.current_ip), self.new_ip))
			self.current_ip = str(self.new_ip)

	def load_current_ip(self):
		try:
			with open("current_ip", "r") as r_ip_file:  # TODO use nslookup instead of text file
				self.current_ip = r_ip_file.read()
		except IOError:
			LOGGER.warning("current ip file does not exist")
			self.flush_current_ip()
			self.load_current_ip()

	def flush_current_ip(self):
		with open("current_ip", "w") as w_ip_file:
			try:
				w_ip_file.write(self.new_ip)
			except TypeError:
				LOGGER.error("instance <new_ip>: %s not an IP address, exit (2)" % str(self.new_ip))
				exit(2)

	def get_current_ip(self):
		return self.current_ip
	
	def get_zone_ip(self):
		regex = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
		nslookup_command = ["nslookup", "%s" % self._aws_zone]
		ret = check_output(nslookup_command)
		return regex.findall(ret.split(self._aws_zone)[1])[0]

	def get_public_ip(self):
		dig_command = "dig +short %s @%s" % (self._dig_server, self._dig_resolver)
		try:
			self.new_ip = check_output(dig_command.split(" "))
		except Exception as e:
			LOGGER.error("failed run %s: %s" % (dig_command, e))

	def __repr__(self):
		return self.get_current_ip()

	def update_route53(self, ttl=120):
		try:
			conn = boto.route53.connect_to_region(self._aws_region)
			zone = conn.get_zone(self._aws_zone)
			change_set = boto.route53.record.ResourceRecordSets(conn, zone.id)
			upsert = change_set.add_change("UPSERT", "%s." % self._aws_domain, "A", ttl=ttl)
			upsert.add_value(self.current_ip)
			ret = change_set.commit()
			LOGGER.info("route53 commit done")
			return ret["ChangeResourceRecordSetsResponse"]["ChangeInfo"]["Status"] == u"PENDING"
		except Exception as e:
			LOGGER.error("failed to update route53: %s" % e)


if __name__ == "__main__":
	slave = PublicIp()
	slave.update_current_ip()