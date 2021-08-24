.. See LICENSE.incore for details

.. highlight:: shell

.. _quickstart:

==========
Quickstart
==========

This section is meant to serve as a quick-guide to setup UArchTest (utg). This guide
will help you setup all the required tooling for running utg on your system.


Install Python
==============

.. tabs::

   .. tab:: Ubuntu


      Ubuntu 17.10 and 18.04 by default come with python-3.6.9 which is sufficient for using riscv-config.
      
      If you are are Ubuntu 16.10 and 17.04 you can directly install python3.6 using the Universe
      repository
      
      .. code-block:: shell-session

        $ sudo apt-get install python3.6
        $ pip3 install --upgrade pip
      
      If you are using Ubuntu 14.04 or 16.04 you need to get python3.6 from a Personal Package Archive 
      (PPA)
      
      .. code-block:: shell-session

        $ sudo add-apt-repository ppa:deadsnakes/ppa
        $ sudo apt-get update
        $ sudo apt-get install python3.6 -y 
        $ pip3 install --upgrade pip
      
      You should now have 2 binaries: ``python3`` and ``pip3`` available in your $PATH. 
      You can check the versions as below
      
      .. code-block:: shell-session

        $ python3 --version
        Python 3.6.9
        $ pip3 --version
        pip 20.1 from <user-path>.local/lib/python3.6/site-packages/pip (python 3.6)

   .. tab:: CentOS7

      The CentOS 7 Linux distribution includes Python 2 by default. However, as of CentOS 7.7, Python 3 
      is available in the base package repository which can be installed using the following commands
      
      .. code-block:: shell-session

        $ sudo yum update -y
        $ sudo yum install -y python3
        $ pip3 install --upgrade pip
      
      For versions prior to 7.7 you can install python3.6 using third-party repositories, such as the 
      IUS repository
      
      .. code-block:: shell-session

        $ sudo yum update -y
        $ sudo yum install yum-utils
        $ sudo yum install https://centos7.iuscommunity.org/ius-release.rpm
        $ sudo yum install python36u
        $ pip3 install --upgrade pip
      
      You can check the versions
      
      .. code-block:: shell-session

        $ python3 --version
        Python 3.6.8
        $ pip --version
        pip 20.1 from <user-path>.local/lib/python3.6/site-packages/pip (python 3.6)

Using Virtualenv for Python 
---------------------------

Many a times users face issues in installing and managing multiple python versions. This is actually 
a major issue as many gui elements in Linux use the default python versions, in which case installing
python3.6 using the above methods might break other software. We thus advise the use of **pyenv** to
install python3.6.

For Ubuntu and CentosOS, please follow the steps here: https://github.com/pyenv/pyenv#basic-github-checkout

RHEL users can find more detailed guides for virtual-env here: https://developers.redhat.com/blog/2018/08/13/install-python3-rhel/#create-env

Once you have pyenv installed do the following to install python 3.6.0::

  $ pyenv install 3.6.0
  $ pip3 install --upgrade pip
  $ pyenv shell 3.6.0
  
You can check the version in the **same shell**::

  $ python --version
  Python 3.6.0
  $ pip --version
  pip 20.1 from <user-path>.local/lib/python3.6/site-packages/pip (python 3.6)

.. _install_utg:

Install UArchTest
=================

.. tabs:: 

   .. tab:: for Dev

     The sources for UArchTest can be downloaded from the `GitLab repo`_.
     
     You can clone the repository:
     
     .. code-block:: console
     
         $ git clone https://gitlab.com/incoresemi/micro-arch-tests.git
     
     
     Once you have a copy of the source, you can install it with:
     
     .. code-block:: console
         
         $ cd utg
         $ pip3 install --editable .
     
     .. _Gitlab repo: https://gitlab.com/incoresemi/micro-arch-tests

   .. tab:: via Git

     To install UArchTest, run this command in your terminal:
     
     .. code-block:: console
     
         $ pip3 install git+https://gitlab.com/incoresemi/micro-arch-tests.git
     
     This is the preferred method to install UArchTest, as it will always install the most recent stable release.
     
     If you don't have `pip`_ installed, this `Python installation guide`_ can guide
     you through the process.
     
     .. _pip: https://pip.pypa.io
     .. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

   .. tab:: via Pip

     .. note:: If you are using `pyenv` as mentioned above, make sure to enable that environment before
      performing the following steps.
     
     .. code-block:: bash
     
       $ pip3 install utg
     
     To update an already installed version of UArchTest to the latest version:
     
     .. code-block:: bash
     
       $ pip3 install -U utg
     
     To checkout a specific version of UArchTest:
     
     .. code-block:: bash
     
       $ pip3 install utg==1.x.x


Test UArchTest
==============

Once you have installed UArchTest you can execute ``utg --help`` to print the help routine:

.. code-block:: bash

  
  Usage: utg [OPTIONS]

  Options:
    --version                       Show the version and exit.
    -v, --verbose [info|error|debug]
                                    Set verbose level for debugging
    -cl, --clean                    clean flag is set if generated files needs
                                    to be cleaned.Presently, __pycache__, tests/
                                    folders are removed along with yapsy-plugins
    -rc, --run_config PATH          Provide a config.ini file's path. This runs
                                    utg based upon the parameters stored in the
                                    file. If not specified individual args/flags
                                    are to be passed through cli. In thecase of
                                    conflict between cli and config.ini values,
                                    config.ini values will be chosen
    -dc, --dut_config PATH          Path to the yaml file containing DUT
                                    configuration. Needed to generate/validate
                                    tests
    -md, --module_dir PATH          Absolute Path to the directory containing
                                    the python files which generate the assembly
                                    tests. Required Parameter
    -wd, --work_dir PATH            Path to the working directory where
                                    generated files will be stored.
    -af, --alias_file PATH          Path to the aliasing file containing
                                    containing BSV alias names.
    -gt, --gen_test                 gen_test flag is set if tests are to be
                                    generated. Generates ASM files and SV Files
    -vt, --val_test                 val_test flag is set if generated tests are
                                    to be validated. Validates log files & SV
                                    cover-points
    -lm, --list_modules             displays all the modules that are presently
                                    supported by the framework
    -ld, --linker_dir PATH          Path to the linkerfile.
    -t, --gen_test_list             Set this flag if a test-list.yaml is to be
                                    generated by utg.utg does not
                                    generate the test_list by default.
    -gc, --gen_cvg                  Set this flag to generate the Covergroups
    -m, --modules TEXT              Enter a list of modules as a string in a
                                    comma separated format.
                                    --module
                                    'branch_predictor, decoder'
                                    Here decoder and
                                    branch_predictor are chosen
                                    If all module
                                    are to be selected use keyword 'all'.
                                    Presently supportedmodules are:
                                    branch_predictor
    --help                          Show this message and exit.


Install RISCV-GNU Toolchain
===========================

This guide will use the 64-bit riscv-gnu tool chain to compile the architectural suite.
If you already have the 64-bit gnu-toolchain available, you can skip to the next section.

.. note:: The git clone and installation will take significant time. Please be patient. If you face
   issues with any of the following steps please refer to
   https://github.com/riscv/riscv-gnu-toolchain for further help in installation.

.. tabs::
   .. tab:: Ubuntu

     .. code-block:: bash
       
       $ sudo apt-get install autoconf automake autotools-dev curl python3 libmpc-dev \
             libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool \
             patchutils bc zlib1g-dev libexpat-dev
       $ git clone --recursive https://github.com/riscv/riscv-gnu-toolchain
       $ git clone --recursive https://github.com/riscv/riscv-opcodes.git
       $ cd riscv-gnu-toolchain
       $ ./configure --prefix=/path/to/install --with-arch=rv64gc --with-abi=ilp64d --with-cmodel=medany # for 64-bit toolchain
       $ [sudo] make # sudo is required depending on the path chosen in the previous setup
     
   .. tab:: CentosOS/RHEL
     
     .. code-block:: bash
     
       $ sudo yum install autoconf automake python3 libmpc-devel mpfr-devel gmp-devel \
             gawk  bison flex texinfo patchutils gcc gcc-c++ zlib-devel expat-devel
       $ git clone --recursive https://github.com/riscv/riscv-gnu-toolchain
       $ git clone --recursive https://github.com/riscv/riscv-opcodes.git
       $ cd riscv-gnu-toolchain
       $ ./configure --prefix=/path/to/install --with-arch=rv64gc --with-abi=ilp64d --with-cmodel=medany # for 64-bit toolchain
       $ [sudo] make # sudo is required depending on the path chosen in the previous setup

Make sure to add the path ``/path/to/install`` to your `$PATH` in the .bashrc/cshrc
With this you should now have all the following available as command line arguments::

  riscv64-unknown-elf-addr2line      riscv64-unknown-elf-elfedit
  riscv64-unknown-elf-ar             riscv64-unknown-elf-g++
  riscv64-unknown-elf-as             riscv64-unknown-elf-gcc
  riscv64-unknown-elf-c++            riscv64-unknown-elf-gcc-8.3.0
  riscv64-unknown-elf-c++filt        riscv64-unknown-elf-gcc-ar
  riscv64-unknown-elf-cpp            riscv64-unknown-elf-gcc-nm
  riscv64-unknown-elf-gcc-ranlib     riscv64-unknown-elf-gprof
  riscv64-unknown-elf-gcov           riscv64-unknown-elf-ld
  riscv64-unknown-elf-gcov-dump      riscv64-unknown-elf-ld.bfd
  riscv64-unknown-elf-gcov-tool      riscv64-unknown-elf-nm
  riscv64-unknown-elf-gdb            riscv64-unknown-elf-objcopy
  riscv64-unknown-elf-gdb-add-index  riscv64-unknown-elf-objdump
  riscv64-unknown-elf-ranlib         riscv64-unknown-elf-readelf
  riscv64-unknown-elf-run            riscv64-unknown-elf-size
  riscv64-unknown-elf-strings        riscv64-unknown-elf-strip


Change Neccesary Target Env Files
=================================

TODO 

Running UArchTest
=================

.. note:: utg is interchangeably denoted as framework in this documentation.

Once you have installed UArch-test. 

.. note:: please clone `uarch_modules <https://gitlab.com/incoresemi/uarch_modules.git>`_ within the utg directory. once cloned, checkout the dev-0.0.1 branch of uarch_modules. This module contains all the tests written for the submodules in Chromite.

Command to **generate** ASM tests 
---------------------------------

.. code-block:: bash

  $ utg -dc /path/to/dut_config.yaml/file -md /path/to/the/modules/directory -gt -v <loglevel>


- This command will create a `work` directory within the micro-arch-tests directory and create the test files within this directory. It will also create a `model_test.h` and `link.ld` file in the same directory by default.
- The generated ASM files can be located within the work directory follwing this path -> `work_dir/modules_name/test_name/test_name.S`
- This command does not generate the SV covergroup and TB files. It is required to pass the `-gc` flag to be specified in addition to `-gt`
- The log level can be chosen between `info, error` and `debug`
- `-dc` and `-md` are required parameters. 
- `-gc` and `-v` are not.


The command previously shown is minimal and uses the default work directory, default linker files among several others. All options can be found by executing the command

.. code-block:: bash

  $ utg --help

The complete command required to **generate ASM tests and covergroups** with control over several parameters is shown as follows

.. code-block:: bash

  $ utg -dc /path/to/dut_config.yaml -md /path/to/modules/directory -wd /path/to/working/directory/ \
    -ld /path/to/directory/containing/linker/files -m <modules_for_which_tests_are_to_generated> \
    -af /path/to/aliasing.yaml/file -gt -gc  \
    -v <log level>

Here,

- The `-dc` and `-md` are paths to the *dut_config.yaml* and the *modules* directory respectively. These are required for all *utg* commands

  - The *modules* directory contains the python files which will be invoked by the framework while genrating the tests. 

- The `-wd` is optional. It specifies the work directory in which the tests are to be created.
- The directory passed with `-ld` option should contain both the `model_test.h` as well as the `link.ld` files within it. If not, those files will be created in the work directory.
- The `-m` option should be a string listing all the modules for which the tests are to be generated. By default, when unsepcified, the framework assumes it to be *'all'*.
- the `-af` option should list the path to an `aliasing.yaml` file which will be used for BSV signal aliasing. This is a required parameter if you wish to generate covergroups. 
- `-gt` generates tests, `-gc` generates covergroups.
- `-v` indicates the level of the logging the user requires.


**Once you have created the tests, and have succesfully run it on RiVer Core. You can use the minimal check logs feature present in the framework.**

.. note:: it is necessary that the user enables log dumping in the river_core_dut_plugin. Details about that will be covered in the documentation of river_core.

command to **validate** the generated logs
------------------------------------------

.. code-block:: bash

  $ utg -dc /path/to/dut_config.yaml -md /path/to/modules/directory -vt -v <log level>

Here, 
- `-dc` and `-md` are required parameters. `-v` is optional
- `-vt` indicates that the framework is required to parse the logs and check it against the known cases which should have been exploited by the test.


command to **list modules**
---------------------------

.. code-block:: bash

  $ utg -dc path/to/dut_config -md /path/to/modules/directory -lm 

- This command lists all the hardware modules for which test generation is possible by looking at the directory names within the *modules* directory

command to **clean**
--------------------

.. code-block:: bash

  $ utg -md /path/to/modules/directory -dc /path/to/dut_config.yaml -cl

- `-cl` cleans the work directory as well as removes all the `__pycache__` and `.yapsy_plugin` files present within the modules directory.
