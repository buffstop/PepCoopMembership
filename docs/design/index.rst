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
of the main requirements the design aims to fufill.

The package diagram of the data model:

.. uml::
   :caption: The UML package diagram of the data model.

   @startuml
   package Data {
       package Users
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
   @enduml



-----
Users
-----


The Users package defines the basic data entities for the application's user
management. The class User stores only the necessary information for providing
access to the application. User groups are used for granting permissions on
certain functions of the application.

.. uml::
   :caption: UML class diagram of the Users package.

   @startuml
   package Users {

       class UserGroup {
           id
           name
       }

       class User {
           id
           email_address
           password_hash
           last_password_change
       }

       UserGroup "*" -- "*" User
       class Staff
       User <|-- Staff
   }
   @enduml



----------
Membership
----------


The Membership package contains data entities for storing member specific
information. The two types of members are natural persons and legal bodies
which require different attributes.

Member attributes:

================= ========= ==================================================
Attribute name    Data type Description
================= ========= ==================================================
id                Integer   (Primary key) Technical id of the data record
address_line_1    String    First address line of the postal address
address_line_2    String    Second address line of the postal address
postal_code       String    Postal code of the postal address
city              String    City of the postal address
country           String    Country of the postal address
locale            String    Language which the member prefers to communicate
                            in
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
first_name          String    The given name of the member
last_name           String    The family name of the member
title               String    The title of the member
date_of_birth       Date      The date of birth of the  member
is_member_of_colsoc Boolean   Indicates whether the member is member of at
                              least one other collecting society
name_of_colsoc      String    The names of the other collecting societies the
                              member is a member of
=================== ========= ================================================

LegalBodyMember attributes:

=================== ========= ================================================
Attribute name      Data type Description
=================== ========= ================================================
name                String    The name of the legal body
court_of_law        String    The court of law which registered the legal body
registration_number String    The registration number of the legal body at the
                              court of law
=================== ========= ================================================

The following figure shows the UML class diagram of the Membership package:

.. uml::
   :caption: UML class diagram of the Membership package.

   @startuml
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
   @enduml



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
shares. I consists of (for now) exactly two splits, each for each cooperative
entity which either gives or receives the shares. A share is received when the
quantity is positive and given when it is negative. The quantity sum of each
share transaction must always be zero. The current quantity a cooperative
entity possesses is the sum of the quantity of all its splits.

ShareTransaction:

================= ========= ==================================================
Attribute name    Data type Description
================= ========= ==================================================
id                Integer   (Primary key)
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
id                   Integer   (Primary key) Technical id of the data record
share_transaction_id Integer   (Foreign Key, ShareTransaction.id) The
                               technical id of the share transaction to which
                               the split belongs.
member_id            Integer   (Foreign key, Member.id) The technical id of
                               the member which is affected by the shares
                               transfer
quantity             Decimal   The quantity of shares which are transferred.
                               A positive quantity implies a gain and a
                               negative quantity the loss of shares. The
                               quantity sum of all splits must always be zero.
==================== ========= ===============================================


.. uml::
   :caption: UML class diagram of the Shares package.
   
   @startuml
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
   @enduml

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


.. uml::
   :caption: UML class diagram of the Membership Processes package.

   @startuml
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
           phase
           ' TODO: applied, admitted, rejected, withdrawn
           ' Wie können Datumswerte für rejected und withdrawn konsistent dargestellt werden?
           ' Normalisierung nötig?
           signature_received_date
           signature_confirmed_date,
           payment_received_date
           payment_confirmed_date

           ' TODO: Eigentlich müsste für MembershipApplication eine Rechnung
           ' ausgestellt und zu dieser ein Zahlungseingang verbucht werden.
       }

       MembershipStatusChange <|-- MembershipApplication

       class MembershipResignation {
           id
           notice_date
           notice_period_end_date
           effective_date
           withdrawn_date

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
   @enduml



-----------------------
Membership Certificates
-----------------------


.. uml::
   :caption: UML class diagram of the Membership Certificates package.

   @startuml
   package Membership {
       class Member
   }
   package MembershipCertificates {
       class MemberCertificateAccessToken {
           member_id
       }
       AccessToken <|-- MemberCertificateAccessToken
       Member "1" <-- "*" MemberCertificateAccessToken
   }
   @enduml



----------
Accounting
----------


.. uml::
   :caption: UML class diagram of the Accounting package.

   @startuml
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
   @enduml



---------
Invoicing
---------


.. uml::
   :caption: UML class diagram of the Invoicing package.

   @startuml
   package Accounting {
       class AccountTransaction
   }
   package Invoicing {
       class Invoice {
           id
           number
           date
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
   }
   @enduml



----
Dues
----


.. uml::
   :caption: UML class diagram of the Dues package.

   @startuml
   package Invoicing {
       class Invoice
   }
   package Accounting {
       class Account
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
   @enduml



Discount:

- ID
- Begin date
- End date
- Discount type
- Discount amount
- Member ID (FK)

Invoice:

- ID
- Invoice number (business key)
- Creation date
- Invoice date
- Due date
- Total amount (cancellation: negative amount)
- Member ID (FK)

Invoice position:

- ID
- Description
- Amount
- Invoice ID (FK)

Payment:

- ID
- Value (in EUR)
- Booking date (date when the data was entered into the system)
- Value date (date when the payment arrived, i.e. the cash was handed over or
  the payment was received on the bank account)
- Type: cash/transfer
- Reference/comment (e.g. transfer purpose)
- Invoice ID (FK)

Membership application:

- ID
- Application date
- Decision date
- Share ID
- Application incoming date
- Payment incoming date
- Member ID (FK)

**TODO:** *Redundancy of payment incoming date if the payments are tracked in
a seperate table. Resolve.*

Membership resignation:

- ID
- Application date
- Decision date
- Member ID (FK)

Shares should be stored in a double-entry bookkeeping style. This means that
shares are always transferred. If acquired by a new member, the C3S "looses"
the amount of shares and at the same time the new member "gains" them. When
shares are sold between members, the selling member "looses" them and the
buying member "gains" them. This leads to shares being transactions between
two entities.


**Todo:**

- *Members: Should member inherit from user or could multiple users be
  associated with a user?*

- *Payments*

  - *Can be assigned to:*

    - *Invoices for shares: acquisition, restitution*

    - *Invoices for membership fees: fee payable, discount*

- *Shares*

  - *Can be acquired, transferred/sold and restituted.*
  
  - *For transfer/sale two members are involved which must be reflected in the
    data model.*
  
  - *Have different states: applied for and not paid yet, paid for but not
    approved yet, approved, denied but not refunded, refunded*

- *Invoices should be sent for the acquisition and restitution. This is not
  necessarily the case at the moment.*

- *Email addresses might need to be abstracted. It is necessary to store
  whether an email address was confirmed. Confirmation works through the
  generation of a token which is sent to the email address. If the link
  including the token is clicked, the email address is verified. Therefore,
  the token as well as a flag about the successful verification need to be
  stored. This can happen more than once in case a password reset is
  requested.*
  
- *Use SQLAlchemy-Continuum for keeping history where necessary.*


========================
Environment Architecture
========================


.. uml::
   :caption: UML component diagram of the environment architecture.
   
   @startuml
   [Apache] --> [c3sMembership]
   [c3sMembership] --> [SQLite]
   [c3sMembership] --> [Python]
   @enduml


========================
Application Architecture
========================


.. uml::
   :caption: UML package diagram of the application architecture.

   @startuml
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
   @enduml

.. uml::
   :caption: UML package diagram of the documentation.

   @startuml
   package Documentation {
      package Sphinx
      package Graphviz
      Sphinx ..> Graphviz
      package PlantUML
      PlantUML ..> Graphviz
      Sphinx ..> PlantUML
   }
   @enduml


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


**TODO**: *Elaborate on the architecture of the membership application.*

