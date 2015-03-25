AXES-LITE
=========

AXES-LITE provides a working example of how to link together several
visual and multimedia search services developed as part of the
[AXES project](http://www.axes-project.eu) using the LIMAS middleware
and AXES-Home web frontend to provide a fully-working multimedia
retrieval system over any dataset of video data.

Currently the following components are supported:

 - `cpuvisor-srv` - Visual category search from the University of Oxford
 - `ueberclassifiers` - Uberclassifiers from KU Leuven

Installation Instructions
-------------------------

### Prerequisites

First, the following components must be installed:

 - `cpuvisor-srv` available at: https://github.com/kencoken/cpuvisor-srv
 - `limas` available at: https://bitbucket.org/alyr/limas
 - `axes-home` available at: https://bitbucket.org/kevinmcguinness/axes-home

Following this, `components.json` must be updated with the path of each
of the components on the system.

For convenience, a script is provided to undertake these two steps,
downloading a copy of each component and placing them within the
AXES-LITE directory, and then updating `components.json`:

    $ python get_components.py

Once a copy has been obtained of each of the components, whether using
the script or manually, the instructions in their respective `README` files
should be followed to complete their individual installation along with their
dependencies.

### Linking the components together

Now that the individual system components have been downloaded and their paths
specified in

    $ python link_components.py
    $ python index_data.py

Usage
-----

    $ python start.py
