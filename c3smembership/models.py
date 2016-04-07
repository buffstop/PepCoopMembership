# -*- coding: utf-8  -*-
"""
This module holds the database models for c3sMembership.

Unit and functional tests for the code are in tests/test_models.py.
Other functional and integration tests can be found throughout the
other bits of tests and code relying on or using these models.

The classes below represent the database tables.
It is actually a SQLAlchemy model.

Classes / Data Objects:

* **Groups** (Roles for Users)
* **C3sStaff** (backend login people, administration)
* **Shares** (packages -- members can hold packages of shares)
* **C3sMember** (members .. or applications to become members)
* **Dues15Invoice** (membership dues, 2015 edition)
"""

from datetime import (
    datetime,
)
from decimal import Decimal
import cryptacular.bcrypt
import math
import re

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    Boolean,
    DateTime,
    Date,
    Unicode,
    or_,
    and_,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from sqlalchemy.sql import expression
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    synonym
)
import sqlalchemy.types as types

from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
crypt = cryptacular.bcrypt.BCRYPTPasswordManager()


def hash_password(password):
    return unicode(crypt.encode(password))


# TODO: Use standard SQLAlchemy Decimal when a database is used which supports
# it.
class SqliteDecimal(types.TypeDecorator):
    """
    Type decorator for persisting Decimal (currency values)

    TODO: Use standard SQLAlchemy Decimal
    when a database is used which supports it.
    """
    impl = types.String

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.VARCHAR(100))

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None and value != '':
            return Decimal(value)
        else:
            return None

DatabaseDecimal = SqliteDecimal


class Group(Base):
    """
    The table of Groups.

    aka roles for users.

    Users in group 'staff' may do things others may not.
    """
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, nullable=False)
    """technical id. / number in table (Integer, Primary Key)"""
    name = Column(Unicode(30), unique=True, nullable=False)
    """name of the group (Unicode)"""
    def __str__(self):
        return 'group:%s' % self.name

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_staffers_group(cls, groupname=u'staff'):
        """
        Get the "staff" group.

        Returns:
            object: staff group.
        """
        dbsession = DBSession()
        staff_group = dbsession.query(
            cls).filter(cls.name == groupname).first()
        return staff_group


# table for relation between staffers and groups
staff_groups = Table(
    'staff_groups', Base.metadata,
    Column(
        'staff_id', Integer, ForeignKey('staff.id'),
        primary_key=True, nullable=False),
    Column(
        'group_id', Integer, ForeignKey('groups.id'),
        primary_key=True, nullable=False)
)
# """
# Table for relation of staff to groups
# """


class C3sStaff(Base):
    """
    C3S staff may login and do things.

    """
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True)
    """technical id. / number in table (integer, primary key)"""
    login = Column(Unicode(255), unique=True)
    """every user has a login name. (unicode)"""
    _password = Column('password', Unicode(60))
    """a hash"""
    last_password_change = Column(
        DateTime,
        default=func.current_timestamp())
    """timestamp of last password change/form submission (Datetime)"""
    email = Column(Unicode(255))
    """email address (Unicode)"""
    groups = relationship(
        Group,
        secondary=staff_groups,
        backref="staff")
    """list of group objects (users groups) (relation)"""
    def _init_(self, login, password, email):  # pragma: no cover
        """
        make new group
        """
        self.login = login
        self.password = password
        self.last_password_change = datetime.now()
        self.email = email

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    @classmethod
    def get_by_id(cls, id):
        """
        Get C3sStaff object by id.

        Args:
            id: the id of the C3sStaff object to be returned.

        Returns:
            * **object**: C3sStaff object with relevant id, if exists.
            * **None**: if id can't be found.
        """
        return DBSession.query(cls).filter(cls.id == id).first()

    @classmethod
    def get_by_login(cls, login):
        """
        Get C3sStaff object by login.

        Args:
            login: the login of the C3sStaff object to be returned.

        Returns:
            * **object**: C3sStaff object with relevant login, if exists.
            * **None**: if login can't be found.
        """
        return DBSession.query(cls).filter(cls.login == login).first()

    @classmethod
    def check_password(cls, login, password):
        """
        Check staff password.

        Args:
            login: staff login.
            password: staff password as supplied.

        Returns:
            the answer of bcrypt.crypt, comparing the password supplied
                and the hash from the database
        """
        staffer = cls.get_by_login(login)
        return crypt.check(staffer.password, password)

    # this one is used by RequestWithUserAttribute
    @classmethod
    def check_user_or_None(cls, login):
        """
        Check whether a user by that login exists in the database.

        Args:
            login: the name to log in with

        Returns:
            * **C3sStaff object**, if login exists.
            * **None**, if login does not exist.
        """
        login = cls.get_by_login(login)  # is None if user not exists
        return login

    @classmethod
    def delete_by_id(cls, id):
        """
        Delete one C3sStaff object by id.
        """
        _del = DBSession.query(cls).filter(cls.id == id).first()
        _del.groups = []
        DBSession.query(cls).filter(cls.id == id).delete()
        return

    @classmethod
    def get_all(cls):
        """
        Get all C3sStaff objects from the database.

        Returns:
            list: list of C3sStaff objects.
        """
        return DBSession.query(cls).all()


class Shares(Base):
    """
    The database of shares.

    Each entry is a number of shares varying from 1 to 60.
    Each member may have several packages of shares,
    e.g. from different events or processes
    (crowdfunding, founding ceremony, web form).

    Once AFM submissions are complete,
    the relevant information about the shares is moved here.
    Each member then has a list of these objects.

    """
    __tablename__ = 'shares'
    id = Column(Integer, primary_key=True)
    """technical id. / number in table (integer, primary key)"""
    number = Column(Integer())
    """number of shares in this package(integer)"""
    date_of_acquisition = Column(DateTime(), nullable=False)
    """acquired when (datetime)"""
    reference_code = Column(Unicode(255), unique=True)
    """ex email_confirm_code (Unicode)"""
    signature_received = Column(Boolean, default=False)
    """flag of acknowledgement for signature to arrive at headquarters."""
    signature_received_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    """timestamp of acknowledgement for signature to arrive at headquarters."""
    signature_confirmed = Column(Boolean, default=False)
    """flag to remember sending signature receipt email to oncoming member"""
    signature_confirmed_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    """timestamp of sending signature receipt email to oncoming member."""
    payment_received = Column(Boolean, default=False)
    """flag of acknowledgement for payment to arrive at headquarters."""
    payment_received_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    """timestamp of acknowledgement for payment to arrive at headquarters."""
    payment_confirmed = Column(Boolean, default=False)
    """flag to remember sending payment receipt email to oncoming member."""
    payment_confirmed_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    """timestamp of sending signature receipt email to oncoming member"""
    accountant_comment = Column(Unicode(255))
    """freestyle comment. unicode"""

    @classmethod
    def get_number(cls):
        """return number of entries (by counting rows in table)"""
        return DBSession.query(cls).count()

    @classmethod
    def get_max_id(cls):
        """return number of entries (by counting rows in table)"""
        res, = DBSession.query(func.max(cls.id)).first()
        return res

    @classmethod
    def get_by_id(cls, _id):
        """return one package of shares by id"""
        return DBSession.query(cls).filter(cls.id == _id).first()

    @classmethod
    def get_all(cls):
        """return all packages of shares"""
        return DBSession.query(cls).all()

    @classmethod
    def get_total_shares(cls):
        """return number of shares of accepted members"""
        all_shares = DBSession.query(cls).all()
        total = 0
        for share in all_shares:
            total += share.number
        return total

    @classmethod
    def delete_by_id(cls, _id):
        """delete one package of shares by id"""
        return DBSession.query(cls).filter(cls.id == _id).delete()

# table for relation between membership and shares
members_shares = Table(
    'members_shares', Base.metadata,
    Column(
        'members_id', Integer, ForeignKey('members.id'),
        primary_key=True, nullable=False),
    Column(
        'shares_id', Integer, ForeignKey('shares.id'),
        primary_key=True, nullable=False)
)


class C3sMember(Base):
    """
    This table holds datasets from submissions to the C3S AFM form
    (AFM = application for membership),
    as well as members who have completed the process
    of becoming a member.

    Apart from datasets from the original form,
    other datasets have found their way into the database
    through imports: crowdfunders and founding members, for example.

    * The crowdfunders were gathered through a CF platform.
    * The founders from the initial assembly (RL! Hamburg!)
    * legal entities (we had a form on dead wood)

    Some attributes have been added over time to cater for different needs.
    """
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    """technical id. / number in table (integer, primary key)"""

    # personal information
    """
    **personal information**
    """
    firstname = Column(Unicode(255))
    """given name(s) of person"""
    lastname = Column(Unicode(255))
    """last name of person"""
    email = Column(Unicode(255))
    """email address of person
    """
    _password = Column('password', Unicode(60))
    """password hash of person
    """
    last_password_change = Column(
        DateTime,
        default=func.current_timestamp())
    """timestamp of password persistence (time of submission)
    """
    # pass_reset_token = Column(Unicode(255))
    address1 = Column(Unicode(255))
    """Street & Number"""
    address2 = Column(Unicode(255))
    """Address continued"""
    postcode = Column(Unicode(255))
    """Postal Code"""
    city = Column(Unicode(255))
    """City or Place"""
    country = Column(Unicode(255))
    """Country"""
    locale = Column(Unicode(255))
    """The Language chosen by a member when filling out the form.

    We remember this so we know which language to address her with.
    """
    date_of_birth = Column(Date(), nullable=False)
    email_is_confirmed = Column(Boolean, default=False)
    email_confirm_code = Column(Unicode(255), unique=True)  # reference code
    """The Code used as reference when registering for membership:

    * contained in URL of link applicants have to use to get their PDF.
    * used for bank transfer reference

    """
    email_confirm_token = Column(Unicode(255), unique=True)  # token
    '''Unicode'''
    email_confirm_mail_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    # duplicate entries // people submitting at different times
    is_duplicate = Column(Boolean, default=False)
    """boolean

    * flag for entries that are known duplicates of other applications
      if person has already applied before.
    """
    is_duplicate_of = Column(Integer, nullable=True)
    """Integer

    * id of entry considered as original or relevant for membership
    """
    # shares
    num_shares = Column(Integer())  # XXX TODO: check for number <= max_shares
    """Integer

    * The number of shares from the time of afm submission
    * Then application is approved, this number of shares is turned into
      an entry in the shares list below, referencing a shares package
      which is persisted in the Shares table.

    .. note:: For accepted members, this is not necessarily the total
       number of shares, as members can hold several packages,
       from different times of acquisition.

    """
    date_of_submission = Column(DateTime(), nullable=False)
    """datetime

    * the date and time this application was submitted
    """
    signature_received = Column(Boolean, default=False)
    """Boolean

    * Has the signature been received?
    """
    signature_received_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    """datetime

    * the date and time this application was submitted
    """
    signature_confirmed = Column(Boolean, default=False)
    """Boolean

    * Has reception of signed form been confirmed?
    """
    signature_confirmed_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    """datetime

    * the date and time arrival of signed form was confirmed per email
    """
    payment_received = Column(Boolean, default=False)
    """Boolean

    * Has the payment been received?
    """
    payment_received_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    """datetime

    * the date and time payment for this application was received
    """
    payment_confirmed = Column(Boolean, default=False)
    """Boolean

    * Has the payment been confirmed?
    """
    payment_confirmed_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    """datetime

    * the date and time this application was confirmed per email
    """
    # shares in other table
    shares = relationship(
        Shares,
        secondary=members_shares,
        backref="members"
    )
    """relation

    * list of shares packages a member has acquired.
    * has entries as soon as an application for membership has been approved
      by the board of directors -- and the relevant date of approval
      has been entered into the system by staff.
    """
    # reminders
    sent_signature_reminder = Column(Integer, default=0)
    """Integer

    * stores how many signature reminders have been sent out
    """
    sent_signature_reminder_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    """DateTime

    * stores *when* the last signature reminder was sent out
    """
    sent_payment_reminder = Column(Integer, default=0)
    """Integer

    * stores how many payment reminders have been sent out
    """
    sent_payment_reminder_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    """DateTime

    * stores *when* the last payment reminder was sent out
    """
    # comment
    accountant_comment = Column(Unicode(255))
    # membership information
    membership_type = Column(Unicode(255))
    """Unicode

    * Type of membership. either one of

       * normal (persons, artists)
       * investing (non-artist persons or legal entities)
    """
    member_of_colsoc = Column(Boolean, default=False)
    """Boolean

    * is member of other collecting society
    """
    name_of_colsoc = Column(Unicode(255))
    """Unicode

    * name(s) of other collecting societies
    """
    # acquisition of membership
    membership_accepted = Column(Boolean, default=False)
    """Boolean

    * has the membersip been accepted by the board of directors?
    """
    membership_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    """DateTime

    Date of membership approval by the board.
    """
    membership_number = Column(Integer())
    """Integer

    * Membership Number given upon approval.
    """
    # ## loss of membership
    # the date on which the membership terminates, i.e. the date of
    # membership and the day after which the membership does no longer exist
    membership_loss_date = Column(DateTime())
    # the membership can be lost upon:
    # - resignation
    # - expulsion
    # - death
    # - bankruptcy
    # - transfer of remaining shares
    membership_loss_type = Column(Unicode(255))

    # startnex repair operations
    mtype_confirm_token = Column(Unicode(255))
    mtype_email_date = Column(DateTime(), default=datetime(1970, 1, 1))
    # invitations
    email_invite_flag_bcgv14 = Column(Boolean, default=False)
    email_invite_date_bcgv14 = Column(DateTime(), default=datetime(1970, 1, 1))
    email_invite_flag_bcgv15 = Column(Boolean, default=False)
    email_invite_date_bcgv15 = Column(DateTime(), default=datetime(1970, 1, 1))
    email_invite_token_bcgv15 = Column(Unicode(255))
    email_invite_flag_bcgv16 = Column(Boolean, default=False)
    email_invite_date_bcgv16 = Column(DateTime(), default=datetime(1970, 1, 1))
    email_invite_token_bcgv16 = Column(Unicode(255))
    # legal entities
    is_legalentity = Column(Boolean, default=False)
    court_of_law = Column(Unicode(255))
    registration_number = Column(Unicode(255))
    # membership certificate
    certificate_email = Column(Boolean, default=False)
    certificate_token = Column(Unicode(10))
    certificate_email_date = Column(DateTime())
    # membership fees aka dues, for 2015
    dues15_invoice = Column(Boolean, default=False)  # sent?
    dues15_invoice_date = Column(DateTime())  # when?
    dues15_invoice_no = Column(Integer())  # lfd. nummer
    dues15_token = Column(Unicode(10))  # access token
    dues15_start = Column(Unicode(255))  # a string, 2015 quarter of membership
    dues15_amount = Column(  # calculated amount member has to pay by default
        DatabaseDecimal(12, 2), default=Decimal('NaN'))
    dues15_reduced = Column(Boolean, default=False)  # was reduced?
    _dues15_amount_reduced = Column(
        'dues15_amount_reduced',  # the amount reduced to
        DatabaseDecimal(12, 2), default=Decimal('NaN'))  # ..to xs
    # balance
    _dues15_balance = Column(
        'dues15_balance',  # the amount to be settled
        DatabaseDecimal(12, 2), default=Decimal('0'))
    dues15_balanced = Column(Boolean, default=True)  # was balanced?
    # payment
    dues15_paid = Column(Boolean, default=False)  # payment flag
    dues15_amount_paid = Column(  # how much paid?
        DatabaseDecimal(12, 2), default=Decimal('0'))
    dues15_paid_date = Column(DateTime())  # paid when?

    def __init__(self, firstname, lastname, email, password,
                 address1, address2, postcode, city, country, locale,
                 date_of_birth, email_is_confirmed, email_confirm_code,
                 num_shares,
                 date_of_submission,
                 membership_type, member_of_colsoc, name_of_colsoc):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.last_password_change = datetime.now()
        self.address1 = address1
        self.address2 = address2
        self.postcode = postcode
        self.city = city
        self.country = country
        self.locale = locale
        self.date_of_birth = date_of_birth
        self.email_is_confirmed = email_is_confirmed
        self.email_confirm_code = email_confirm_code
        self.num_shares = num_shares
        self.date_of_submission = date_of_submission
        self.signature_received = False
        self.payment_received = False
        self.membership_type = membership_type
        self.member_of_colsoc = member_of_colsoc
        if self.member_of_colsoc is True:
            self.name_of_colsoc = name_of_colsoc
        else:
            self.name_of_colsoc = u''

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    @hybrid_property
    def dues15_balance(self):
        """
        XXX TODO write this docstring
        XXX TODO write testcase in test_models.py
        """
        return self._dues15_balance

    @dues15_balance.setter
    def dues15_balance(self, dues15_balance):
        """
        XXX TODO write this docstring
        XXX TODO write testcase in test_models.py
        """
        self._dues15_balance = dues15_balance
        self.dues15_balanced = self._dues15_balance == Decimal('0')

    @hybrid_property
    def dues15_amount_reduced(self):
        """
        XXX TODO write this docstring
        XXX TODO write testcase in test_models.py
        """
        return self._dues15_amount_reduced

    @dues15_amount_reduced.setter
    def dues15_amount_reduced(self, dues15_amount_reduced):
        """
        XXX TODO write this docstring
        XXX TODO write testcase in test_models.py
        """
        self._dues15_amount_reduced = dues15_amount_reduced
        self.dues15_reduced = \
            not math.isnan(self.dues15_amount_reduced) \
            and \
            self.dues15_amount_reduced != self.dues15_amount

    @classmethod
    def get_by_code(cls, email_confirm_code):
        """
        Find a member by confirmation code

        This is needed when a user returns from reading her email
        and clicking on a link containing the confirmation code.
        As the code is unique, one record is returned.

        Returns:
           object: C3sMember object
        """
        return DBSession.query(cls).filter(
            cls.email_confirm_code == email_confirm_code).first()

    # used got barcamp & general assembly invitations
    @classmethod
    def get_by_bcgvtoken(cls, token):
        """
        Find a member by token used for GA and BarCamp.

        This is needed when a user returns from reading her email
        and clicking on a link containing the token.

        Returns:
            object: C3sMember object
        """
        return DBSession.query(cls).filter(
            cls.email_invite_token_bcgv16 == token).first()

    @classmethod
    def check_for_existing_confirm_code(cls, email_confirm_code):
        """
        check if a code is already present
        """
        check = DBSession.query(cls).filter(
            cls.email_confirm_code == email_confirm_code).first()
        if check:  # pragma: no cover
            return True
        else:
            return False

    @classmethod
    def get_by_id(cls, _id):
        """
        Get one C3sMember object by id.

        Returns:
            * **C3sMember object**, if id exists.
            * **None**, if id does not exist.
        """
        return DBSession.query(cls).filter(cls.id == _id).first()

    @classmethod
    def get_by_email(cls, _email):
        """return one or more members by email (a list!)"""
        return DBSession.query(cls).filter(cls.email == _email).all()

    @classmethod
    def get_by_dues15_token(cls, _code):
        """return one member by fee token"""
        return DBSession.query(cls).filter(cls.dues15_token == _code).first()

    @classmethod
    def get_all(cls):
        """return all afms and members"""
        return DBSession.query(cls).all()

    # needed for invitation to barcam & general assembly
    @classmethod
    def get_invitees(cls, num):
        """
        Get a given number *n* of members to invite for barcamp and GV.

        Queries the database for members, where

        * members are accepted
        * members have not received their invitation email yet

        Args:
          num is the number *n* of invitees to return

        Returns:
          a list of *n* member objects
        """
        return DBSession.query(cls).filter(
            and_(
                (cls.membership_accepted == 1),
                # cls.email_invite_flag_bcgv16 != 1,
                or_(
                    (cls.email_invite_flag_bcgv16 == 0),
                    (cls.email_invite_flag_bcgv16 == ''),
                    (cls.email_invite_flag_bcgv16 == None),
                )
            )
        ).slice(0, num).all()

    @classmethod
    def get_dues_invoicees(cls, num):
        """
        Get a given number *n* of members to send dues invoices to.

        Queries the database for members, where

        * members are accepted
        * members have not received their dues invoice email yet

        Args:
          num is the number *n* of C3sMembers to return

        Returns:
          a list of *n* member objects
        """
        return DBSession.query(cls).filter(
            and_(
                cls.membership_accepted == 1,
                cls.dues15_invoice == 0
            )).slice(0, num).all()

    @classmethod
    def delete_by_id(cls, _id):
        """
        Delete one C3sMember entry by id.

        Args:
            _id: the id to delete

        Returns:
            * **1** on success
            * **0** else
        """
        return DBSession.query(cls).filter(cls.id == _id).delete()

    # listings
    @classmethod
    def get_duplicates(cls):
        """
        Get all duplicates: C3sMember entries tagged as duplicates.

        Used in:
            membership_list, statistics_view

        Returns:
            list: list of C3sMember entries flagged as duplicates.
        """
        return DBSession.query(cls).filter(
            cls.is_duplicate == 1).all()

    @classmethod
    def get_members(cls, order_by, how_many=10, offset=0, order="asc"):
        """
        Compute a list of C3sMember items with membership accepted (Query!).

        Args:
            order_by: which column to sort on, e.g. "id"
            how_many: number of entries (Integer)
            offset: how many to omit (leave out first n; default is 0)
            order: either "asc" (ascending, **default**) or "desc" (descending)

        Raises:
            Exception: invalid value for "order_by" or "order".

        Returns:
            query: C3sMember database query
        """
        try:
            attr = getattr(cls, order_by)
            order_function = getattr(attr, order)
        except:
            raise Exception("Invalid order_by ({0}) or order value "
                            "({1})".format(order_by, order))
        _how_many = int(offset) + int(how_many)
        _offset = int(offset)
        q = DBSession.query(cls).filter(
            cls.membership_accepted == 1
        ).order_by(order_function()).slice(_offset, _how_many)
        return q

    # statistical stuff
    @classmethod
    def get_postal_codes_de(cls):
        """
        Get postal codes of C3sMember entries from germany

        Returns:
            bag (list containing duplicates): postal codes in DE"""
        all = DBSession.query(cls).filter(
            cls.country == 'DE'
        ).all()
        postal_codes_de = []
        for i in all:
            try:
                int(i.postcode)
                len(i.postcode) == 5
                postal_codes_de.append(i.postcode)
            except:
                print("exception at id {}: {}".format(
                    i.id,
                    i.postcode))
                # pass
        return postal_codes_de

    # statistical stuff

    @classmethod
    def get_number(cls):
        """
        Count number of entries in C3sMember table (by counting rows)

        Used in:
            statistics_view, membership_list, fix_database, import_export,
            some tests...

        Returns:
            Integer: number
        """
        return DBSession.query(cls).count()

    @classmethod
    def get_num_members_accepted(cls):
        """
        Count the entries that have actually been accepted as members.

        Used in:
            statistics_view, membership_list

        Returns:
            Integer: number
        """
        return DBSession.query(
            cls).filter(cls.membership_accepted == 1).count()

    @classmethod
    def get_num_non_accepted(cls):
        """
        Count the applications that have **not** been accepted as members.

        XXX TODO: how about duplicates!?

        Returns:
            Integer: number of C3sMember entries.
        """
        return DBSession.query(cls).filter(or_(
            cls.membership_accepted != 1,
            cls.membership_accepted == 0,
            cls.membership_accepted is None,
        )).count()

    @classmethod
    def get_num_mem_nat_acc(cls):
        """
        Count the *persons* that have actually been accepted as members.

        Used in:
            statistics_view

        Returns:
            Integer: number
        """
        return DBSession.query(cls).filter(
            cls.is_legalentity == 0,
            cls.membership_accepted == 1,
        ).count()

    @classmethod
    def get_num_mem_jur_acc(cls):
        """
        Count the *legal entities* that have actually been accepted as members.

        Used in:
            statistics_view

        Returns:
            Integer: number
        """
        return DBSession.query(cls).filter(
            cls.is_legalentity == 1,
            cls.membership_accepted == 1
        ).count()

    @classmethod
    def get_num_mem_norm(cls):
        """
        Count the memberships that are normal members.

        Used in:
            statistics_view

        Returns:
            Integer: number
        """
        return DBSession.query(cls).filter(
            cls.membership_accepted == 1,
            cls.membership_type == u'normal'
        ).count()

    @classmethod
    def get_num_mem_invest(cls):
        """
        Count the memberships that are investing members.

        Used in:
            statistics_view

        Returns:
            Integer: number
        """
        return DBSession.query(cls).filter(
            cls.membership_accepted == 1,
            cls.membership_type == u'investing'
        ).count()

    @classmethod
    def get_num_mem_other_features(cls):
        """
        Count the memberships that are neither normal nor investing members.

        Used in:
            statistics_view

        Returns:
            Integer: number
        """
        _foo = DBSession.query(cls).filter(
            cls.membership_accepted == 1,
            cls.membership_type != u'normal',
            cls.membership_type != u'investing'
        ).all()
        _other = {}
        for i in _foo:
            if i.membership_type in _other.keys():
                _other[i.membership_type] += 1
            else:
                _other[i.membership_type] = 1
        return len(_foo)

    # listings
    @classmethod
    def member_listing(cls, order_by, how_many=10, offset=0, order="asc"):
        """
        Compute a list of C3sMember items (Query!).

        Note:
            these are not necessarily accepted members!

        Used in:
            membership_list, import_export

        Args:
            order_by: which column to sort on, e.g. "id"
            how_many: number of entries (Integer)
            offset: how many to omit (leave out first n; default is 0)
            order: either "asc" (ascending, **default**) or "desc" (descending)

        Raises:
            Exception: invalid value for "order_by" or "order".

        Returns:
            query: C3sMember database query
        """
        try:
            attr = getattr(cls, order_by)
            order_function = getattr(attr, order)
        except:
            raise Exception("Invalid order_by ({0}) or order value "
                            "({1})".format(order_by, order))
        _how_many = int(offset) + int(how_many)
        _offset = int(offset)
        q = DBSession.query(cls).order_by(order_function())\
                                .slice(_offset, _how_many)
        return q

    @classmethod
    def get_range_ids(cls, order_by, first_id, last_id, order="asc"):
        """
        Get a list of C3sMember items by range of ids.

        Used in:
            membership_list

        Args:
            order_by: which column to sort on, e.g. "id"
            first_id: id of first entry (Integer)
            last_id: id of last entry (Integer)
            order: either "asc" (ascending, **default**) or "desc" (descending)

        Raises:
            Exception: invalid value for "order_by" or "order".

        Returns:
            list: C3sMembership objects
        """
        try:
            attr = getattr(cls, order_by)
            order_function = getattr(attr, order)
        except:
            raise Exception("Invalid order_by ({0}) or order value "
                            "({1})".format(order_by, order))
        q = DBSession.query(cls).filter(
            and_(
                cls.id >= first_id,
                cls.id <= last_id,
            )
        ).order_by(order_function()).all()
        return q

    @classmethod
    def nonmember_listing(cls, order_by, how_many, offset=0, order="asc"):
        """
        Compute a list of C3sMember items which are **not** accepted members.
        Note:
            these are not necessarily accepted members!

        Used in:
            accountants_views

        Args:
            order_by: which column to sort on, e.g. "id"
            how_many: number of entries (Integer)
            offset: how many to omit (leave out first n; default is 0)
            order: either "asc" (ascending, **default**) or "desc" (descending)

        Raises:
            Exception: invalid value for "order_by" or "order".

        Returns:
            list of C3sMembership objects
        """
        try:
            attr = getattr(cls, order_by)
            order_function = getattr(attr, order)
        except:
            raise Exception("Invalid order_by ({0}) or order value "
                            "({1})".format(order_by, order))
        _how_many = int(offset) + int(how_many)
        _offset = int(offset)
        q = DBSession.query(cls).filter(
            or_(
                cls.membership_accepted == 0,
                cls.membership_accepted == '',
                cls.membership_accepted == None,  # noqa
            )
        ).order_by(
            order_function()
        ).slice(_offset, _how_many)
        return q.all()

    @classmethod
    def nonmember_listing_count(cls):
        q = DBSession.query(cls).filter(
            or_(
                cls.membership_accepted == 0,
                cls.membership_accepted == '',
                cls.membership_accepted == None,  # noqa
            )
        ).count()
        return q

    # count for statistics
    @classmethod
    def afm_num_shares_unpaid(cls):
        all = DBSession.query(cls).all()
        num_shares_unpaid = 0
        for item in all:
            if not item.payment_received:
                num_shares_unpaid += item.num_shares
        return num_shares_unpaid

    @classmethod
    def afm_num_shares_paid(cls):
        all = DBSession.query(cls).all()
        num_shares_paid = 0
        for item in all:
            if item.payment_received:
                num_shares_paid += item.num_shares
        return num_shares_paid

    # workflow: need approval by the board
    @classmethod
    def afms_ready_for_approval(cls):
        return DBSession.query(cls).filter(
            and_(
                (cls.membership_accepted == 0),
                (cls.signature_received),
                (cls.payment_received),
            )).all()

    # autocomplete
    @classmethod
    def get_matching_codes(cls, prefix):
        """
        Return only codes matching the prefix.

        This is used in the autocomplete form to search for C3sMember entries.

        Returns:
            list of strings
        """
        all = DBSession.query(cls).all()
        codes = []
        for item in all:
            if item.email_confirm_code.startswith(prefix):
                codes.append(item.email_confirm_code)
        return codes

    @classmethod
    def check_password(cls, _id, password):
        """
        Check a password against the database.

        Args:
            _id: C3sMember entry id.
            password: a password supplied

        Returns:
            the answer of bcrypt.crypt, comparing the password supplied
                and the hash from the database
        """
        member = cls.get_by_id(_id)
        return crypt.check(member.password, password)

    # this one is used by RequestWithUserAttribute
    @classmethod
    def check_user_or_None(cls, _id):
        """
        Check whether a user by that username exists in the database.

        Used in:
            security.request.RequestWithUserAttribute

        Args:
            _id: id of C3sMember entry.
        Returns:
            object, if id exists, else None.
            None: if id
        """
        login = cls.get_by_id(_id)  # is None if user not exists
        return login

    # for merge comparisons
    @classmethod
    def get_same_lastnames(cls, name):  # XXX todo: similar
        """return list of accepted members with same lastnames"""
        return DBSession.query(cls).filter(
            and_(
                cls.membership_accepted == 1,
                cls.lastname == name
            )).all()

    @classmethod
    def get_same_firstnames(cls, name):  # XXX todo: similar
        """return list of accepted members with same fistnames"""
        return DBSession.query(cls).filter(
            and_(
                cls.membership_accepted == 1,
                cls.firstname == name
            )).all()

    @classmethod
    def get_same_email(cls, mail):  # XXX todo: similar
        """return list of accepted members with same email"""
        return DBSession.query(cls).filter(
            and_(
                cls.membership_accepted == 1,
                cls.email == mail,
            )).all()

    @classmethod
    def get_same_date_of_birth(cls, dob):  # XXX todo: similar
        """return list of accepted members with same date of birth"""
        return DBSession.query(cls).filter(
            and_(
                cls.membership_accepted == 1,
                cls.date_of_birth == dob,
            )).all()

    # membership numbers etc.
    @classmethod
    def get_num_membership_numbers(cls):
        """
        count the number of membership numbers
        """
        return DBSession.query(cls).filter(cls.membership_number).count()

    @classmethod
    def get_next_free_membership_number(cls):
        """
        returns the next free membership number
        """
        return C3sMember.get_highest_membership_number()+1

    @classmethod
    def get_highest_membership_number(cls):
        """
        get the highest membership number
        """
        nrs = DBSession.query(cls.membership_number).filter(
            cls.membership_number != None).all()  # noqa
        _list = []
        for i in nrs:
            _list.append(int(i[0]))
        try:
            _max = max(_list)
        except:
            _list = [0, 999999999]
            _max = 999999999
        try:
            assert(_max == 999999999)
            _list.remove(max(_list))  # remove known maximum
        except:
            pass
        return max(_list)

    # countries
    @classmethod
    def get_num_countries(cls):
        """return number of countries in DB"""
        _list = []
        _all = DBSession.query(cls)
        for item in _all:
            if item.country not in _list:
                _list.append(item.country)
        return len(_list)

    @classmethod
    def get_countries_list(cls):
        """return dict of countries and number of occurrences"""
        _c_dict = {}
        _all = DBSession.query(cls)
        for item in _all:
            if item.country not in _c_dict.keys():
                _c_dict[item.country] = 1
            else:
                _c_dict[item.country] += 1
        return _c_dict

    # autocomplete
    @classmethod
    def get_matching_people(cls, prefix):
        """
        return only entries matchint the prefix
        """
        all = DBSession.query(cls).all()
        names = {}
        for item in all:
            if item.lastname.startswith(prefix):
                _key = (
                    item.email_confirm_code + ' ' +
                    item.lastname + ', ' + item.firstname)
                names[_key] = _key
        return names

    def set_dues15_payment(self, paid_amount, paid_date):
        if math.isnan(self.dues15_amount_paid):
            dues15_amount_paid = Decimal('0')
        else:
            dues15_amount_paid = self.dues15_amount_paid

        self.dues15_paid = True
        self.dues15_amount_paid = dues15_amount_paid + paid_amount
        self.dues15_paid_date = paid_date
        self.dues15_balance = self.dues15_balance - paid_amount

    def set_dues15_amount(self, dues_amount):
        if math.isnan(self.dues15_amount):
            dues15_amount = Decimal('0')
        else:
            dues15_amount = self.dues15_amount

        self.dues15_balance = self.dues15_balance - dues15_amount + Decimal(
            dues_amount)  # what they actually have to pay
        self.dues15_amount = dues_amount  # what they have to pay (calc'ed)

    def set_dues15_reduced_amount(self, reduced_amount):
        if reduced_amount != self.dues15_amount:
            previous_amount_in_balance = (
                self.dues15_amount_reduced
                if self.dues15_reduced
                else self.dues15_amount)
            self.dues15_balance = self.dues15_balance - \
                previous_amount_in_balance + reduced_amount
            self.dues15_amount_reduced = reduced_amount
        else:
            self.dues15_amount_reduced = Decimal('NaN')

    def get_url_safe_name(self):
        return re.sub(  # # replace characters
            '[^0-9a-zA-Z]',  # other than these
            '-',  # with a -
            self.lastname if self.is_legalentity else (
                self.lastname + self.firstname))


class Dues15Invoice(Base):
    """
    This table stores the invoices for the 2015 version of dues.

    We need this for bookkeeping,
    because whenever a member is granted a reduction of her dues,
    the old invoice is canceled by a reversal invoice
    and a new invoice must be issued.

    Edge case: if reduced to 0, no new invoice needed.

    """
    __tablename__ = 'dues15invoices'
    id = Column(Integer, primary_key=True)
    """tech. id. / no. in table (integer, primary key)"""
    # this invoice
    invoice_no = Column(Integer(), unique=True)
    """invoice number (Integer, unique)"""
    invoice_no_string = Column(Unicode(255), unique=True)
    """invoice number string (unique)"""
    invoice_date = Column(DateTime())
    """timestamp of invoice creation (DateTime)"""
    invoice_amount = Column(DatabaseDecimal(12, 2), default=Decimal('NaN'))
    """amount (DatabaseDecimal(12,2))"""
    # has it been superseeded by reversal?
    is_cancelled = Column(Boolean, default=False)
    """flag: invoice has been superseeded by reversal or cancellation"""
    cancelled_date = Column(DateTime())
    """timestamp of cancellation/reversal"""
    # is it a reversal?
    is_reversal = Column(Boolean, default=False)
    """flag: is this a reversal invoice?"""
    # is it a reduction (or even more than default)?
    is_altered = Column(Boolean, default=False)
    """flag: has the amount been reduced or increased?"""
    # person reference
    member_id = Column(Integer())
    """reference to C3sMember id"""
    membership_no = Column(Integer())
    """reference to C3sMember membership_number"""
    email = Column(Unicode(255))
    """C3sMembers email we sent this invoice to"""
    token = Column(Unicode(255))
    """used to limit access to this invoice"""
    # referrals
    preceding_invoice_no = Column(Integer(), default=None)
    """the invoice number preceeding this one, if applicable"""
    succeeding_invoice_no = Column(Integer(), default=None)
    """the invoice number succeeding this one, if applicable"""

    def __init__(self,
                 invoice_no,
                 invoice_no_string,
                 invoice_date,
                 invoice_amount,
                 member_id,
                 membership_no,
                 email,
                 token,
                 ):
        """
        Make a new invoice object

        Args:
            invoice_no: invoice number
            invoice_no_string: invoice number string
            invoice_date: timestamp of creation
            invoice_amount: amount of money
            member_id: references C3sMember
            membership_no: references C3sMember
            email: email to send it to
            token: a token to limit access
        """
        self.invoice_no = invoice_no
        self.invoice_no_string = invoice_no_string
        self.invoice_date = invoice_date
        self.invoice_amount = invoice_amount
        self.member_id = member_id
        self.membership_no = membership_no
        self.email = email
        self.token = token

    @classmethod
    def get_all(cls):
        """
        Return all dues15 invoices
        """
        return DBSession.query(cls).all()

    @classmethod
    def get_by_invoice_no(cls, _no):
        """return one invoice by invoice number"""
        return DBSession.query(cls).filter(cls.invoice_no == _no).first()

    @classmethod
    def get_by_membership_no(cls, _no):
        """return all invoices of one member by membership number"""
        return DBSession.query(cls).filter(cls.membership_no == _no).all()

    @classmethod
    def get_max_invoice_no(cls):
        """
        Get the maximum invoice number.

        Returns:
            * Integer: maximum of given invoice numbers or 0"""
        res, = DBSession.query(func.max(cls.id)).first()

        if res is None:
            return 0
        return res

    @classmethod
    def check_for_existing_dues15_token(cls, dues_token):
        """
        Check if a dues token is already present.

        Args:
            dues_token: a given string

        Returns:
            * **True**, if token already in table
            * **False** else
        """
        check = DBSession.query(cls).filter(
            cls.token == dues_token).first()
        if check:  # pragma: no cover
            return True
        else:
            return False

    @classmethod
    def get_monthly_stats(cls):
        """
        Gets the monthly statistics.

        Provides sums of the normale as well as reversal invoices per
        calendar month based on the invoice date.
        """
        result = []
        # SQLite specific: substring for SQLite as it does not support
        # date_trunc.
        # invoice_date_month = func.date_trunc(
        #     'month',
        #     Dues15Invoice.invoice_date)
        invoice_date_month = func.substr(Dues15Invoice.invoice_date, 1, 7)
        payment_date_month = func.substr(C3sMember.dues15_paid_date, 1, 7)

        # collect the invoice amounts per month
        invoice_amounts_query = DBSession.query(
            invoice_date_month.label('month'),
            func.sum(expression.case(
                [(
                    expression.not_(Dues15Invoice.is_reversal),
                    Dues15Invoice.invoice_amount)],
                else_=Decimal('0.0'))).label('amount_invoiced_normal'),
            func.sum(expression.case(
                [(
                    Dues15Invoice.is_reversal,
                    Dues15Invoice.invoice_amount)],
                else_=Decimal('0.0'))).label('amount_invoiced_reversal'),
            expression.literal_column(
                '\'0.0\'', SqliteDecimal).label('amount_paid')
        ).group_by(invoice_date_month)
        # collect the payments per month
        member_payments_query = DBSession.query(
            payment_date_month.label('month'),
            expression.literal_column(
                '\'0.0\'', SqliteDecimal).label('amount_invoiced_normal'),
            expression.literal_column(
                '\'0.0\'', SqliteDecimal
            ).label('amount_invoiced_reversal'),
            func.sum(C3sMember.dues15_amount_paid).label('amount_paid')
        ).filter(C3sMember.dues15_paid_date.isnot(None)) \
            .group_by(payment_date_month)
        # union invoice amounts and payments
        union_all_query = expression.union_all(
            member_payments_query, invoice_amounts_query)
        # aggregate invoice amounts and payments by month
        result_query = DBSession.query(
            union_all_query.c.month.label('month'),
            func.sum(union_all_query.c.amount_invoiced_normal).label(
                'amount_invoiced_normal'),
            func.sum(union_all_query.c.amount_invoiced_reversal).label(
                'amount_invoiced_reversal'),
            func.sum(union_all_query.c.amount_paid).label('amount_paid')
        ) \
            .group_by(union_all_query.c.month) \
            .order_by(union_all_query.c.month)
        for month_stat in result_query.all():
            result.append(
                {
                    'month': datetime(
                        int(month_stat[0][0:4]),
                        int(month_stat[0][5:7]),
                        1),
                    'amount_invoiced_normal': month_stat[1],
                    'amount_invoiced_reversal': month_stat[2],
                    'amount_paid': month_stat[3]
                })
        return result
