######
Design
######


This chapter focuses on the design of the C3S Membership Administration
(c3sMembership).



==========
Data Model
==========


The data model is the basis of the application. It describes all data
entities, their properties and relations. Abstraction and reusability are two
of the major requirements the design aims to fufill.

The package diagram of the data model:

.. uml::
   :caption: The UML package diagram of the data model.

   package Data {
       ' package Utilities
       package Users
       ' Utilities <.. Users
       package Membership
       Users <.. Membership
       package MembershipProcesses
       Membership <.. MembershipProcesses
       package Accounting
       package Shares
       Membership <.. Shares
       package Invoicing
       package Dues
       Invoicing <.. Dues
       Accounting <.. Dues
       Membership <.. Dues
   }


.. ---------
.. Utilities
.. ---------
..
..
.. The Utilities package contains data entities which are used for providing
.. services.
..
.. AccessToken attributes:
..
.. ============== ========= =====================================================
.. Attribute name Data type Description
.. ============== ========= =====================================================
.. id             Integer   (Primary key) Technical id of the data record
.. token          String    A randomly generated character string
.. creation       Timestamp The time of creation of the token from which on it is
..                          valid
.. expiration     Timestamp The time of expiration of the token until which it is
..                          valid
.. ============== ========= =====================================================
..
.. .. uml::
..
..    package Utilities {
..        class AccessToken {
..            id
..            token
..            creation
..            expiration
..        }
..    }



-----
Users
-----


The Users package defines the basic data entities for the application's user
management. The class User stores the necessary information for providing
access to the application. User groups are used for granting permissions on
certain functions of the application.

UserGroup attributes:

============== ========= =====================================================
Attribute name Data type Description
============== ========= =====================================================
id             Integer   (Primary key) The technical id of the data record.
name           String    The name of the user group.
============== ========= =====================================================

User attributes:

==================== ========= ===============================================
Attribute name       Data type Description
==================== ========= ===============================================
id                   Integer   (Primary key) The technical id of the data
                               record.
email_address        String    (Business key) The email address of the user
                               which also functions as a account identifier.
password_hash        String    The salted hash of the password for
                               identification.
registration         Timestamp The timestamp of the registration.
last_password_change Timestamp The timestamp of the last password change.
==================== ========= ===============================================

.. uml::
   :caption: UML class diagram of the Users package.

   package Users {

       class UserGroup {
           id
           name
       }

       class User {
           id
           email_address
           password_hash
           registration
           last_password_change
       }

       UserGroup "*" -- "*" User

       ' class EmailAddressConfirmationAccessToken {
       '     member_id
       ' }

       ' AccessToken <|-- EmailAddressConfirmationAccessToken
       ' Member "1" <-- "*" EmailAddressConfirmationAccessToken
      }



----------
Membership
----------


The Membership package stores member specific information which is necessary
for the membership list and basic administrative purposes. Two types of
members exists which are natural persons and legal bodies. Both have different
attributes.

Member attributes:

================= ========= ==================================================
Attribute name    Data type Description
================= ========= ==================================================
id                Integer   (Primary key) Technical id of the data record.
address_line_1    String    First address line of the postal address.
address_line_2    String    Second address line of the postal address.
postal_code       String    Postal code of the postal address.
city              String    City of the postal address.
country           String    Country of the postal address.
locale            String    Language which the member prefers to communicate
                            in.
status            String    Possible values:
                            
                            - "applied": the member applied for membership
                            - "admitted": the membership was admitted
                            - "given_notice": the member gave notice to resign
                              from membership
                            - "resigned": the membership status turns to
                              resigned after the notice period ends
                            - "excluded": The member was excluded
                            - "died": The natural person member died
                            - "liquidated": The legal body member was
                              liquidated
                            - "rejected": The member applied for membership
                              but was rejected
                            - "withdrawn": The member applied for membership
                              but withdrew the application before it was
                              admitted
                            
type              String    Possible values:
                            
                            - "normal": The member is a normal member  with
                              full right.
                            - "investing": The member is an investor (non-
                              user) member.
                            
membership_number String    (Business key) Membership number of the member.
================= ========= ==================================================

NaturalPersonMember attributes:

=================== ========= ================================================
Attribute name      Data type Description
=================== ========= ================================================
first_name          String    The given name of the member.
last_name           String    The family name of the member.
title               String    The title of the member.
date_of_birth       Date      The date of birth of the  member.
is_member_of_colsoc Boolean   Indicates whether the member is member of at
                              least one other collecting society.
name_of_colsoc      String    The names of the other collecting societies the
                              member is a member of.
=================== ========= ================================================

LegalBodyMember attributes:

=================== ========= ================================================
Attribute name      Data type Description
=================== ========= ================================================
name                String    The name of the legal body.
court_of_law        String    The court of law which registered the legal
                              body.
registration_number String    The registration number of the legal body at the
                              court of law.
=================== ========= ================================================

The following figure shows the UML class diagram of the Membership package:

.. uml::
   :caption: UML class diagram of the Membership package.

   package Users {
       class User
   }

   package Membership {

       class Member {
           id
           address_line_1
           address_line_2
           postal_code
           city
           country
           locale
           status
           ' applied, admitted, given_notice, resigned, excluded, died_or_liquidated, rejected, withdrawn
           type
           ' normal, investing
           number
       }

       User <|-- Member

       class NaturalPersonMember {
           first_name
           last_name
           title
           date_of_birth
           is_member_of_colsoc
           name_of_colsoc
       }

       Member <|-- NaturalPersonMember

       class LegalBodyMember {
           name
           court_of_law
           registration_number
       }

       Member <|-- LegalBodyMember
   }



------
Shares
------


Each member must buy at least one share which the C3S issues. Members can also
transfer shares between each other and they can restitute them. Shares
therefore only exist in terms of transfers. They come to existence when the
C3S issues them and cease to exist when they are restituted.

Thus, shares can be viewed from a bookkeeping perspective as something which
is moved form one cooperative entity to another, i.e. from the cooperative to
a member, between members of from a member back to the cooperative.

The share transaction is the data entity representing such a transfer of
shares. It currently consists of exactly two splits, each for each cooperative
entity which either gives or receives the shares. A share is received when the
quantity is positive and given when it is negative. The quantity sum of each
share transaction must always be zero. The current quantity a cooperative
entity possesses is the sum of the quantity of all its splits.

ShareTransaction:

================= ========= ==================================================
Attribute name    Data type Description
================= ========= ==================================================
id                Integer   (Primary key) Technical id of the data record.
requested         Timestamp The time when the share transfer was requested,
                            e.g. for issuing share the time of the
                            membership application.
valued            Timestamp The time when the share transfer was valued, i.e.
                            when it became effective.
booked            Timestamp The time when the share transfer was booked into
                            the system.
type              String    The type of the shares transfer. Possible values:

                            - "acquisition": The member acquires shares from
                              the C3S which issues them.
                            - "transfer": Shares are transferred between
                              members.
                            - "restitution": The member returns shares to the
                              C3S.
================= ========= ==================================================

ShareTransactionSplit:

==================== ========= ===============================================
Attribute name       Data type Description
==================== ========= ===============================================
id                   Integer   (Primary key) Technical id of the data record.
share_transaction_id Integer   (Foreign Key, ShareTransaction.id) The
                               technical id of the share transaction to which
                               the split belongs.
member_id            Integer   (Foreign key, Member.id) The technical id of
                               the member which is affected by the shares
                               transfer.
quantity             Decimal   The quantity of shares which are transferred.
                               A positive quantity implies a gain and a
                               negative quantity the loss of shares. The
                               quantity sum of all splits must always be zero.
==================== ========= ===============================================


.. uml::
   :caption: UML class diagram of the Shares package.
   
   package Membership {
       class Member
   }
   package Shares {

       class ShareTransaction {
           id
           request_timestamp
           value_timestamp
           booking_timestamp
           type
       }

       class ShareTransactionSplit {
           id
           share_transaction_id
           member_id
           quantity
       }

       ShareTransaction "1" <-- "2" ShareTransactionSplit
       Member "1" <-- "*" ShareTransactionSplit
   }

Example:

ShareTransaction:

== ========== =========== ========== ===========
id requested  valued      booked     type
== ========== =========== ========== ===========
1  2015-09-20 2015-09-26  2015-09-21 acquisition
2  2015-09-21 2015-09-26  2015-09-21 acquisition
3  2015-09-25 2015-09-26  2015-09-30 transfer   
4  2015-09-27 2015-09-27  2015-09-30 restitution
== ========== =========== ========== ===========

ShareTransactionSplit:

== ==================== ======= ========
id share_transaction_id member  quantity
== ==================== ======= ========
1  1                    Member1 +10.0
2  1                    C3S     -10.0
3  2                    Member2 +20.0
4  2                    C3S     -20.0
5  3                    Member1 -10.0
6  3                    Member2 +10.0
7  4                    Member2 -30.0
8  4                    C3S     +30.0
== ==================== ======= ========

For simplification the member_id attribute is replaced by a member attribute
in this example.

With share_transaction_id 1 10 shares are issued from the C3S and acquired by
Member1. In the following share_transaction_id 2 C3S issues 20 shares to
Member2. The transfer of 10 shares of Member1 to Member2 is booked with
share_transaction_id 3 and finally in share_transaction_id 4 Member2
restitutes all by then 30 shares in its possession to the C3S.


--------------------
Membership Processes
--------------------


The Membership Processes package stores all information which is related to
the business processes regarding the membership. This information is kept
separate from the basic member information of the Membership package because
it depends solely on the processes and not on the member attributes which must
be recorded for the membership list.

.. uml::
   :caption: UML class diagram of the Membership Processes package.

   package Membership {
       class Member
   }
   package MembershipProcesses {
       class MembershipStatusChange {
           id
           member_id
       }

       Member "1" <-- "*" MembershipStatusChange

       class MembershipApplication {
           id
           share_transaction_id
           phase
           ' TODO: applied, admitted, rejected, withdrawn
           ' Wie können Datumswerte für rejected und withdrawn konsistent dargestellt werden?
           ' Normalisierung nötig?
           application_date
           signature_received_date
           signature_confirmed_date,
           ' payment_received_date
           ' payment_confirmed_date
           decision_date

           ' TODO: Eigentlich müsste für MembershipApplication eine Rechnung
           ' ausgestellt und zu dieser ein Zahlungseingang verbucht werden.
       }

       MembershipStatusChange <|-- MembershipApplication

       class MembershipResignation {
           id
           notice_date
           notice_period_end_date
           effective_date
           withdraw_date

           ' TODO: Wird für die Rückerstattung der Anteilsgebühr ein Beleg
           ' ausgestellt, ähnlich einer Storno-Rechnung? Dieser könnte mit der
           ' Kündigung verknüpft werden und es könnte einen Zahlungsvorgang
           ' dazu im Accounting geben.

       }

       MembershipStatusChange <|-- MembershipResignation

       class MembershipExclusion {
           id
           decision_date
           ' TODO: Eigenschaften mit rechtlichen Voraussetzungen abgleichen.
       }

       MembershipStatusChange <|-- MembershipExclusion

       ' TODO: death, liquidation
   }



.. -----------------------
.. Membership Certificates
.. -----------------------
..
..
.. .. uml::
..    :caption: UML class diagram of the Membership Certificates package.
..
..     package Utilities {
..        class AccessToken
..    }
..    package Membership {
..        class Member
..    }
..    package MembershipCertificates {
..        class MemberCertificateAccessToken {
..            member_id
..        }
..        AccessToken <|-- MemberCertificateAccessToken
..        Member "1" <-- "*" MemberCertificateAccessToken
..    }



----------
Accounting
----------


.. uml::
   :caption: UML class diagram of the Accounting package.

   package Accounting {
       class Account {
           id
           name
       }

       class AccountTransaction {
           id
           description
       }

       class AccountTransactionSplit {
           id
           transaction_id
           account_id
       }

       Account "1" <-- "*" AccountTransactionSplit
       AccountTransaction "1" <-- "*" AccountTransactionSplit
   }



---------
Invoicing
---------


Invoices are modeled as a general concept independently from any special
purpose.

Invoice attributes:

============== ========= =====================================================
Attribute name Data type Description
============== ========= =====================================================
id             Integer   (Primary key) Technical id of the data record.
number         String    (Business key) The invoice number which uniquely
                         identifies the invoice.
invoice_date   Date      The date at which the invoice was issued.
due_date       Date      The date at which the invoiced amount is due.
type           String    The type of the invoice:

                         - "normal": A normal invoice.
                         - "cancellation": This invoice cancels another
                           invoice
============== ========= =====================================================

InvoicePosition attributes:

============== ========= =====================================================
Attribute name Data type Description
============== ========= =====================================================
id             Integer   (Primary key) Technical id of the data record.
invoice_id     Integer   (Foreign key, Invoice.id) Reference of the invoice
                         this position belongs to.
number         Integer   (Business key) The number of the invoice position
                         which identifies the position uniquely within the
                         invoice.
name           String    The name of the invoice position which is displayed
                         on the invoice.
unit_price     Decimal   The unit price of the invoice position.
currency       String    ISO 4217 currency code, e.g. EUR, USD, SEK, NOK, DKK,
                         CHF.
quantity       Decimal   The quantity of the invoice position.
type           String    The type of the invoice position.
description    String    The description of the invoice position which
                         provides details on the position name.
============== ========= =====================================================

InvoiceCancellation attributes:

======================= ========= ============================================
Attribute name          Data type Description
======================= ========= ============================================
id                      Integer   (Primary key) Technical id of the data
                                  record.
invoice_id              Integer   (Foreign key, Invoice.id) Identifies the
                                  invoice which is being cancelled by the
                                  other invoice.
cancellation_invoice_id Integer   (Foreign key, Invoice.id) Identifies the
                                  invoice which cancels the original invoice.
======================= ========= ============================================

.. uml::
   :caption: UML class diagram of the Invoicing package.

   ' package Utilities {
   '     class AccessToken
   ' }
   package Accounting {
       class AccountTransaction
   }
   package Invoicing {
       class Invoice {
           id
           number
           invoice_date
           due_date
           type
       }

       class InvoicePosition {
           id
           invoice_id
           number
           name
           unit_price
           currency
           quantity
           type
           description

           ' TODO: Eigentlich reicht es nicht, wenn hier Accounts referenziert
           ' werden, es müssen Buchungen auf einen Account referenziert werden.
           ' Pro Posten muss automatisch eine Buchung auf ein Konto erfolgen.
       }

       Invoice "1" <--"1..*" InvoicePosition
       AccountTransaction "1" <-- "*" InvoicePosition

       class InvoiceCancellation {
           id
           invoice_id
           cancellation_invoice_id
       }

       Invoice "1" <-- "1" InvoiceCancellation : invoice
       Invoice "1" <-- "1" InvoiceCancellation : cancellation_invoice

       ' class InvoiceAccessToken {
       '     invoice_id
       ' }

       ' Invoice "1" <-- "*" InvoiceAccessToken
       ' AccessToken <|-- InvoiceAccessToken
   }



----
Dues
----


Dues attributes:

============== ========= =====================================================
Attribute name Data type Description
============== ========= =====================================================
id             Integer   (Primary key) Technical id of the data record
name           String    The name of the dues, e.g. "Membership dues 2015"
description    String    Detailed explanation of the dues
============== ========= =====================================================

DuesInvoice attributes (inherits Invoicing.Invoice):

============== ========= =====================================================
Attribute name Data type Description
============== ========= =====================================================
id             Integer   (Primary key) Technical id of the data record.
member_id      Integer   (Foreign key Member.id) The member to which the dues
                         invoice is issued.
dues_id        Integer   (Foreign key, Dues.id) The dues which defines the
                         context in which the dues invoice is issued.
============== ========= =====================================================

DuesAttribute attributes (inherits Accounting.Account):

============== ========= =====================================================
Attribute name Data type Description
============== ========= =====================================================
id             Integer   (Primary key) Technical id of the data record.
member_id      Integer   (Foreign key Member.id) The member for which the
                         account was created.
dues_id        Integer   (Foreign key, Dues.id) The dues which defines the
                         account was created.
============== ========= =====================================================

Implicitly, all account transactions for dues invoice positions are booked
with account transaction splits on dues accounts.

.. uml::
   :caption: UML class diagram of the Dues package.

   package Invoicing {
       class Invoice
       class InvoicePosition
       Invoice "1" <--"1..*" InvoicePosition
   }
   package Accounting {
       class Account
       class AccountTransaction
       Account "1" <-- "*" AccountTransactionSplit
       AccountTransaction "1" <-- "*" AccountTransactionSplit
       AccountTransaction "1" <-- "*" InvoicePosition
   }
   package Membership {
       class Member
   }
   package Dues {
       class Dues {
           id
           name
           description
       }
       class DuesInvoice {
           id
           member_id
           dues_id
       }
       Invoice <|-- DuesInvoice
       Member "1" <-- "*" DuesInvoice
       Dues "1" <-- "*" DuesInvoice

       class DuesAccount {
           id
           member_id
           dues_id
       }

       Account <|-- DuesAccount
       Dues "1" <-- "*" DuesAccount
       Member "1" <-- "*" DuesAccount
   }



========================
Environment Architecture
========================


.. uml::
   :caption: UML component diagram of the environment architecture.
   
   [Apache] --> [c3sMembership]
   [c3sMembership] --> [SQLite]
   [c3sMembership] --> [Python]



========================
Application Architecture
========================



--------
Patterns
--------


The application is (being) implemented as a layered application [MS_AAG2]_ spread across three main layers:

- Presentation layer: Provides the user frontend
- Business layer: Implements the business logic
- Data layer: Provides abstracted access to the data model

The data layer uses the repository pattern ([MF_PoEE_Rep]_, [MSDN_DP_Rep]_) to
abstract the data access.



----------
Components
----------


.. uml::
   :caption: UML package diagram of the application architecture.

   package Data {
       package SQLAlchemy
       package SQLAlchemyContinuum
       SQLAlchemyContinuum ..> SQLAlchemy
   }
   package ExternalServices {
       package GnuPG
       package Email
       package PdfTk
       package LaTeX
   }
   package Logic
   Logic ..> Data
   Logic ..> ExternalServices
   package Presentation {
       package PyramidViews
       package Pyramid
       PyramidViews ..> Pyramid
       package Deform
       PyramidViews ..> Deform
       package Colander
       PyramidViews ..> Colander
       package ChameleonTemplates
       ChameleonTemplates ..> PyramidViews
       package Bootstrap
       ChameleonTemplates ..> Bootstrap
       package jQuery
       ChameleonTemplates ..> jQuery
       package jQueryUI
       jQueryUI ..> jQuery
       ChameleonTemplates ..> jQueryUI
   }
   Presentation ..> Logic

.. uml::
   :caption: UML package diagram of the documentation.

   package Documentation {
      package Sphinx
      package Graphviz
      Sphinx ..> Graphviz
      package PlantUML
      PlantUML ..> Graphviz
      Sphinx ..> PlantUML
   }


- External services

  - GnuPG [GnuPG]_
  - Email
  - PDFtk [PDFtk]_
  - TeX Live [TeX_Live]_

- Data layer

  - SQLAlchemy ORM model [SQLAlchemy]_
  - SQLAlchemy-Continuum [SQLAlchemy-Continuum]_

- Logic layer
- Presentation layer

  - Pyramid Views [Pyramid]_
  - Chameleon Templates [Chameleon]_
  - Bootstrap [Bootstrap]_
  - jQuery [jQuery]_
  - jQueryUI [jQueryUI]_

- Documentation

  - Sphinx [Sphinx]_
  - Graphviz [Graphviz]_, [Sphinx-Graphviz]_ 
  - PlantUML [PlantUML]_


====
Todo
====


- Membership status: What happens if a former member who terminated the
  membership becomes a member again? Is the old membership number reactivated
  or is a new one assigned? This might have an impact on the data model in
  terms of keeping history and reusing member data records.

- Discount: ID, Begin date, End date, Discount type, Discount amount, Member
  ID (FK)

- Payments

  - Attributes: ID, Value (in EUR), Booking date (date when the data was
    entered into the system), Value date (date when the payment arrived, i.e.
    the cash was handed over or the payment was received on the bank
    account), Type: cash/transfer, Reference/comment (e.g. transfer purpose),
    Invoice ID (FK)

  - Can be assigned to:

    - Invoices for shares: acquisition, restitution

    - Invoices for membership fees: fee payable, discount

- Shares

  - Can be

    - acquired
    - transferred (e.g. sold)
    - restituted

  - For transfer/sale two members are involved which must be reflected in the
    data model.

  - Can have states

    - applied for and not paid yet
    - paid for but not approved yet
    - approved
    - denied but not refunded
    - refunded

  - How are wrong bookings handled? Possibility to change bookings or only to
    enter a reverse booking?

  - How to store the information when a share transfer was requested and when
    approved? It might be necessary to get statistics about how many share
    transfers are pending.

- Invoices should be sent for the acquisition and restitution. This is not
  necessarily the case at the moment.

- Email addresses might need to be abstracted. It is necessary to store
  whether an email address was confirmed. Confirmation works through the
  generation of a token which is sent to the email address. If the link
  including the token is clicked, the email address is verified. Therefore,
  the token as well as a flag about the successful verification need to be
  stored. This can happen more than once in case a password reset is
  requested. **Decision**: Email addresses are not abstracted but tokens are.
  As the old email address can be recovered from the member data history, it
  does not need a separate table. The tokens are abstracted in an own concept
  as they are not only needed for email verification but also for invoice
  as well as membership certificate access.

- Use SQLAlchemy-Continuum for keeping history where necessary.
