Next Release
============


- Fix permissions for reversal invoice generation as users cannot access it.



1.11.1
======

- Fix notation of euro values and currency symbols.

- Remove unnecessary empty lines at beginning and end of email texts.

- Workaround for German character "ß" (sharp s) in LaTeX documents.

- Clarify phrasing in English membership dues emails.



1.11
====

- Introduce membership dues handling. Dues are calculated per quarter
  depending on the membership duration.

  - Invoices are generated and sent to the member. They can be canceled.

  - Membership dues can be reduced which leads to a canceling of the previous
    invoice and generation of a new one.

  - The payment can be entered with amount and date.

- Extend documentation.

  - An overview of the application is given.

  - The source code documentation auto-generated.

  - How to run the test.

  - Setup for development is descibed.

  - How to deploy the application onto an Apache server is explained.

- Invitation emails for the 2015 general assembly and barcamp.

- Cleanup code.

- Fixed minor bugs.



1.10.2
======

- Fixed jQuery path in dashboard template which was preventing the
  confirmation dialog for deleting a member to be shown. Made sure that
  a wrong jQuery path would not allow deletions without confirmation dialog
  in the future.

- Fixed usage of jQuery, jQuery UI and Bootstrap. Reorganized files and
  corrected all references.

- Fixed link to statistics of finished memberships.

- Set GPL license for c3sMembership code and CC BY 4.0 for documentation.

- Added copyright notice for c3sMembership code and documentation as well
  as redistributed works.

- Added license texts GPL and MIT for redistributed works.

- Added license texts section to documentation.

- Added list of contributors.

- Implemented redirect for member deletion based on route name.



1.10.1
======

- Removed column "BC/GV" from Application for Membership dashboard. Emails
  were sent without confirmation when clicking the button.

- Introduced version number to c3sMembership. Started with 1.10.1. The
  application has been productively used for some time (i.e. at least 1.0)
  and went through a few changes since then. Therefore, taking 1.10.0 for
  the existing version 1.10.0 seems reasonable.
