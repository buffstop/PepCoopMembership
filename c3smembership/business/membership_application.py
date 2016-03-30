# -*- coding: utf-8 -*-

from datetime import (
    datetime,
)
from c3smembership.mail_utils import (
    make_signature_confirmation_email,
    make_payment_confirmation_email,
    send_message,
)
from pyramid_mailer.message import Message


class IMembershipApplication(object):

    def set_signature_status(self, member_id, signature_status):
        """
        Sets the signature status of the member indicating whether a signed
        contract was received.

        Args:
            member_id (int): The ID of the member of which the signature status
                must be set.
            signature_status (boolean): Boolean value indicating the signature
                status to be set to.
        """
        raise NotImplementedError()

    def get_signature_status(self, member_id):
        """
        Gets the signature status of the member's application indicating whether
        a signed contract was received.

        Args:
            member_id (int): The ID of the member of which the signature status
                is requested.

        Returns:
            A boolean value indicating the signature status of the member's
            membership application. True, if a signed contract was received,
            otherwise False.
        """
        raise NotImplementedError()

    def set_payment_status(self, member_id, payment_status):
        """
        Sets the payment status of the member indicating whether a signed
        contract was received.

        Args:
            member_id (int): The ID of the member of which the payment status
                must be set.
            signature_status (boolean): Boolean value indicating the payment
                status to be set to.
        """
        raise NotImplementedError()

    def get_payment_status(self, member_id):
        """
        Gets the payment status of the member's application indicating whether
        a signed contract was received.

        Args:
            member_id (int): The ID of the member of which the payment status
                is requested.

        Returns:
            A boolean value indicating the payment status of the member's
            membership application. True, if a signed contract was received,
            otherwise False.
        """
        raise NotImplementedError()

    def mail_signature_confirmation(self, member_id):
        """
        Sends an email to the member in order to confirm that the signed
        contract was received by the C3S.

        Args:
            member_id (int): The ID of the member to which the confirmation
                email is sent.
        """
        raise NotImplementedError()


class MembershipApplication(IMembershipApplication):

    # TODO:
    #
    # - http://code.activestate.com/recipes/576862/
    # - http://stackoverflow.com/questions/8100166/inheriting-methods-
    #   docstrings-in-python

    def __init__(self, c3s_member):
        """
        Initialises the MembershipApplication object.

        Args:
            c3s_member: Object implementing a get_by_id(member_id) method
                returning a member objects with properties
                signature_received_date and signature_received.
        """
        self.c3s_member = c3s_member

    def set_signature_status(self, member_id, signature_status):
        member = self.c3s_member.get_by_id(member_id)
        member.signature_received = signature_status
        if signature_status:
            signature_received_date = datetime.now()
        else:
            signature_received_date = datetime(1970, 1, 1)
        member.signature_received_date = signature_received_date

    def get_signature_status(self, member_id):
        member = self.c3s_member.get_by_id(member_id)
        return (member.signature_received == True)

    def set_payment_status(self, member_id, payment_status):
        member = self.c3s_member.get_by_id(member_id)
        member.payment_received = payment_status
        if payment_status:
            payment_received_date = datetime.now()
        else:
            payment_received_date = datetime(1970, 1, 1)
        member.payment_received_date = payment_received_date

    def get_payment_status(self, member_id):
        member = self.c3s_member.get_by_id(member_id)
        return (member.payment_received == True)

    def mail_signature_confirmation(self, member_id, request):
        # TODO:
        # - Email functionality should be injected to be testable!
        # - Email functionality is an external service which belongs to
        #   cross-cutting concerns.
        # - Emailing service should be independent of the presentation layer,
        #   i.e. independent from pyramid which makes it hard to use
        #   pyramid_mailer.
        member = self.c3s_member.get_by_id(member_id)
        email_subject, email_body = make_signature_confirmation_email(member)
        # TODO: Remove dependency to pyramid_mail.
        message = Message(
            subject=email_subject,
            sender='yes@c3s.cc',
            recipients=[member.email],
            body=email_body
        )
        # TODO: Resolve request dependency.
        send_message(request, message)
        member.signature_confirmed = True
        member.signature_confirmed_date = datetime.now()
