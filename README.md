GRAPE 2.0
=========

GRAPE 2.0 provides an extensive pipeline for RNA-Seq analyses. It allows the creation of an automated and integrated workflow to manage, analyse and visualize RNA-Seq data.


License
-------

GRAPE 2.0 is release under GPL. See the LICENSE.txt file.


Documentation
-------------

The latest GRAPE 2.0 documentation can be found at:

http://grape-pipeline.rtfd.org


Installation
------------

Before installing GRAPE 2.0 some dependendencies need to be installed:

    $ pip install distribute==0.6.36 zc.buildout==2.1.0 

GRAPE 2.0 can then be installed with pip (since GRAPE 2.0 development is in beta stage you will need the `--pre` option):

    $ pip install grape-pipeline --pre

or it can be easily installed from source:

    $ git clone git://github.com/grape-pipeline/grape.git
    $ cd grape
    $ make install

The installation con be activated running the following command from the `grape` folder:

    $ source bin/activate


Development
-----------

If you want to contribute to the GRAPE 2.0 development you can get the code from github and get started:

    $ git clone git://github.com/grape-pipeline/grape.git
    $ cd grape
    $ make develop
