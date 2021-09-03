.. See LICENSE.incore for details

.. highlight:: shell

.. _quickstart:

==========
Quickstart
==========

This section is meant to serve as a quick-guide to setup UTG(Uarch Test Generator). This guide
will help you setup all the required tooling for running utg on your system.


Install Python
==============

.. tabs::

   .. tab:: Ubuntu 20.04

      Ubuntu 20.04, by default, comes with python-3.8 which is expected to be compatible with UTG.
            
      You should have 2 binaries: ``python3`` and ``pip3`` available in your $PATH. 
      You can check the versions as below
      
      .. code-block:: shell-session

        $ python3 --version
        Python 3.8.10
        $ pip3 --version
        pip 20.0.2 from /usr/lib/python3/dist-packages/pip (python 3.8)

 
Using CONDA Virtualenv for Python 
---------------------------------

UTG officially requires python-3.7, even though it might be compatible with the other versions. Hence we would recommend using python-3.7.

Many a times users face issues in installing and managing multiple python versions. This is actually 
a major issue as many gui elements in Linux use the default python versions, in which case installing
python3.6 using the above methods might break other software. We thus advise the use of **conda** to
install python3.7.0

For Ubuntu and CentosOS, please follow the steps here: https://conda.io/projects/conda/en/latest/user-guide/install/linux.html

Fedora users can use the ``sudo dnf install conda`` command to install conda. On installation, close and restart your terminal.

Once you have conda installed do the following to install python 3.7.0::

  $ conda init bash
  $ conda create --name <env-name> --python=3.7 --yes
  $ conda set --activate-base false
  $ conda activate <env-name>
  
You can check the version in the **same shell**::

  $ python --version
  Python 3.7.0
  $ pip --version
  pip 20.1 from <user-path>.local/lib/python3.7/site-packages/pip (python 3.7)

.. _install_utg:

Install UTG
===========

.. tabs:: 

   .. tab:: for Dev

     The sources for UTG can be downloaded from the `GitLab repo`_.
     
     You can clone the repository:
     
     .. code-block:: console
     
         $ git clone https://gitlab.com/incoresemi/micro-arch-tests.git
     
     
     Once you have a copy of the source, you can install it with:
     
     .. code-block:: console
         
         $ cd utg
         $ pip3 install --editable .
     
     .. _Gitlab repo: https://gitlab.com/incoresemi/micro-arch-tests

   .. tab:: via Git

     To install UTG, run this command in your terminal:
     
     .. code-block:: console
     
         $ pip3 install git+https://gitlab.com/incoresemi/micro-arch-tests.git
     
     This is the preferred method to install UTG, as it will always install the most recent stable release.
     
     If you don't have `pip`_ installed, this `Python installation guide`_ can guide
     you through the process.
     
     .. _pip: https://pip.pypa.io
     .. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

   .. tab:: via Pip

     .. note:: If you are using `pyenv` as mentioned above, make sure to enable that environment before
      performing the following steps.
     
     .. code-block:: shell-session
     
       $ pip3 install utg
     
     To update an already installed version of UTG to the latest version:
     
     .. code-block:: shell-session
     
       $ pip3 install -U utg
     
     To checkout a specific version of UTG:
     
     .. code-block:: shell-session
     
       $ pip3 install utg==1.x.x


Test UTG
========

Once you have installed UArchTest you can execute ``utg --help`` to print the help routine:

.. code-block:: shell-session

    Usage: utg [OPTIONS] COMMAND [ARGS]...

      RISC-V Micro-Architectural Test Generator

    Options:
      --version  Show the version and exit.
      --help     Show this message and exit.

    Commands:
      clean         Removes ASM, SV and other generated files from the work...
      from-config   This subcommand reads parameters from config.ini and runs...
      generate      Generates tests, cover-groups for a list of modules...
      list-modules  Provides the list of modules supported from the module_dir...
      setup         Setups template files for config.ini, dut_config.yaml and...
      validate


Install RISCV-GNU Toolchain
===========================

This guide will use the 64-bit riscv-gnu tool chain to compile the architectural suite.
If you already have the 64-bit gnu-toolchain available, you can skip to the next section.

.. note:: The git clone and installation will take significant time. Please be patient. If you face
   issues with any of the following steps please refer to
   https://github.com/riscv/riscv-gnu-toolchain for further help in installation.

.. tabs::
   .. tab:: Ubuntu

     .. code-block:: shell-session
       
       $ sudo apt-get install autoconf automake autotools-dev curl python3 libmpc-dev \
             libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool \
             patchutils bc zlib1g-dev libexpat-dev
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

- The environment files required for the framework are present within the ``utg/env/`` directory.
- The additional files like the linker will be generated automatically along with the tests, if the user does not choose to use a linker of his own.
- In addition to that, the framework requires an additional dut_config.yaml file, which should summarize the configuration of the DUT under test. The values obtained from this YAML will be used to customize the tests for the DUT.

Running UTG
===========


