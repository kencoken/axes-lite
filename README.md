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
 
For convenience, a script is provided to obtain a copy of each of these
components and place them within the AXES-LITE directory:

    $ ./get_components.sh
    
Once a copy has been obtained of each of the components, the instructions
contained in their respective `README` files should be used to install them
and their dependencies.

### Linking the components together

    $ ./setup_env.sh
    $ python link.py
    $ python index.py

Usage
-----

    $ python start.py
