.. See LICENSE.incore for details

.. highlight:: shell

.. _quickstart:

==========
Quickstart
==========

This section is meant to serve as a quick-guide to setup UArchTest and perform a sample validation check
between ``spike`` (DUT in this case) and ``SAIL-RISCV`` (Reference model in this case). This guide
will help you setup all the required tooling for running uarch_test on your system.


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

.. _install_uarch_test:

Install UArchTest
=================

.. tabs:: 

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
     
       $ pip3 install uarch_test
     
     To update an already installed version of UArchTest to the latest version:
     
     .. code-block:: bash
     
       $ pip3 install -U uarch_test
     
     To checkout a specific version of UArchTest:
     
     .. code-block:: bash
     
       $ pip3 install uarch_test==1.x.x

   .. tab:: for Dev

     The sources for UArchTest can be downloaded from the `GitLab repo`_.
     
     You can clone the repository:
     
     .. code-block:: console
     
         $ git clone https://gitlab.com/incoresemi/micro-arch-tests.git
     
     
     Once you have a copy of the source, you can install it with:
     
     .. code-block:: console
         
         $ cd uarch_test
         $ pip3 install --editable .
     
     .. _Gitlab repo: https://gitlab.com/incoresemi/micro-arch-tests

Test UArchTest
==============

Once you have installed UArchTest you can execute ``uarch_test --help`` to print the help routine:

.. code-block:: bash

   usage: uarch_test [-h] [--version] [--verbose]
                 {coverage,gendb,setup,validateyaml,run,testlist} ...
   
   UArchTest is a framework used to run the Architectural Tests on a DUT and check
   compatibility with the RISC-V ISA
   
   optional arguments:
     --verbose             [Default=info]
     --version, -v         Print version of UArchTest being used
     -h, --help            show this help message and exit
   
   Action:
     The action to be performed by uarch_test.
   
     {coverage,gendb,setup,validateyaml,run,testlist}
                           List of actions supported by uarch_test.
       coverage            Generate Coverage Report for the given YAML spec.
       gendb               Generate Database for the standard suite.
       setup               Initiate setup for uarch_test.
       validateyaml        Validate the Input YAMLs using riscv-config.
       run                 Run the tests on DUT and reference and compare
                           signatures.
       testlist            Generate the test list for the given DUT and suite.
   Action 'coverage'
   
   	usage: uarch_test coverage [-h] [--config PATH] [--cgf PATH] [--suite PATH]
   	                       [--work-dir PATH] [--no-browser]
   	
   	optional arguments:
   	  --cgf PATH       The Path to the cgf file(s). Multiple allowed
   	  --config PATH    The Path to the config file. [Default=./config.ini]
   	  --no-browser     Do not open the browser for showing the test report.
   	  --suite PATH     The Path to the custom suite directory.
   	  --work-dir PATH  The Path to the work-dir.
   	  -h, --help       show this help message and exit
   	
   Action 'gendb'
   
   	usage: uarch_test gendb [-h] [--suite PATH] [--work-dir PATH]
   	
   	optional arguments:
   	  --suite PATH     The Path to the custom suite directory.
   	  --work-dir PATH  The Path to the work-dir.
   	  -h, --help       show this help message and exit
   	
   Action 'setup'
   
   	usage: uarch_test setup [-h] [--dutname NAME] [--refname NAME] [--work-dir PATH]
   	
   	optional arguments:
   	  --dutname NAME   Name of DUT plugin. [Default=spike]
   	  --refname NAME   Name of Reference plugin. [Default=sail_cSim]
   	  --work-dir PATH  The Path to the work-dir.
   	  -h, --help       show this help message and exit
   	
   Action 'validateyaml'
   
   	usage: uarch_test validateyaml [-h] [--config PATH] [--work-dir PATH]
   	
   	optional arguments:
   	  --config PATH    The Path to the config file. [Default=./config.ini]
   	  --work-dir PATH  The Path to the work-dir.
   	  -h, --help       show this help message and exit
   	
   Action 'run'
   
   	usage: uarch_test run [-h] [--config PATH] [--suite PATH] [--no-browser]
   	                  [--work-dir PATH]
   	
   	optional arguments:
   	  --config PATH    The Path to the config file. [Default=./config.ini]
   	  --no-browser     Do not open the browser for showing the test report.
   	  --suite PATH     The Path to the custom suite directory.
   	  --work-dir PATH  The Path to the work-dir.
   	  -h, --help       show this help message and exit
   	
   Action 'testlist'
   
   	usage: uarch_test testlist [-h] [--work-dir PATH] [--config PATH] [--suite PATH]
   	
   	optional arguments:
   	  --config PATH    The Path to the config file. [Default=./config.ini]
   	  --suite PATH     The Path to the custom suite directory.
   	  --work-dir PATH  The Path to the work-dir.
   	  -h, --help       show this help message and exit

Install RISCV-GNU Toolchain
===========================

This guide will use the 32-bit riscv-gnu tool chain to compile the architectural suite.
If you already have the 32-bit gnu-toolchain available, you can skip to the next section.

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
       $ ./configure --prefix=/path/to/install --with-arch=rv32gc --with-abi=ilp32d # for 32-bit toolchain
       $ [sudo] make # sudo is required depending on the path chosen in the previous setup
     
   .. tab:: CentosOS/RHEL
     
     .. code-block:: bash
     
       $ sudo yum install autoconf automake python3 libmpc-devel mpfr-devel gmp-devel \
             gawk  bison flex texinfo patchutils gcc gcc-c++ zlib-devel expat-devel
       $ git clone --recursive https://github.com/riscv/riscv-gnu-toolchain
       $ git clone --recursive https://github.com/riscv/riscv-opcodes.git
       $ cd riscv-gnu-toolchain
       $ ./configure --prefix=/path/to/install --with-arch=rv32gc --with-abi=ilp32d # for 32-bit toolchain
       $ [sudo] make # sudo is required depending on the path chosen in the previous setup

Make sure to add the path ``/path/to/install`` to your `$PATH` in the .bashrc/cshrc
With this you should now have all the following available as command line arguments::

  riscv32-unknown-elf-addr2line      riscv32-unknown-elf-elfedit
  riscv32-unknown-elf-ar             riscv32-unknown-elf-g++
  riscv32-unknown-elf-as             riscv32-unknown-elf-gcc
  riscv32-unknown-elf-c++            riscv32-unknown-elf-gcc-8.3.0
  riscv32-unknown-elf-c++filt        riscv32-unknown-elf-gcc-ar
  riscv32-unknown-elf-cpp            riscv32-unknown-elf-gcc-nm
  riscv32-unknown-elf-gcc-ranlib     riscv32-unknown-elf-gprof
  riscv32-unknown-elf-gcov           riscv32-unknown-elf-ld
  riscv32-unknown-elf-gcov-dump      riscv32-unknown-elf-ld.bfd
  riscv32-unknown-elf-gcov-tool      riscv32-unknown-elf-nm
  riscv32-unknown-elf-gdb            riscv32-unknown-elf-objcopy
  riscv32-unknown-elf-gdb-add-index  riscv32-unknown-elf-objdump
  riscv32-unknown-elf-ranlib         riscv32-unknown-elf-readelf
  riscv32-unknown-elf-run            riscv32-unknown-elf-size
  riscv32-unknown-elf-strings        riscv32-unknown-elf-strip


Change Neccesary Target Env Files
=================================

TODO 

Running UArchTest
=================

TODO
