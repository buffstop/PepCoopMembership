Next Release
=======

- Included version information into dashboard view and template. Created
  helper class GitTools to provide git information about tags, branches and
  commits.

- Code cleanup

  - accountants_view.py

  - views.py

- Integrated the deform TextInputSliderWidget so that it doesn't need
  to be applied as a text and neither the slider.pt template needs to
  be copied anywhere. This reduces manual setup steps to run the
  application.

- Changed salutation of payment reminder email body.

- Fixed several German typos like "Nachnahme" instead of "Nachname", "Email"
  instead of "E-Mail" and "Addresse" instead of "Adresse".

- Change certificate email templates from .pt to .txt as are plain
  text, therefore not compatible with .pt internationalization and causing 
  parsing errors.

- Fix several template HTML syntax errors.

- Fix setup.py which was referencing CHANGES.txt instead of CHANGES.md.

- Make the link to the Cultural Commons Manifesto language specific in order
  to show the C3S website in the corresponding language.

- Add documentation about internationalization of template and python files.



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
