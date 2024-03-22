import re
from typing import Optional
from imap_tools import MailBox, A, AND
from email.header import decode_header

_imap_mapping = {
    'outlook.com': 'outlook.office365.com',
    'hotmail.com': 'outlook.office365.com',
    'rambler.ru': 'imap.rambler.ru',
    'gmx.com': 'imap.gmx.com'
}

__all__ = ['Email']


class Email:
    """This is a class retrieving mails' content from a corresponding email service. You also can inherit from it"""
    def __init__(self, login: str, password: str, imap_server: Optional[str] = None):
        """
        :param login: Email address of an email's account
        :param password: Password of an email's account
        :param imap_server: IMAP server of an email service. If it supports you haven't to configure it
        """
        self.__login = login
        self.__password = password
        self.__imap_server = imap_server
        if imap_server is None:
            email_service = login.split('@')[1]
            if email_service in _imap_mapping:
                self.__imap_server = _imap_mapping[email_service]
            else:
                self.__imap_server = f'imap.{email_service}'

    @property
    def login(self) -> str:
        """
        Returns address of an email's account
        :return: str
        """
        return self.__login

    @property
    def password(self) -> str:
        """
        Returns password of an email's account
        :return: str
        """
        return self.__password

    @property
    def imap_server(self) -> str:
        """
        Returns IMAP server of an email service.
        :return: str
        """
        return self.__imap_server

    def search_content(self, regex: str) -> list[str] | None:
        """
        Returns matches of regular expression finding in the mails' content
        :param regex: Regular expression
        :return: Iterable[str] | None
        """
        matches = []
        with MailBox(self.imap_server).login(self.login, self.password, 'INBOX') as mailbox:
            for msg in mailbox.fetch(A(recent=True)):
                body = msg.text or msg.html
                matches.append(re.findall(regex, body))
        return matches if matches else None

    def get_last_mail(self) -> str | None:
        """
        Returns the last mail's content
        :return: str | None
        """
        with MailBox(self.imap_server).login(self.login, self.password, 'INBOX') as mailbox:
            last_mail = None
            for msg in mailbox.fetch(A(recent=True)):
                last_mail = msg.text or msg.html

        return last_mail if last_mail else None

    def get_mails_by_sender(self, sender: str) -> list[str] | None:
        """
        Returns list of mails specified by sender's email
        :param sender: sender's email
        :return: list[str] | None
        """
        with MailBox(self.imap_server).login(self.login, self.password, 'INBOX') as mailbox:
            email_subjects = []
            for msg in mailbox.fetch(AND(from_=sender)):
                subject = msg.subject
                subject, _ = decode_header(subject)[0]
                email_subjects.append(subject)
            return email_subjects if email_subjects else None
