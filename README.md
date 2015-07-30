# PyEmailWatcher
A simple Python IMAP and SMTP wrapper for watching an inbox for input.

About
----

`PyEmailWatcher` is an IMAP and SMTP wrapper which allows for easy monitoring of an inbox (to perform another Python action based on email input) and sending of confirmation emails.

I include this in several projects which run as `crontab` tasks to check an inbox for input every minute.

One class is defined, called `Watcher`, which takes the following arguments:

- username
- password
- imap_server
- smtp_server
- imap_port (default 993)
- smtp_port (default 465)
- confirm_from (the 'from' field on confirmation emails, default 'PyEmailWatcher')
- smtp_tls (default False)

The first four parameters are required.

Each message is treated as a tuple of the message's uid and an [email.message](https://docs.python.org/2/library/email.message.html) object.

When attempting a delete, both 'Trash' and 'Deleted Items' folders will be attempted.

Example
-----

Below is a example script that I use to monitor an inbox and update my blog with each new email. You can see the full code of that application [here](https://github.com/jasongtz).

----------

		login = Watcher('jamesbond@misix.com', 'totallysecretpassword', 
			'imap.misix.com', 'smtp.misix.com')
		login.connect()
		results = login.search('Mission: ')

		for email in results:
			# email = tuple
			uid, message = email

			title = message['subject']
			for part in message.walk():
			if part.get_content_maintype() == 'text':
				body = email.get_payload()
				break

			update_blog(title, body)
			
			# Send a confirmation email and delete the message
			login.confirm(uid, message)
		
		login.logout()

------------

Requirements
------

`PyEmailWatcher` dependencies are all in the standard library.

Coming Soon
------

- Better exception handling
>	- deleting emails
>	- empty inboxes
- Looking in folders other than 'Inbox'
