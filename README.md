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

Following this, a `config.json` must be created with the paths of
each of the components of the system. A template is provided for this purpose
`config.json.template`, in which the location of each of the above
components should be inserted.

For convenience, a script is provided to undertake these two steps,
downloading a copy of each component and placing them within the
AXES-LITE directory, and then creating a suitable configuration file 
`config.json`:

    $ python get_components.py

Once a copy has been obtained of each of the components, whether using
the script or manually, the instructions in their respective `README` files
should be followed to complete their individual installation along with their
dependencies.

### Preparing the demo dataset

To experiment with the system, a small demo dataset consisting of two videos
is provided. It can be obtained as follows:

    $ wget http://axis.ewi.utwente.nl/collections/cAXESOpen/cAXESOpenMini.tgz
		$ tar xvzp -f cAXESOpenMini.tgz
		
This will create a `cAXESOpenMini` folder in the axes-lite directory. Please
specify this path both as private and as public data set. 

### Linking the components together

Now that the individual system components have been downloaded and their paths
specified in `config.json`, we first link the systems together:

    $ python link_components.py

**FIXME: link_components.py actually contains some preprocessing for cpuvisor-srv also (the computation of negative features)**

Then we can index for a given dataset:

    $ python index_data.py

**TODO: Add details of sample data here**

Usage
-----

    $ python start.py

### Installing NGINX

    $ wget http://nginx.org/download/nginx-1.7.11.tar.gz
		$ tar xvzp -f nginx-1.7.11.tar.gz
		$ mv nginx-1.7.11 nginx
		$ cd nginx
		$ configure --prefix=$PWD
	
		
### Start with supervisor 

    $ virtualenv vent
		$ . venv/bin/activate
		$ pip install supervisor
		$ supervisor -c supervisor.conf
		$ supervisor -c supervisor.conf start all
		
