.. See LICENSE.incore for details

.. highlight:: shell

.. _quickstart:

==========
Quickstart
==========

This section is meant to serve as a quick-guide to setup UATG (μArch Test Generator). This guide
will help you setup all the required tooling for running UATG on your system.


Install Python
==============

.. tabs::

   .. tab:: Ubuntu 20.04

      Ubuntu 20.04, by default, comes with python-3.8 which is expected to be compatible with UATG.
            
      You should have 2 binaries: ``python3`` and ``pip3`` available in your $PATH. 
      You can check the versions as below
      
      .. code-block:: shell-session

        $ python3 --version
        Python 3.8.10
        $ pip3 --version
        pip 20.0.2 from /usr/lib/python3/dist-packages/pip (python 3.8)

 
Using CONDA Virtualenv for Python 
---------------------------------

UATG is built and tested to work with python-3.7. It may work with the other (newer) versions, but we would recommend using python-3.7.

Many a times users face issues in installing and managing multiple python versions. This is actually 
a major issue as many gui elements in Linux use the default python versions, in which case installing
python3.7 using the above methods might break other software. We thus advise the use of **conda** to
install python3.7.0

For Ubuntu and CentosOS, please follow the steps here: https://conda.io/projects/conda/en/latest/user-guide/install/linux.html

Fedora users can use the ``sudo dnf install conda`` command to install conda. On installation, close and restart your terminal.

Once you have conda installed do the following to install python 3.7.0::

  $ conda init bash
  $ conda create --name <env-name> python=3.7 --yes
  $ conda config --set auto_activate_base false
  $ conda activate <env-name>
  
You can check the version in the **same shell**::

  $ python --version
  Python 3.7.0
  $ pip --version
  pip 20.1 from <user-path>.local/lib/python3.7/site-packages/pip (python 3.7)

.. _install_uatg:

Install UATG
============

.. tabs:: 

   .. tab:: via Pip

     .. note:: If you are using `pyenv` as mentioned above, make sure to enable that environment before
      performing the following steps.
     
     .. code-block:: shell-session
     
       $ pip3 install uatg
     
     To update an already installed version of UATG to the latest version:
     
     .. code-block:: shell-session
     
       $ pip3 install -U uatg
     
     To checkout a specific version of UATG:
     
     .. code-block:: shell-session
     
       $ pip3 install uatg==1.x.x

     This is the preferred method to install UATG, as it will always install the most recent stable release.
     
     If you don't have `pip`_ installed, this `Python installation guide`_ can guide
     you through the process.
     
     .. _pip: https://pip.pypa.io
     .. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

   .. tab:: for Dev

     The sources for UATG can be downloaded from the `Github repo <https://github.com/incoresemi/uatg>`_.
     
     You can clone the repository:
     
     .. code-block:: console
     
         $ git clone https://github.com/incoresemi/uatg.git
     
     
     Once you have a copy of the source, you can install it with:
     
     .. code-block:: console
         
         $ cd uatg
         $ pip3 install --editable .
     
     .. _Gitlab repo: https://github.com/incoresemi/uatg

   .. tab:: via Git

     To install UATG, run this command in your terminal:
     
     .. code-block:: console
     
         $ pip3 install git+https://github.com/incoresemi/uatg.git
     

Test UATG
=========

Once you have installed UArchTest you can execute ``uatg --help`` to print the help routine:

.. code-block:: shell-session

    Usage: uatg [OPTIONS] COMMAND [ARGS]...

      RISC-V µArchitectural Test Generator

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

Change Neccesary Target Env Files
=================================

- The additional files like the linker will be generated automatically along 
  with the tests, if the user does not choose to use a linker of his own.
- In addition to that, the framework requires multiple additional configuration YAML files 
  which contains the configuration of the DUT under test. Currently, UATG is built to search for 5 configuration files
  of chromite (isa, debug, core, csr and custom configuration YAMLs). The 
  values obtained from these YAMLs will be used to customize the tests for the 
  DUT.

Running UATG
============

To start using UATG, let us create a directory called ``myquickstart``. For 
demonstration, we are creating the quickstart directory within the 
``/home/<user>/`` or ``~`` directory. 

.. code-block:: console

   $ mkdir ~/myquickstart

You can install the chromite_uatg_tests with several tests from the 
`Repo <https://github.com/incoresemi/chromite_uatg_tests.git>`_

.. code-block:: console

    $ cd ~/myquickstart
    $ git clone https://github.com/incoresemi/chromite_uatg_tests.git

It is necessary to create a work directory for UATG. The work directory is where 
UATG will be store the ASM test files as well as test reports and logs.

.. code-block:: console

   $ cd ~/myquickstart
   $ mkdir work

We will next create the ``config.ini``, ``isa_config.yaml``, 
``core_config.yaml``, ``custom_config.yaml``, ``csr_grouping.yaml``,  
``rv_debug.yaml`` and the ``aliasing.yaml`` files under the ``myquickstart`` 
directory. You can use the setup to create this file:

.. code-block:: console

   $ cd ~/myquickstart
   $ uatg setup

The above should create a ``config.ini`` file with the following contents.
It should also create the ``aliasing.yaml``, ``csr_grouping.yaml`` 
``rv_debug.yaml`` and ``*_config.yaml`` files.

Details and further specification of the config file syntax is available at 
:ref:`Configuration files Spec<configuration_files>`.

.. warning:: The yaml files generated by running ``uatg setup`` should be 
   considered as templates. They have been created just to give a headstart to 
   the user when they try to create their own YAMLs for their design. These files, eventhough 
   working,  are likely to be very old and can be factually wrong. 
   So, the user is required to use these files to test and setup UATG but not for actual verification.
   The user must start using the actual YAMLs once they understand the UATG flow by following this quickstart or the tutorial.

.. warning:: **CHROMITE SPECIFIC** When generating tests for any configuration of the Chromite core, the user should make use
   of the checked YAMLs generated while configuring the core. The checked YAMLs
   can be found in the ``build`` directory of chromite.

Steps to generate the checked YAMLs of Chromite
-----------------------------------------------

The steps to clone and build your own copy of Chromite are as follows,

.. code-block:: shell-session

  $ cd ~/myquickstart/
  $ git clone https://gitlab.com/incoresemi/core-generators/chromite.git

If you are cloning the chromite repo for the first time it would be best to 
install the dependencies first:

.. code-block:: shell-session

  $ cd chromite/
  $ pyenv activate venv # ignore this is you are not using pyenv
  $ pip install -U -r requirements.txt

The Chromite core generator takes a specific YAML files as input. 
It makes specific checks to validate if the user has entered 
valid data and none of the parameters conflict with each other. For e.g., 
mentioning the 'D' extension without the 'F' will be captured by the generator 
as an invalid spec. More information on the exact parameters and constraints on 
each field are discussed here.

Once the input YAML has been validated, the generator then clones all the 
dependent repositories which enable building a test-soc, simulating it and 
performing verification of the core. This is an alternative to maintaining the 
repositories as submodules, which typically pollutes the commit history with 
bump commits.

At the end, the generator outputs a single ``makefile.inc`` in the same folder 
that it was run, which contains definitions of paths where relevant bluespec 
files are present, bsc command with macro definitions, verilator simulation 
commands, etc.

A sample yaml input YAML (`default.yaml`) is available in the ``sample_config`` 
directory of the repository. 

To build the core with a sample test-soc using the default config do the 
following:

.. code-block:: shell-session

  $ python -m configure.main -ispec sample_config/c64/rv64i_isa.yaml\
    -customspec sample_config/c64/rv64i_custom.yaml -cspec sample_config/c64/core64.yaml\
    -gspec sample_config/c64/csr_grouping64.yaml\
    -dspec sample_config/c64/rv64i_debug.yaml --verbose debug

The above step generates a ``makefile.inc`` file in the same folder and also
clones other dependent repositories to build a test-soc and carry out
verification.

.. note:: The most up-to-date documentation to build the core can be found 
   `here <https://chromite.readthedocs.io/en/using-csrbox/getting_started.html#building-the-core>`_ 
   in the ``Chromite`` core's documentation.

.. warning:: You will need to change ``user`` to your username in the below file.

.. warning:: All paths should be absolute.

.. code-block:: ini
   :linenos:
    
    # See LICENSE.incore for license details

    [uatg]

    # number of processes to spawn. Default = 1
    jobs = 4
    
    # [info, error, debug] set verbosity level to view different levels of messages.
    verbose = info
    
    # [True, False] the clean flag removes unnecessary files from the previous runs and cleans directories
    clean = False

    # Enter the modules whose tests are to be generated/validated in comma separated format.
    # Run 'uatg --list-modules -md <path> ' to find all the modules that are supported.
    # Use 'all' to generate/validate all modules
    modules = all

    # Absolute path to chromite_uatg_tests/modules Directory
    module_dir = /home/user/myquickstart/chromite_uatg_tests/modules/

    # Directory to dump assembly files and reports
    work_dir = /home/user/myquickstart/work/

    # location to store the link.ld linker file. By default it's the target directory within chromite_uatg_tests
    linker_dir = /home/user/myquickstart/chromite_uatg_tests/target

    paging_modes = sv39, sv48, sv57

    index_file =

    # Absolute Path of the yaml file containing the signal aliases of the DUT 
    alias_file = /home/user/myquickstart/chromite_uatg_tests/aliasing.yaml

    # [True, False] If the gen_test_list flag is True, the test_list.yaml needed for running tests in river_core are generated automatically.
    # Unless you want to run individual tests in river_core, set the flag to True
    gen_test_list = True
    # [True, False] If the gen_test flag is True, assembly files are generated/overwritten
    gen_test = True
    # [True, False] If the val_test flag is True, Log from DUT are parsed and the modules are validated
    val_test = False
    # [True, False] If the gen_cvg flag is True, System Verilog cover-groups are generated
    gen_cvg = True
    # [True, False] if test_compile flag is True, the generated assembly files are compiled to uncover syntax errors if any.
    test_compile = False

    # Path to the yaml files containing DUT Configuration.
    [uatg.configuration_files]
    isa = /home/user/myquickstart/chromite/build/isa_checked.yaml
    core = /home/user/myquickstart/chromite/build/core_checked.yaml
    custom = /home/user/myquickstart/chromite/build/custom_checked.yaml
    debug = /home/user/myquickstart/chromite/build/debug_checked.yaml
    csr_grouping = /home/user/myquickstart/chromite/sample_config/rv64imacsu/csr_grouping.yaml
    
Once you have changed the user field in the paths, save the file. 
You can run UATG using the ``from-config`` subcommand.

.. code-block:: console

   $ cd ~/myquickstart
   $ uatg from-config -c config.ini -v debug

You should see the following log on your screen

.. code-block:: console

      info  | ****** Micro Architectural Tests *******
      info  | Version : dev-0.0.1
      info  | Copyright (c) 2021, InCore Semiconductors Pvt. Ltd.
      info  | All Rights Reserved.
      info  | uatg dir is /home/akrish/work/InCore/micro-arch-tests/uatg
      info  | work_dir is /home/akrish/quickstart/work/
     debug  | Checking /home/akrish/quickstart/chromite_uatg_tests/modules/ for modules
     debug  | The modules are ['branch_predictor', 'decoder', 'decompressor']
      info  | ****** Generating Tests ******
     debug  | Directory for branch_predictor is /home/akrish/quickstart/chromite_uatg_tests/modules/branch_predictor
      info  | Starting plugin Creation for branch_predictor
      info  | Created plugins for branch_predictor
     debug  | Generating assembly tests for branch_predictor
     debug  | Generating test for uatg_gshare_fa_btb_fill_01
     debug  | Generating test for uatg_gshare_fa_mispredict_loop_01
     debug  | Generating test for uatg_gshare_fa_ghr_alternating_01
     debug  | Generating test for uatg_gshare_fa_btb_selfmodifying_01
     debug  | Generating test for uatg_gshare_fa_fence_01
     debug  | Generating test for uatg_gshare_fa_ghr_ones_01
     debug  | Generating test for uatg_gshare_fa_ghr_zeros_01
     debug  | Generating test for uatg_gshare_fa_ras_push_pop_01
     debug  | Finished Generating Assembly Tests for branch_predictor
      info  | Creating test_list for the branch_predictor
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/uatg_gshare_fa_btb_fill_01/uatg_gshare_fa_btb_fill_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/uatg_gshare_fa_mispredict_loop_01/uatg_gshare_fa_mispredict_loop_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/uatg_gshare_fa_ghr_alternating_01/uatg_gshare_fa_ghr_alternating_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/uatg_gshare_fa_btb_selfmodifying_01/uatg_gshare_fa_btb_selfmodifying_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/uatg_gshare_fa_fence_01/uatg_gshare_fa_fence_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/uatg_gshare_fa_ghr_ones_01/uatg_gshare_fa_ghr_ones_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/uatg_gshare_fa_ghr_zeros_01/uatg_gshare_fa_ghr_zeros_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/uatg_gshare_fa_ras_push_pop_01/uatg_gshare_fa_ras_push_pop_01.S
     debug  | Directory for decoder is /home/akrish/quickstart/chromite_uatg_tests/modules/decoder
      info  | Starting plugin Creation for decoder
      info  | Created plugins for decoder
     debug  | Generating assembly tests for decoder
     debug  | Generating test for uatg_decoder_i_ext_r_type
     debug  | Finished Generating Assembly Tests for decoder
      info  | Creating test_list for the decoder
     debug  | Current test is /home/akrish/quickstart/work/decoder/uatg_decoder_i_ext_r_type/uatg_decoder_i_ext_r_type.S
     debug  | Directory for decompressor is /home/akrish/quickstart/chromite_uatg_tests/modules/decompressor
      info  | Starting plugin Creation for decompressor
      info  | Created plugins for decompressor
     debug  | Generating assembly tests for decompressor
     debug  | Generating test for uatg_decompressor
     debug  | Finished Generating Assembly Tests for decompressor
      info  | Creating test_list for the decompressor
     debug  | Current test is /home/akrish/quickstart/work/decompressor/uatg_decompressor/uatg_decompressor.S
      info  | ****** Finished Generating Tests ******
     debug  | Using user specified linker
     debug  | Using user specified model_test file
      info  | Test List was generated by uatg. You can find it in the work dir 
     debug  | Checking /home/akrish/quickstart/chromite_uatg_tests/modules/ for modules
      info  | ****** Generating Covergroups ******
     debug  | Generated tbtop, defines and interface files
     debug  | Removing Existing coverpoints SV file
     debug  | Generating CoverPoints for branch_predictor
   warning  | Skipping coverpoint generation for uatg_gshare_fa_ras_push_pop_01 as there is no gen_covergroup method 
   warning  | Skipping coverpoint generation for uatg_gshare_fa_ghr_alternating_01 as there is no gen_covergroup method 
      info  | Generating coverpoints SV file for uatg_gshare_fa_fence_01
      info  | Generating coverpoints SV file for uatg_gshare_fa_ghr_zeros_01
   warning  | Skipping coverpoint generation for uatg_gshare_fa_ghr_ones_01 as there is no gen_covergroup method 
      info  | Generating coverpoints SV file for uatg_gshare_fa_mispredict_loop_01
      info  | Generating coverpoints SV file for uatg_gshare_fa_btb_fill_01
   warning  | Skipping coverpoint generation for uatg_gshare_fa_btb_selfmodifying_01 as there is no gen_covergroup method 
     debug  | Finished Generating Coverpoints for branch_predictor
     debug  | Generating CoverPoints for decoder
      info  | Generating coverpoints SV file for uatg_decoder_i_ext_r_type
     debug  | Finished Generating Coverpoints for decoder
     debug  | Generating CoverPoints for decompressor
   warning  | Skipping coverpoint generation for uatg_decompressor as there is no gen_covergroup method 
     debug  | Finished Generating Coverpoints for decompressor
      info  | ****** Finished Generating Covergroups ******


You will find the generated files within the work directory. The directory
structure is as follows.

.. code-block:: bash
  
    work/
    ├── branch_predictor
    │   ├── uatg_gshare_fa_btb_fill_01
    │   │   └── uatg_gshare_fa_btb_fill_01.S
    │   ├── uatg_gshare_fa_btb_selfmodifying_01
    │   │   └── uatg_gshare_fa_btb_selfmodifying_01.S
    │   ├── uatg_gshare_fa_fence_01
    │   │   └── uatg_gshare_fa_fence_01.S
    │   ├── uatg_gshare_fa_ghr_alternating_01
    │   │   └── uatg_gshare_fa_ghr_alternating_01.S
    │   ├── uatg_gshare_fa_ghr_ones_01
    │   │   └── uatg_gshare_fa_ghr_ones_01.S
    │   ├── uatg_gshare_fa_ghr_zeros_01
    │   │   └── uatg_gshare_fa_ghr_zeros_01.S
    │   ├── uatg_gshare_fa_mispredict_loop_01
    │   │   └── uatg_gshare_fa_mispredict_loop_01.S
    │   └── uatg_gshare_fa_ras_push_pop_01
    │       └── uatg_gshare_fa_ras_push_pop_01.S
    ├── decoder
    │   └── uatg_decoder_i_ext_r_type
    │       └── uatg_decoder_i_ext_r_type.S
    ├── decompressor
    │   └── uatg_decompressor
    │       └── uatg_decompressor.S
    ├── link.ld
    ├── model_test.h
    ├── sv_top
    │   ├── coverpoints.sv
    │   ├── defines.sv
    │   ├── interface.sv
    │   └── tb_top.sv
    └── test_list.yaml

For the sake of conciseness, the work directory shown here contains very limited
tests. The number of modules may differ for you depending on the number of modules/test plugins 
added to the chromite_uatg_tests repository. 

The ``link.ld`` and ``model_test.h`` files are DUT specific files. It is 
generated assuming that the DUT is Chromite. The user should be providing the
path to his own linker files in the *config.ini* file if he is testing his own
design.

The ``sv_top`` directory contains the system verilog coverpoints generated 
using uatg.

You can also perform a syntax check of the assembly generated using the makefile
present in the work directory. Ypu can find additional in 
:ref:`here <make-reference>`

Finally, the ``test_list.yaml`` is used to make list of all the tests generated.
Details about the test_list can be found here,  
:ref:`Configuration files Spec<configuration_files>`.

Congratulations, you have successfully run UATG. 

.. note:: For a detailed tutorial about using UATG to generate tests, check the 
   :ref:`tutorial <tutorial>` section of this documentation.
