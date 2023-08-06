#!/Users/christmas/opt/anaconda3/bin/python3
# -*- coding: utf-8 -*-
#  日期 : 2023/3/10 13:58
#  作者 : Christmas
#  邮箱 : 273519355@qq.com
#  项目 : Project
#  版本 : python 3
#  摘要 :
"""
processBar such as: ftp sftp
"""
import datetime


class SftpProcessbar(object):
	"""
	sftp_obj =SftpProcessbar()
	Sprocess_bar = sftp_obj.process_bar

	# ssh = paramiko.SSHClient()
	# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	# ssh.connect(hostname=host, port=22, username='wave', password='wave', timeout=100)
	# sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
	# sftp_obj =SftpProcessbar()
	# Sprocess_bar = sftp_obj.process_bar
	# sftp.put(local_path, a, callback=Sprocess_bar)
	"""

	def __init__(self, bar_length=30, change_percent=1):
		self.bar_length = bar_length
		self.lastShownPercent = 0
		self.change_percent = change_percent

	def call_back(self, curr=100, total=100):
		bar_length = self.bar_length
		percents = '\033[32;1m%s\033[0m' % round(float(curr) * 100 / float(total), self.change_percent)
		filled = int(bar_length * curr / float(total))
		bar = '\033[32;1m%s\033[0m' % '=' * filled + '-' * (bar_length - filled)

		percentComplete = round((curr / total) * 100, self.change_percent)
		if self.lastShownPercent != percentComplete:
			self.lastShownPercent = percentComplete
			ddt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			print(f'{ddt} ---> [{bar}] {percents}% already complete: {translate_byte(curr)}, total: {translate_byte(total)}\r', end='')

	def process_bar(self):
		return self.call_back


def translate_byte(B):
	B = float(B)
	KB = float(1024)
	MB = float(KB * 1024)
	GB = float(MB * 1024)
	TB = float(GB * 1024)
	if B < KB:
		return f"{B} {'bytes' if B > 1 else 'byte'}"
	elif KB <= B < MB:
		return '{:.2f} KB'.format(B / KB)
	elif MB <= B < GB:
		return '{:.2f} MB'.format(B / MB)
	elif GB <= B < TB:
		return '{:.2f} GB'.format(B / GB)
	else:
		return '{:.2f} TB'.format(B / TB)


class FtpProcessbar(object):
	"""
	Ftp_obj = FtpProcessbar(os.path.getsize(local_path))
	Fprocess_bar = Ftp_obj.process_bar()

	# ftp = ftplib.FTP()
	# ftp.encoding = 'utf-8'
	# ftp.set_debuglevel(0)
	# ftp.connect(host=_host, port=_port)
	# ftp.login(_username, _password)
	# Ftp_obj = FtpProcessbar(os.path.getsize(local_path))
	# Fprocess_bar = Ftp_obj.process_bar()
	# with open(local_path, 'rb') as fp:
	#   ftp.storbinary(f'STOR {file}', fp, buf_size, Fprocess_bar)
	"""

	def __init__(self, totalSize, bar_length=30, change_percent=1):
		self.totalSize = totalSize
		self.sizeWritten = 0
		self.lastShownPercent = 0
		self.bar_length = bar_length  # 进度条长度
		self.change_percent = change_percent  # 进度条变化百分比 0为1%输出 1为0.1%输出 2为0.01%输出

	def call_back(self, block):
		self.sizeWritten += len(block)
		bar_length = self.bar_length
		percents = '\033[32;1m%s\033[0m' % round(float(self.sizeWritten) * 100 / float(self.totalSize), self.change_percent)
		filled = int(bar_length * self.sizeWritten / float(self.totalSize))
		bar = '\033[32;1m%s\033[0m' % '=' * filled + '-' * (bar_length - filled)

		percentComplete = round((self.sizeWritten / self.totalSize) * 100, self.change_percent)
		if self.lastShownPercent != percentComplete:
			self.lastShownPercent = percentComplete
			ddt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			print(f'{ddt} ---> [{bar}] {percents}% already complete: {translate_byte(self.sizeWritten)}, total: {translate_byte(self.totalSize)}\r', end='')

	def process_bar(self):
		return self.call_back
