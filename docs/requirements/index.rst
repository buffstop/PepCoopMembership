##########################
Requirements Specification
##########################

The requirements specification is used to track the requirements of the existing c3sMembership application as well as new requirements for future development.

The approach and document structure are inspired by the book "Requirements Engineering Fundamentals" by Chris Rupp and Klaus Pohl (English ISBN 978-1-93753-877-4, German ISBN 978-3-86490-283-3).

Authors:

- Sarah Stoffels
- Markus Lorenz, mrks@lrnz.name
- Eva Bolten



============
Introduction
============


The application C3S Membership Administration (c3sMembership) is used to manage members of the C3S SCE. It focuses on the automation and support of business processes for membership application, accounting and others.

This documents covers the following perspectives:

- Business perspective: it describes the business processes in whose context the application is used
- Structural perspective: specification of data structures which the application deals with
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


The requirements are gathered from stakeholders and existing documentation.

Stakeholders are the uses of the application:

- Financial accounting: for working with membership applications, invoices, payments, analyses, working with certain membership data (e.g. adresses, date of entry, date of cancellation), generating of legally required membership list [GenG_Mitgliederliste]_
- Cooperative members: for registering, receiving information and invoices

**TODO:** *Investigate existing documentation.*



=====
Risks
=====


The C3S Membership Administration application is already in production and being used. The introduction of changes therefore requires extensive testing to provide a high reliability. The potential damages through a loss of data could be disastrous.



==============
System Context
==============


The system consists of a publicly accessible part for membership application and a restricted area for administration.

Interfaces exist for importing and exporting data.

**TODO**: *elaborate.*



==================
Business Processes
==================


Business processes are the basis of the application. They would even function with pen and paper but shall be technically supported and by the application. Therefore, this chapter describes and explains the business processes from which use cases and the majority of business and technical requirements can be derived. The business processes themselves are independent from the technology which helps living them.



----------------------
Membership Application
----------------------


A signed and fully filled membership application is required. Furthermore, the payment for the shares which shall be acquired must have arrived. Then the membership can be approved or declined by the governing board. The decision of the governing board must be recorded on the member's record in the membership list.

**TODO:** *Clarification of legal rules and regulations including the C3S statue which motivate the process.*



----------------------
Membership Resignation
----------------------


A member can resign from C3S by application. Therefore, a signed application of resignation needs to be provided by the member. The membership is then terminated by the end of the following year.

**TODO:**

- *Check and reference statute*
- *Does the payback of the shares' value only depend on the financial situation?*
- *Clarification of legal rules and regulations including the C3S statue which motivate the process.*



--------------------------------
Additional Acquisition of Shares
--------------------------------


A member can acquire additional shares by application. The number of shares must be at most 30. The payment for the additional shares needs to be received and the board of directory needs to approve.

**TODO:** *Clarification of legal rules and regulations including the C3S statue which motivate the process.*



---------------------
Restitution of Shares
---------------------


**TODO:**

- *Process is unclear. Is approval of board of directory enough? When is the amount paid back?*
- *Clarification of legal rules and regulations including the C3S statue which motivate the process.*


--------------------------------------
Invitation for Annual General Assembly
--------------------------------------


All members must be invited to the annual general assembly.

**TODO:** *Elaborate.*



--------------------------
Annual Financial Statement
--------------------------


The annual financial statement must be provided which requires statistics from the membership list.



=========
Use Cases
=========


This section describes the uses cases for this application. These use cases are derived from the business processes as the application is used to support them. 



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


----------
Data model
----------


User:

- ID
- Email address
- Password hash

User-member association:

- ID
- User ID (FK)
- Member ID (FK)

Member:

- ID
- Membership number (business key)
- Family name
- Given name
- Date of birth
- Email address
- First address line
- Second address line
- Postal code
- City
- Country
- Language
- Membership type: full/investing
- Is legal entity
- Court of law
- Registration number
- Is member of other collecting society
- Collecting societies of additional membership
- Accouting comment

Membership status:

- ID
- Type: acquired/resigned/exclusion
- Date
- Member ID (FK)

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

Invoice line item:

- ID
- Description
- Amount
- Invoice ID (FK)

Payment:

- ID
- Value (in EUR)
- Booking date (date when the data was entered into the system)
- Value date (date when the payment arrived, i.e. the cash was handed over or the payment was received on the bank account)
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

**TODO:** *Redundancy of payment incoming date if the payments are tracked in a seperate table. Resolve.*

Membership resignation:

- ID
- Application date
- Decision date
- Member ID (FK)

Share:

- ID
- Member ID (FK)
- Application date
- Decision date
- Status: applied, paid, approved, denied, refunded
- Type: acquisition/emission, transfer, restitution/redemption
- Share count (negative for restitution in case of resignation and exclusion as well as transfer)


**Todo:**

- *Payments*

  - *Can be assigned to:*

    - *Invoices for shares: acquisition, restitution*

    - *Invoices for membership fees: fee payable, discount*

- *Shares*

  - *Can be acquired, transferred/sold and restituted.*
  
  - *For transfer/sale two members are involved which must be reflected in the data model.*
  
  - *Have different states: applied for and not paid yet, paid for but not approved yet, approved, denied but not refunded, refunded*

  - *Shares should be stored in a double-entry bookkeeping style. This means that shares are always transferred. If acquired by a new member, the C3S "looses" the amount of shares and at the same time the new member "gains" them. When shares are sold between members, the selling member "looses" them and the buying member "gains" them. This leads to shares being transactions between two entities.*

    *ShareTransaction:*

    == ========== =========== ===========
    ID ValueDate  BookingDate Type       
    == ========== =========== ===========
    1  2015-09-20 2015-09-26  Acquisition
    2  2015-09-21 2015-09-26  Acquisition
    3  2015-09-25 2015-09-26  Transfer   
    4  2015-09-27 2015-09-27  Restitution
    == ========== =========== ===========

    *ShareSplit:*

    ============= == ======= =====
    TransactionID ID Account Value
    ============= == ======= =====
    1             1  Member1 +10  
    1             2  C3S     -10  
    2             1  Member2 +20  
    2             2  C3S     -20  
    3             1  Member1 -10  
    3             2  Member2 +10  
    4             1  Member2 -30  
    4             2  C3S     +30  
    ============= == ======= =====

- *Invoices should be sent for the acquisition and restitution. This is not necessarily the case at the moment.*

- *Email addresses might need to be abstracted. It is necessary to store whether an email address was confirmed. Confirmation works through the generation of a token which is sent to the email address. If the link including the token is clicked, the email address is verified. Therefore, the token as well as a flag about the successful verification need to be stored. This can happen more than once in case a password reset is requested.*
  
- *Check whether the changes to a member dataset must be stored in an audit-proof way. It could also lead to privacy issues and needs to be legally clarified.*

- *Legal entities can also become members. Therefore, given name, family name and name of the company or association need to be stored somehow.*

  - *One solution would be to store all fields in the same data entity and fill the appropriate ones.*
  
  - *Another solution is to put these fields into two additional data entities and join them when necessary.*



======================
Technical Requirements
======================


**TODO:** *Explain what technical requirements are.*



------------------
System Environment
------------------


The c3sMembership application will operate on a linux-server. The company-wide currently used server-systems are based on the Debian Wheezy operating system. The application deployment will be realized via a graphical web interface, which can be used by a common browser. Therefore, the c3sMembership application will run on a web server. The web server to use is not prescribed by the server system or the IT-department.



--------------------
Software Environment
--------------------


A particular software environment is not prescribed by the server system or IT-department, but a decision, to use Python as programming language and the Pyramid framework was already mady by the development team. This decision was based on already existing company software, the developer team's expertise and the focus on a maximally customizable and robust open-source environment. Therefore [Pyramid]_ will be used as framework for the server-side development of the graphical interfaces, web-services and application logic.



======================
Quality Requiremements
======================


- Privacy and data security for preventing unauthorized access to and tampering of sensible data. Priority 1.
- Reliability and data consistency supported by a proper data model. Priority 1.
- Usability
- Scalability, extensibility, maintainability
- Performance in terms of possible large data volumes in the future



..

   The section "Open Topics" is hidden because it's currently not used. Remove ".." and indentation to use it.

   ===========
   Open Topics
   ===========



========
Glossary
========


- Advisory board (German "Beirat"): see [C3S_Statute]_ § 12 II e.

- Annual financial statement (German "Jahresabschluss"): see [C3S_Statute]_ § 22.

- Board of directors (German "Verwaltungsrat"): see [C3S_Statute]_ § 12 II b, § 17.

- Court of arbitration (German "Schiedsgericht"): see [C3S_Statute]_ § 12 II d.

- Executive directors (German "Geschäftsführende Direktoren"): see [C3S_Statute]_ § 12 II c, § 16.

- Full membership (German "Ordentliche Mitgliedschaft"): see [C3S_Statute]_ § 4 I.

- General assembly (German "Generalversammlung"): see [C3S_Statute]_ § 12 II a, § 13.

- Investing membership (German "Investierende Mitgliedschaft"): see [C3S_Statute]_ § 4 II.

- Resignation (German "Austritt"): see [C3S_Statute]_ § 8.

- Shares (German "Geschäftsanteile"): see [C3S_Statute]_ § 9.

- Statute (articles of association, German "Satzung") [C3S_Statute]_.



============
Bibliography
============


.. [C3S_Statute] C3S: Articles of Association of the Cultural Commons Collecting Society SCE (C3S). http://archive.c3s.cc/legal/C3S_en_v1.0.pdf, https://archive.c3s.cc/aktuell/legal/C3S_SCE_de.pdf.

.. [GenG_Mitgliederliste] http://www.gesetze-im-internet.de/geng/__30.html, http://www.gesetze-im-internet.de/geng/__31.html, http://www.gesetze-im-internet.de/geng/__32.html

.. [Pyramid] http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/introduction.html#pyramid-and-other-web-frameworks

.. [Wiki_Kano] Wikipedia: Kano model. https://en.wikipedia.org/w/index.php?title=Kano_model&oldid=678655771

