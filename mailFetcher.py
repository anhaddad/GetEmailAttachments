import imaplib
import email
import tempfile
import datetime
import os
import re

download_folder = tempfile.gettempdir()  # Unless otherwise is stated in the object


class EmailConnection:
    mail_server = None
    connection = None
    error = None
    inbox = None

    def __init__(self, mail_server):
        self.mail_server = mail_server

    def connect(self, username, password):
        try:
            self.connection = imaplib.IMAP4_SSL(self.mail_server)
            self.connection.login(username, password)
        except self.connection.error:
            return False
        return True

    def select_inbox(self, inbox, ro=True):
        rv, mboxes = self.connection.list()
        mboxExists = False
        if rv == 'OK':
            for m in mboxes:
                if inbox.lower() in str(m).lower():
                    mboxExists = True
                    break
            if not mboxExists:
                print("Requested inbox does not exist")
                return None
            rv, data = self.connection.select(inbox, readonly=ro)  # False if we want to mark emails as read
            if rv == 'OK':
                return EmailInbox(self)
            else:
                print("Cannot access requested mailbox")
                return None
        else:
            print("Cannot list mailboxes")
            return None

    def disconnect(self):
        try:
            self.connection.close()
        except:
            return


class EmailHeader:
    message = None

    def __init__(self, message):
        h = email.header.make_header
        d = email.header.decode_header

        self.message = message

        """
        Let's build dynamically the properties and their values,
        handling any error occurs because of faulty entry.
        """
        mobjects = ['Subject', 'From', 'To']
        for obj in mobjects:
            try:
                obvalue = h(d(message.msg[obj]))
                setattr(self, obj, obvalue)
            except:
                faulty_name = '_faulty' + obj
                setattr(self, obj, faulty_name)

        self.Rdate = message.remote_date()
        self.Ldate = message.local_date()

    def __str__(self):
        return "From: {0} \nSender's Date: {1} \nLocal Date: {2} \nTo: {3} \nSubject: {4}" \
            .format(self.From, self.Rdate, self.Ldate, self.To, self.Subject)


class EmailMessage:
    inbox = None
    msg = None
    header = None

    def __init__(self, msg, inbox):
        self.inbox = inbox
        self.msg = msg
        self.header = EmailHeader(self)

    def remote_date(self):
        return self.msg['Date']

    def local_date(self):
        """
        Now convert sender's date to local date-time
        """
        date_tuple = email.utils.parsedate_tz(self.msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple))
            return local_date.strftime("%a, %d %b %Y %H:%M:%S")

    def extract_body(self):
        """
        Given raw message, extract only the body of the message
        """
        for part in self.msg.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload()

    def save_attachment(self, download_folder):
        """
        Given a message, save its attachments to the specified download folder
        return: file path to attachment
        """
        att_path = "No attachment found."
        for part in self.msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename is None:
                filename = "_faultyName"
            filename = re.sub('[/\\\\:*?="<>|+\r\n\t`]', '', filename)
            att_path = os.path.join(download_folder, filename)

            if not os.path.isfile(att_path):
                fp = open(att_path, 'wb')
                try:
                    att = part.get_payload(decode=True)
                except:
                    att = "_faultyAttachment"
                    continue

                fp.write(att)
                fp.close()

        return att_path

    def __str__(self):
        try:
            return str(self.header) \
                   + str(self.extract_body())
        except:
            pass


class EmailInbox:
    conn = None
    msglist = None

    def __init__(self, conn):
        self.conn = conn

    def fetch_mail(self, filter="UnSeen"):
        """
        Get the body of an email. Variable level can has values "ALL", "Seen" or "UnSeen. UnSeen is the default value."
        """
        self.msglist = []
        rv, data = self.conn.connection.search(None, filter)
        if rv != 'OK':
            print("No messages found!")
            return None
        else:
            for num in data[0].split():
                rv, data = self.conn.connection.fetch(num, '(RFC822)')
                if rv != 'OK':
                    print("ERROR fetching message", num)
                else:
                    msg = email.message_from_bytes(data[0][1])
                    em = EmailMessage(msg, self)
                    yield em  # With this line we check and save the progress.
        return self.msglist


if __name__ == '__main__':
    my_email = EmailConnection("EMAIL-SERVER")
    if my_email.connect("EMAIL-ADDRESS", "EMAIL-PASSWORD"):
        inbox = my_email.select_inbox("inbox")
        if not inbox is None:
            mail = inbox.fetch_mail(
                filter="All"
            )
            for m in mail:
                print(m)
                m.save_attachment(download_folder)
        my_email.disconnect()
    else:
        print("Cannot connect to server")
