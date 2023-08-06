XS-treatment suite for SAXS/WAXS data treatment.

by
Arnaldo G. Oliveira-Filho <agolivei@if.usp.br> &
Dennys Reis <dreis@if.usp.br>

Copyright 2022 by GFCx-IF-USP

### Installation process.

This suite was developed in Phyton 3, with extensive use of its libraries. It
might run under any operating system with Python interpreter and due libraries
installed.

This installation process was developed for Linux systems, using a bash script
named installXS.sh. It checks whether the necessary Python 3 libraries are
installed, confirms the installation target directory (usually, /usr/local/lib)
and creates links for the executables in /usr/local/bin, so the scritps may be
run from any directory.

Currently there is still no installation script for Windows, but the suite
might work if all needed Python 3 libraries are available in your system. You
can download the scripts and place them in a suitable directory. The absent
libraries must be checked and installed manually.

The installation script was not tested in a MAC-OS as well. If you can do it,
please give us some feedback.

To proceed with installation, follow these steps.


1) Download the XS-treatment suite, if not done yet:

git clone https://gitlab.uspdigital.usp.br/gfcx/XS-treatment.git


2) Run

cd XS-treatment
./installXS.sh

And follow the instructions. By default, the files will be installed in
/usr/local/lib; other installation directory can be chosen along the
installation process. Links to executables will be created in
/usr/local/bin


3) Run

XS-help

if you need some general guidance for the use of the scripts.

All XS_treatment scripts begin with the XS_ prefix, so to check what is
available, just type XS_ and the TAB key so the shell shows the alternatives.


### To uninstall the suite

Run

./installXS.sh -u
