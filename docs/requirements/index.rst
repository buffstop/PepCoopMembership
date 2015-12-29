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



-------------------------
Acquisition of Membership
-------------------------


The acquisition of membership must be approved by the administrative board
([EU_CR_1435_2003_SCE]_ art. 14(1)).

- Only natural persons can become full members, legal bodies can only become
  investor members ([C3S_Statute]_ § 4 I, II).

- A signed and fully filled membership application is required
  ([C3S_Statute]_ § 4 III).

- The membership application must be admitted by the administrative board
  ([C3S_Statute]_ § 4 III).

- The acquisiton of at least one share is required for becoming a member
  ([C3S_Statute]_ § 5 II 1).

- The share must be paid for acquiring membership ([C3S_Statute]_ § 5 I 2).

- A member can sign up to 60 shares ([C3S_Statute]_ § 5 II 2).

- The nominal value of one share is 50 € ([C3S_Statute]_ § 5 I 1).

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


Membership shall be lost upon resignation ([EU_CR_1435_2003_SCE]_ art. 15(1)).

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

**TODO:** *Describe the business process.*



Upon Expulsion
==============


Membership shall be lost upon expulsion where the member commits a serious
breach of his/her obligations or acts contrary to the interests of the SCE
([EU_CR_1435_2003_SCE]_ art. 15(1)).

**TODO:** *Describe the business process.*



Upon Death
==========


Membership shall be lost upon death ([EU_CR_1435_2003_SCE]_ art. 15(1), § 77
[GenG]_, § 4 IV d [C3S_Statute]_).

**TODO:** *Elaborate.*



Upon Bankrupsy
==============


Membership shall be lost upon bankrupsy ([EU_CR_1435_2003_SCE]_ art. 15(1), §
77a [GenG]_, § 4 IV d [C3S_Statute]_).

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



--------------------------------------
Invitation for Annual General Assembly
--------------------------------------


All members must be invited to the annual general assembly.

**TODO:** *Elaborate.*



--------------------------
Annual Financial Statement
--------------------------


The annual financial statement must be provided which requires statistics from
the membership list.

**TODO:** *Elaborate.*



=========
Use Cases
=========


This section describes the uses cases for this application. These use cases
are derived from the business processes as the application is used to support
them.



-------------------------
Membership Administration
-------------------------


**TODO:** *Elaborate.*



Application for membership through a web interface
==================================================


**TODO:** *Elaborate.*



Handle and approve a membership application
===========================================


**TODO:** *Elaborate.*



--------------------
Financial Accounting
--------------------


**TODO:** *Elaborate.*



Billing
=======


**TODO:** *Elaborate.*



Create an Invoice
-----------------


**TODO:** *Elaborate.*



Cancel an Invoice
-----------------


**TODO:** *Elaborate.*



Discount Invoice
----------------


**TODO:** *Elaborate.*



Payments
========


**TODO:** *Elaborate.*



Enter a Payment
---------------


**TODO:** *Elaborate.*



Enter a Partial Payment
-----------------------


**TODO:** *Elaborate.*



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



