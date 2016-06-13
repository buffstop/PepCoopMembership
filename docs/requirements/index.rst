##########################
Requirements Specification
##########################


The requirements specification is used to track the requirements of the
existing c3sMembership application as well as new requirements for future
development.

The approach and document structure are inspired by the book "Requirements
Engineering Fundamentals" by Chris Rupp and Klaus Pohl
(English ISBN 978-1-93753-877-4, German ISBN 978-3-86490-283-3).

Authors:

- Sarah Stoffels
- Markus Lorenz, mrks@lrnz.name
- Eva Bolten
- Christoph Scheid



============
Introduction
============


The application C3S Membership Administration (c3sMembership) is used to
manage members of the C3S SCE. It focuses on the automation and support of
business processes for membership application, accounting and others.

This documents covers the following perspectives:

- Business perspective: it describes the business processes in whose context
  the application is used
- Structural perspective: specification of data structures which the
  application deals with
- Functional perspective: the workflows which the application covers
- Behavioural perspective: the use cases

Quality Criteria of the Requirements Specification:

- Unambiguousness and consistency
- Clear and well-defined structure
- Changeability and extensibility
- Completeness
- Traceability of changes



====================
Requirements Sources
====================


The requirements are gathered from stakeholders, legal regulations and
existing documentation.

Stakeholders are the users of the application:

- Financial accounting: for working with membership applications, invoices,
  payments, analyses, working with certain membership data (e.g. adresses,
  date of entry, date of cancellation), generating of legally required
  membership list (§§ 30, 31, 32 [GenG]_)
- Cooperative members: for registering, receiving information and invoices

**TODO:** *Investigate existing documentation.*



=====
Risks
=====


The C3S Membership Administration application is already in production and
being used. The introduction of changes therefore requires extensive testing
to provide a high reliability. The potential damages through a loss of data
could be disastrous.



==============
System Context
==============


The system consists of a publicly accessible part for membership application
and a restricted area for administration.

Interfaces exist for importing and exporting data.

**TODO**: *elaborate.*



==================
Business Processes
==================


Business processes are the basis of the application. They would function with
pen and paper but shall be technically supported by the application.
Therefore, this chapter describes and explains the business processes from
which use cases and the majority of business and technical requirements can be
derived. The business processes themselves are independent from the technology
which helps living them.



---------------
Membership List
---------------


The membership list must be maintained (§ 30 [GenG]_). For each member is must
contain the following attributes:

- For natural persons (§ 30 II 1 1. [GenG]_)

  - Family name,
  - Given name and
  - Postal address

- For legal bodies (§ 30 II 1 1. [GenG]_)

  - Company name and
  - Postal address

- For bodies of persons (§ 30 II 1 1. [GenG]_)

  - Either

    - Name and
    - Postal address

  - Or

    - Family names,
    - Given names and
    - Postal addresses of the members

- Number of shares (§ 30 II 1 2. [GenG]_)
- Date of acquisition of membership (§ 30 II 2 [GenG]_)
- Justifying facts of the acquisition of membership (§ 30 II 2 [GenG]_), e.g.
  decision of the administrative board
- Date of loss of membership (§ 30 II 1 3. [GenG]_)
- Justifying facts of the loss of membership (§ 30 II 2 [GenG]_), e.g.
  resignation, expulsion, death, bankruptcy

Documents which are related to the acquisition or loss of membership must be
kept for three years until the end of the year in which the loss of membership
became effective (§ 30 III [GenG]_).

Members and third parties with legitimate interest review the membership list
at the cooperative (§ 31 I 2 [GenG]_).

The register court demand a copy of the membership list (§ 32 [GenG]_).



-------------------------
Acquisition of Membership
-------------------------


The acquisition of membership must be approved by the administrative board
(art. 14(1) [EU_CR_1435_2003_SCE]_).

- Only natural persons can become full members, legal bodies can only become
  investor members (§ 4 I, II [C3S_Statute]_).

- A signed and fully filled membership application is required
  (§ 4 III [C3S_Statute]_).

- The membership application must be admitted by the administrative board
  (§ 4 III [C3S_Statute]_).

- The acquisiton of at least one share is required for becoming a member
  (§ 5 II 1 [C3S_Statute]_).

- The share must be paid for acquiring membership (§ 5 I 2 [C3S_Statute]_).

- A member can sign up to 60 shares (§ 5 II 2 [C3S_Statute]_).

- The nominal value of one share is 50 € (§ 5 I 1 [C3S_Statute]_).

**TODO:**

- *Clarification of legal rules and regulations including the C3S statue which
  motivate the process.*

- *The decision of the administrative board must be recorded on the member's
  record in the membership list.*



------------------
Loss of Membership
------------------



Upon Resignation
================


Membership shall be lost upon resignation (art. 15(1) [EU_CR_1435_2003_SCE]_).

A member can resign from the C3S membership (§ 65 I [GenG]_, § 8
[C3S_Statute]_). The following criteria must be met:

- The member must deliver a written and signed membership resignation
  statement (§ 65 II 1 [GenG]_, § 8 I 1 [C3S_Statute]_).

Implications of the membership resignation are:

- The resignation becomes effective at the end of the following fiscal year
  (§ 8 I 2 [C3S_Statute]_, § 65 II [GenG]_).
- In extraordinary situations the resignation can become effective at the end
  of the fiscal year three months after the resignation statement if the
  ordinary notice period is unreasonable in the personal and economic
  circumstances of the member (§ 65 III [GenG]_).
- All mandatory and voluntary shares are terminated when the resignation
  becomes effective (§ 8 I 3 [C3S_Statute]_).
- The reimbursement value of signed shares depends on the decision of the
  administrative board before drawing the balance sheet (§ 22 III
  [C3S_Statute]_).
- Outstanding membership fees can be subtracted from the shares' reimbursement
  value.
- The date when the membership resignation becomes effective must be recoreded
  in the membership list and the member must be notified about this event
  immediately (§ 69 [GenG]_).

**TODO:**

- *Describe the business process.*
- *§ 67a [GenG]_*



Upon Expulsion
==============


Membership shall be lost upon expulsion where the member commits a serious
breach of his/her obligations or acts contrary to the interests of the SCE
(art. 15(1) [EU_CR_1435_2003_SCE]_).

**TODO:** *Describe the business process.*



Upon Transfer of All Shares
===========================


Membership shall be lost upon the transfer of all shares held to a member or a
natural person or legal entity which has acquired membership (art. 15(1)
[EU_CR_1435_2003_SCE]_, § 4 IV c [C3S_Statute]_).

**TODO:** *Elaborate.*



Upon Winding-up
===============


Membership shall be lost upon winding-up in the case of a member that is not a
natural person (Art. 15(1) [EU_CR_1435_2003_SCE]_, § 77a [GenG]_, § 4 IV d
[C3S_Statute]_).



Upon Death
==========


Membership shall be lost upon death (art. 15(1) [EU_CR_1435_2003_SCE]_, § 77
[GenG]_, § 4 IV d [C3S_Statute]_).

**TODO:** *Elaborate.*



Upon Bankruptcy
===============


Membership shall be lost upon bankruptcy (art. 15(1) [EU_CR_1435_2003_SCE]_, §§
66a, 77a [GenG]_, § 4 IV d [C3S_Statute]_).

**TODO:** *Elaborate.*



--------------------------------
Acquisition of Additional Shares
--------------------------------


A member can acquire additional shares by application. The number of shares
must be at most 60. As one share costs 50 Euros this amounts to a maximum of
3000 Euros any member can deposit.

The payment for the additional shares needs to be received and the
administrative board needs to approve.

**TODO:** *Clarification of legal rules and regulations including the C3S
statue which motivate the process.*



------------------
Shares Termination
------------------


A member can terminate all shares except the mandatory within the same notice
period as for a membership resignation (§ 67b [GenG]_). The following criteria
must be met:

- The member must deliver a written and signed shares termination statement
  (§ 67b I 1 [GenG]_).

Implications of the shares termination are:

- The termination becomes effective at the end of the following fiscal year
  (§ 8 I 2 [C3S_Statute]_, § 65 II [GenG]_).
- In extraordinary situations the termination can become effective at the end
  of the fiscal year three months after the termination statement if the
  ordinary notice period is unreasonable in the personal and economic
  circumstances of the member (§ 65 III [GenG]_).
- The reimbursement value of signed shares depends on the decision of the
  administrative board before drawing the balance sheet (§ 22 III
  [C3S_Statute]_).
- Outstanding membership fees can be subtracted from the shares' reimbursement
  value.
- The date when the shares termination becomes effective must be recoreded
  in the membership list and the member must be notified about this event and
  the number of remaining shares immediately (§ 69 [GenG]_).

**TODO:**

- *Describe the business process.*
- *Transfer of all shares is equal to a membership resignation (§ 4 IV c
  [C3S_Statute]_)*



----------------------
Membership Certificate
----------------------


Members are provided with a membership certificate and states:

- Member information

  - Last name
  - First name
  - Postal address
  - Membership number
  - Number of signed shares
  - Membership registration date

- C3S information

  - Official C3S name
  - Address
  - Email
  - URL
  - Court of law
  - Registration number
  - Name of the chairperson of the administrative board
  - Names of executive directors
  - Images of executive directors' signatures

**TODO:** *Legal requirements? "Abschriften aus der Mitgliederliste sind dem
Mitglied hinsichtlich der ihn betreffenden Eintragungen auf Verlangen zu
erteilen." § 31 I 2 [GenG]_.*



Certificate Issuance
====================


The membership certificate must be created and sent to the member.
Certificates might be issued to a member more than once.
The certificate must contain the member's current information.

We supply the member with a URL which is valid for two weeks.
This link is sent per automated mail by request of the member to headquarters office.

The relevant documentation (generated from the code)
can be found here: :ref:`code_docs_membership_certificate`.



C3S Information Changes
=======================


All changes to the C3S information must be adjusted in the certificate
template.



--------------------------------------
Invitation for Annual General Assembly
--------------------------------------


All members must be invited to the annual general assembly.

**TODO:** *Elaborate.*



--------------------------
Annual Financial Statement
--------------------------


The annual financial statement (§ 33 I 2 [GenG]_) must be provided which
requires information about member payments such as the payment and
reimbursement of shares as well as membership fees.

**TODO:** *Elaborate.*



=========
Use Cases
=========


This section describes the uses cases for this application.
These use cases are derived from the business processes
as the application is used to support them.



-------------------------
Membership Administration
-------------------------


**TODO:** *Elaborate.*



Application for Membership Through a Web Interface
==================================================


**TODO:** *Elaborate.*



Handle and Approve a Membership Application
===========================================


**TODO:** *Elaborate.*



--------------------
Financial Accounting
--------------------


**TODO:** *Elaborate.*



Accounting
==========






Invoicing
=========


A list of all invoice must be accessible via the backend administration
interface. Furthermore, the invoices created for a member must be listed on the
members's detail page.



Create an Invoice
-----------------


Invoices are created as PDF files.

The amount of the invoice is booked on the invoicing account as well as the
invoicee's account.



Send an Invoice Email
---------------------


Sending the invoice means sending a link for a PDF download. For security
reasons the download link must contain a random token and must only be valid for
a certain time.

An invoice which was created once must never be changed. For auditing purposes
neither the database entry nor the PDF file must be changed. The PDF file must
be archived.



Resend an Invoice Email
-----------------------


The accountant must be able to resend an invoice email. The email address to
which the new invoice email is sent must be the invoicee's current email address
which might have changed since the invoice was created.

The button for resending an invoice email must be presented next to the invoice
when it is listed in the global invoices list as well as the member's detail
page. A dialog must be confirmed to resend an invoice email after pushing the
button.

The invoice link of the resent invoice email must point to the same invoice PDF
file which was sent the first time.



Cancel an Invoice
-----------------


Invoices can be cancelled. In this case a cancelation invoice is created which
reverses the cancelled invoice. An invoice email for the cancelation email must
be sent to the invoicee.



Payments
========


**TODO:** *Elaborate.*



Enter a Payment
---------------


It is possible to enter payments on member's accounts.



Membership Dues
===============


The C3S can demand a membership fee:

- The dues amount can be calculated by a formula.
- The dues calculation formula can change each year.
- Dues amounts can be reduced.
- Dues might only apply to full members and not to investing members.
- Investing members can receive a request for donation instead of an invoice.
- Membership dues can be discounted. In this case the previous dues invoice is
  cancelled and a new invoice is created with the discounted dues amount.
- There are accounts for membership dues.

The account hierarchy for membership dues is as follows.

Root/Membership Dues/[YYYY]

- Invoicing

  - Invoiced
  - Cancelled

- Payment

  - Paid
  - Refunded



=====================
Business Requirements
=====================


Categorization according to the Kano modell [Wiki_Kano]_.



---------------
Must-be Quality
---------------


- Privacy. Personally identifiable information is processed.
- Data security. Personally identifiable information is processed.
- Data integrity and consistency.
- Usability of the graphical user interface (GUI).



-----------------------
One-dimensional Quality
-----------------------


**TODO:** *Elaborate.*



--------------------
Indifference Quality
--------------------


**TODO:** *Elaborate.*



---------------
Reverse Quality
---------------


**TODO:** *Elaborate.*



Membership Administration
=========================


**TODO:** *Elaborate.*



Financial Accounting
====================


**TODO:** *Elaborate.*



======================
Technical Requirements
======================


**TODO:** *Explain what technical requirements are.*



------------------
System Environment
------------------


The c3sMembership application will operate on a linux-server. The company-wide
currently used server-systems are based on the Debian Wheezy operating system.
The application deployment will be realized via a graphical web interface,
which can be used by a common browser. Therefore, the c3sMembership
application will run on a web server. The web server to use is not prescribed
by the server system or the IT-department.



--------------------
Software Environment
--------------------


A particular software environment is not prescribed by the server system or
IT-department, but a decision, to use Python as programming language and the
Pyramid framework was already mady by the development team. This decision was
based on already existing company software, the developer team's expertise and
the focus on a maximally customizable and robust open-source environment.
Therefore [Pyramid]_ will be used as framework for the server-side development
of the graphical interfaces, web-services and application logic.



======================
Quality Requiremements
======================


- Privacy and data security for preventing unauthorized access to and
  tampering of sensible data. Priority 1.
- Reliability and data consistency supported by a proper data model. Priority
  1.
- Usability
- Scalability, extensibility, maintainability
- Performance in terms of possible large data volumes in the future
