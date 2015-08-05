# pyemailwatcher

import imaplib, email, json, smtplib, sys, mimetypes
from email.mime.text import MIMEText

class Watcher():
	def __init__(self, username, password, imap_server, smtp_server, 
			imap_port=993, smtp_port=465, confirm_from='PyEmailWatcher', smtp_tls=False):
		self.username = username
		self.password = password
		self.imap_server = imap_server
		self.imap_port = imap_port
		self.smtp_server = smtp_server
		self.smtp_port = smtp_port
		self.confirm_from = confirm_from
		self.connection = None
		self.inbox_messages = None
		self.smtp_tls = smtp_tls

	def connect(self):
		connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
		connection.login(self.username, self.password)
		connection.select()
		self.connection = connection
		return connection

	def check_inbox(self):
		if not self.connection:
			self.connect()
		typ, msgnums = self.connection.uid('search', None, 'ALL')
	
		all_messages = []
		for uid in msgnums[0].split(' '):
			try:
				uid = int(uid)
			except ValueError:
				return ['Nothing in the INBOX']
				sys.exit()
			response_ok, message_data = self.connection.uid('fetch', uid, '(BODY.PEEK[])')
			# REFERENCE: message_data = [tuple(response data, email data), ')']
					# eg message_data[0][0]: 2 (UID 3 BODY[HEADER] {2255}
			msg = email.message_from_string(message_data[0][1])
			all_messages.append((uid, msg))
		# returns uids and message content of all emails in inbox
		self.inbox_messages = all_messages
		return all_messages
	
	def search(self, query):
		if not self.inbox_messages:
			self.connection = self.connect()
			self.check_inbox()
	
		results_list = []
		for message in self.inbox_messages:
			uid = message[0]
			data = message[1]
			try:
				if query in data['subject']:
					results_list.append((uid, data))
			except TypeError as err:
				if 'NoneType' in str(err):
					print 'NO MATCHES'
					sys.exit()
				else: raise
		return results_list
	
	def delete_email(self, uid):
		trash_names = 'Trash', 'Deleted Items'
		for m in trash_names:		
			result = self.connection.uid('COPY', uid, m)
			if result[0] == 'OK':
				deleted = True
				break
			else:
				continue
		if not deleted:
			print "UNABLE TO DELETE MESSAGE"
			sys.exit()
		mov, data = self.connection.uid('STORE', uid, '+FLAGS', '(\Deleted)')
		self.connection.expunge()

	def send_confirmation(self, msg, to_addr):
		
		if self.smtp_tls: 
			send = smtplib.SMTP(self.smtp_server, self.smtp_port)
			send.starttls()
		else:
			send = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)

		send.login(self.username, self.password)
		reply_message = MIMEText(msg)
		reply_message['Subject'] = self.confirm_from
		reply_message['From'] = self.username
		reply_message['To'] = to_addr 
			# to_addr needs to be string
			# if multiple recips, use to_addr = ", ".join(recipients)

		send.sendmail(self.username, to_addr, reply_message.as_string())

	def confirm(self, uid, message):		
		self.send_confirmation("Successful update!\n\nUpdated: " \
			 + message['subject'], message['from'])
		self.delete_email(uid)

	def logout(self):
		self.connection.close()
		self.connection.logout()
