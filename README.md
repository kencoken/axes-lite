AXES-LITE
=========

AXES-LITE provides a working example of how to link together several
visual and multimedia search services developed as part of the
[AXES project](http://www.axes-project.eu) using the LIMAS middleware
and AXES-Home/AXES-Research web frontend to provide a fully-working
multimedia retrieval system over any dataset of video data.

Currently the following multimedia search components are supported:

 - `cpuvisor-srv` - Visual category search from the University of Oxford
 - `uberclassifiers` - Uberclassifiers from KU Leuven

Dependencies
------------

In order to run the web frontend and middleware, the following dependencies
are required:

##### 1. NGINX

NGINX is a HTTP server used to serve the frontend. You can use your own
installation, or have AXES-LITE manage a local version by downloading a copy as
follows:

    $ wget http://nginx.org/download/nginx-1.7.11.tar.gz
    $ tar xvzp -f nginx-1.7.11.tar.gz
    $ mv nginx-1.7.11 nginx
    $ cd nginx
    $ ./configure --prefix=$PWD
    $ make


##### 2. MongoDB

A MongoDB instance is used to store data in the middleware. Again, you can
use your own installation, or have AXES-LITE manage a local version by downloading
a copy as follows:

    $ wget <MONGO_URL>
    $ tar xvzp -f mongodb*tgz
    $ rm mongodb*tgz
    $ mv mongodb* mongodb

Where `<MONGO_URL>` is the appropriate MongoDB package URL for your operating
system, obtained on the [MongoDB website](https://www.mongodb.org/downloads).


Installing the AXES Components
------------------------------

First, the following components must be installed:

 - `cpuvisor-srv` available at: https://github.com/kencoken/cpuvisor-srv
 - `limas` available at: https://bitbucket.org/alyr/limas

In addition, one or both of the two available web frontends is also required:

 - `axes-home` available at: https://github.com/kevinmcguinness/axes-home
 - `axes-research` available at: https://github.com/kevinmcguinness/axes-research

**TODO: Add further details about the differences between these two interfaces here**

The location of these components, along with other configuration settings
related to AXES-LITE such as the location of the target data, are set using a
configuration file `config.json` which must exist in this directory.

A template is provided to help with the preparation of this configuration file
`config.json.template`. You can specify the paths to point to your installation
of these components anywhere on the disk - in the template all components are
set to be stored in subdirectories within this directory.

Once a `config.json` has been created, for convenience a script is provided to
download all the above components automatically if you do not already have them.
It can be run as follows:

    $ python get_components.py

Once the components have been downloaded, they must be installed and configured
as normal, following the instructions in their respective `README` files.
As AXES-LITE will handle the generation of the necessary configuration files for
each component, the procedure for each component is slightly simplified. A summary
is provided in the sections which follow:

##### 1. CPUVISOR-SRV

Only the steps outlined in the *Installation Instructions* section of the README
need to be followed. After obtaining the necessary dependencies of cpuvisor-srv
itself (for which the
[following helper package](https://bitbucket.org/kencoken/cpuvisor-srv-installer)
may be useful) this is a case of simply issuing from within the cpuvisor-srv
directory:

    $ mkdir build
    $ cd build
    $ cmake ../
    $ make
    $ make install

##### 2. LIMAS

For limas to run you only need to execute step 2 from the installation
procedure, as detailed in the README:

    $ cd limas
    $ mvn install

##### 3. AXES-Home interface

Only the dependencies for AXES-Home need to be installed manually. To install
them in a Python virtual environment, run the following commands:

    $ cd axes-home/server
    $ virtualenv venv
    $ . ./venv/bin/activate
    $ pip install -r requirements.txt

##### 4. AXES-Research interface

Only the dependencies for AXES-Research need to be installed manually, which
can be accomplished as follows:

    $ cd axes-research
    $ cp axesresearch/settings/local.py.tmpl axesresearch/settings/local.py
    $ ./bootstrap.sh

### Preparing the demo dataset

To experiment with the system, a small demo dataset consisting of two videos
is provided. It can be obtained as follows:

    $ wget http://axis.ewi.utwente.nl/collections/cAXESOpen/cAXESOpenMini.tgz
    $ tar xvzp -f cAXESOpenMini.tgz

This will create a `cAXESOpenMini` folder in the axes-lite directory. Please
specify this path both as private and as public data set in `config.json`.

Linking the Components Together
-------------------------------

Now that the individual system components have been downloaded and their paths
specified in `config.json`, we first link the systems together:

    $ python link_components.py

Then we can index for a given dataset:

    $ python index_data.py

Starting the system
-------------------

There are two methods for starting the web service once the above steps have been
completed, a simpler method useful for testing/debugging, and a more advanced
method based on the [supervisord Process Control system](http://supervisord.org).

### Quick and dirty launch

A script is provided in this directory which can be called directly with the name
of the frontend to use (either `axes-home` or `axes-lite`). For example, to
launch all components using the `axes-home` frontend:

    $ ./start.sh axes-home

Replace `axes-home` with `axes-research` in the above to launch the AXES-Research
frontend instead.

This will launch a [GNU Screen instance](http://en.wikipedia.org/wiki/GNU_Screen)
within the current shell within which all configured components will be started.

You can switch between views to see log messages from the various services by
issuing `Ctl-a n` and `Ctl-a p` within the shell. You can also detach from
the screen instance using `Ctl-a d` and reattach at a later time by issuing
`$ screen -r axes-lite` from the command prompt. The screen instance can be
killed by issuing `$ screen -S axes-lite -X quit`.

Note that this script assumes that you have launched MongoDB and NGINX services
separately on the ports specified in `config.json`. If both are being managed by
AXES-LITE (i.e. the paths specified in the components section of `config.json`
for each is valid) then you can launch these by issuing:

    $ ./start_support.sh

Alternatively, use supervisord as described below to launch these services.

### Advanced launching using supervisord

Supervisord provides a fully featured process management system which helps to
manage and control a collection of services in the background, offering advanced
functionality such as the automatic restarting of processes that crash etc.

If you do not have supervisord already, it can be installed as follows:

    $ pip install supervisor

After completing the preparation steps in the previous section, using supervisord
to launch AXES-LITE is relatively straightforward.

##### Starting the system

Note: The following assumes you are running supervisor from the axes-lite
directory. If not, add `-c /path/to/supervisord.conf` to the commands below.

Start the supervisor demon process:

    $ supervisord

If you do not already have MongoDB and NGINX running, start them with supervisorctl:

    $ supervisorctl start mongodb nginx

Start all the components:

    $ supervisorctl start components:*

And start the AXES home interface:

    $ supervisorctl start axes-home

Or you can start the AXES research interface by using `axes-research` instead
of `axes-home` in the above. You can check on the status of the system
components with the using supervisor's status command:

    $ supervisorctl status

Each of the components writes log files to the `logs` subdirectory. You should
check these log files if any component fails to start.

##### Stopping the system

Run the following to shutdown supervisor:

    $ supervisorctl shutdown

##### Starting and stopping individual components

You can restart and individual component using supervisor's restart command.
For example, to restart the AXES home user interface, run:

    $ supervisorctl restart axes-home

Components can also be stopped and started manually using the `stop` and `start`
commands.
