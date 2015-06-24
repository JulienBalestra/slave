from subprocess import check_output


class PublicIp:
	def __init__(self):
		self.current_ip = None
		self.new_ip = None
		self.updates = 0

	def update_public_ip(self):
		self.get_public_ip()
		if self.current_ip is None:
			self.load_current_ip()
		if self.current_ip != self.new_ip:
			self.current_ip = str(self.new_ip)
			self.update_route53()

	def load_current_ip(self):
		try:
			with open("current_ip", "r") as r_ip_file:
				self.current_ip = r_ip_file.read()
		except IOError:
			with open("current_ip", "w") as w_ip_file:
				w_ip_file.write(self.new_ip)

	def get_current_ip(self):
		return self.current_ip

	def get_public_ip(self):
		dig_command = "dig +short myip.opendns.com @resolver1.opendns.com"
		self.new_ip = check_output(dig_command.split(" "))
		self.updates += 1

	def __repr__(self):
		return self.get_current_ip()

	def update_route53(self):
		print "route 53"  # update hosted zone here


if __name__ == "__main__":
	slave = PublicIp()
	slave.update_public_ip()	