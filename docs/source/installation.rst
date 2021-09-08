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
     
         $ git clone https://github.com/incoresemi/utg.git
     
     
     Once you have a copy of the source, you can install it with:
     
     .. code-block:: console
         
         $ cd utg
         $ pip3 install --editable .
     
     .. _Gitlab repo: https://github.com/incoresemi/utg

   .. tab:: via Git

     To install UTG, run this command in your terminal:
     
     .. code-block:: console
     
         $ pip3 install git+https://github.com/incoresemi/utg.git
     
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



Change Neccesary Target Env Files
=================================

- The additional files like the linker will be generated automatically along 
  with the tests, if the user does not choose to use a linker of his own.
- In addition to that, the framework requires an additional dut_config.yaml 
  file, which should summarize the configuration of the DUT under test. The 
  values obtained from this YAML will be used to customize the tests for the 
  DUT.

Running UTG
===========

To start using UTG, let us create a directory called ``myquickstart``. For 
demonstration, we are creating the quickstart directory within the 
``/home/<user>/`` or ``~`` directory. 

.. code-block:: console

   $ mkdir ~/myquickstart

You can install the chromite_uarch_tests with several tests from the 
`Repo <https://github.com/incoresemi/chromite_uarch_tests.git>`_

.. code-block:: console

    $ cd ~/myquickstart
    $ git clone https://github.com/incoresemi/chromite_uarch_tests.git

It is necessary to create a work directory for UTG. The work directory is where 
UTG will be store the ASM test files as well as test reports and logs.

.. code-block:: console

   $ cd ~/myquickstart
   $ mkdir work

We will next create the ``config.ini``, ``dut_config.yaml`` and the 
``aliasing.yaml`` files under the ``myquickstart`` directory. You
can use the setup to create this file:

.. code-block:: console

   $ cd ~/myquickstart
   $ utg setup

The above should create a ``config.ini`` file with the following contents.
It should also create the ``aliasing.yaml`` and ``dut_config.yaml`` files.
Details and further specification of the config file syntax is available at 
:ref:`Configuration files Spec<configuration_files>`.

.. warning:: You will need to change ``user`` to your username in the below file.

.. warning:: All paths should be absolute.

.. code-block:: ini
   :linenos:
    
    [utg]

    # [info, error, debug] set verbosity level to view different levels of messages.
    verbose = info
    # [True, False] the clean flag removes unnecessary files from the previous runs and cleans directories
    clean = False

    # Enter the modules whose tests are to be generated/validated in comma separated format.
    # Run 'utg --list-modules -md <path> ' to find all the modules that are supported.
    # Use 'all' to generate/validate all modules
    modules = all

    # Absolute path to chromite_uarch_tests/modules Directory
    module_dir = /home/user/myquickstart/chromite_uarch_tests/modules/

    # Directory to dump assembly files and reports
    work_dir = /home/user/myquickstart/work/

    # location to store the link.ld linker file. By default it's same as work_dir
    linker_dir = /home/user/myquickstart/work/

    # Path of the yaml file containing DUT Configuration.
    dut_config = /home/user/myquickstart/dut_config.yaml

    # Absolute Path of the yaml file containing the signal aliases of the DUT 
    alias_file = /home/user/myquickstart/aliasing.yaml

    # [True, False] If the gen_test_list flag is True, the test_list.yaml needed for running tests in river_core are generated automatically.
    # Unless you want to run individual tests in river_core, set the flag to True
    gen_test_list = True
    # [True, False] If the gen_test flag is True, assembly files are generated/overwritten
    gen_test = True
    # [True, False] If the val_test flag is True, Log from DUT are parsed and the modules are validated
    val_test = False
    # [True, False] If the gen_cvg flag is True, System Verilog cover-groups are generated
    gen_cvg = True

Once you have changed the user field in the paths, save the file. 
You can run UTG using the ``from-config`` subcommand.

.. code-block:: console

   $ cd ~/myquickstart
   $ utg from-config -c config.ini -v debug

You should see the following log on your screen

.. code-block:: console

      info  | ****** Micro Architectural Tests *******
      info  | Version : dev-0.0.1
      info  | Copyright (c) 2021, InCore Semiconductors Pvt. Ltd.
      info  | All Rights Reserved.
      info  | utg dir is /home/akrish/work/InCore/micro-arch-tests/utg
      info  | work_dir is /home/akrish/quickstart/work/
     debug  | Checking /home/akrish/quickstart/chromite_uarch_tests/modules/ for modules
     debug  | The modules are ['branch_predictor', 'decoder', 'decompressor']
      info  | ****** Generating Tests ******
     debug  | Directory for branch_predictor is /home/akrish/quickstart/chromite_uarch_tests/modules/branch_predictor
      info  | Starting plugin Creation for branch_predictor
      info  | Created plugins for branch_predictor
     debug  | Generating assembly tests for branch_predictor
     debug  | Generating test for utg_gshare_fa_btb_fill_01
     debug  | Generating test for utg_gshare_fa_mispredict_loop_01
     debug  | Generating test for utg_gshare_fa_ghr_alternating_01
     debug  | Generating test for utg_gshare_fa_btb_selfmodifying_01
     debug  | Generating test for utg_gshare_fa_fence_01
     debug  | Generating test for utg_gshare_fa_ghr_ones_01
     debug  | Generating test for utg_gshare_fa_ghr_zeros_01
     debug  | Generating test for utg_gshare_fa_ras_push_pop_01
     debug  | Finished Generating Assembly Tests for branch_predictor
      info  | Creating test_list for the branch_predictor
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/utg_gshare_fa_btb_fill_01/utg_gshare_fa_btb_fill_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/utg_gshare_fa_mispredict_loop_01/utg_gshare_fa_mispredict_loop_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/utg_gshare_fa_ghr_alternating_01/utg_gshare_fa_ghr_alternating_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/utg_gshare_fa_btb_selfmodifying_01/utg_gshare_fa_btb_selfmodifying_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/utg_gshare_fa_fence_01/utg_gshare_fa_fence_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/utg_gshare_fa_ghr_ones_01/utg_gshare_fa_ghr_ones_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/utg_gshare_fa_ghr_zeros_01/utg_gshare_fa_ghr_zeros_01.S
     debug  | Current test is /home/akrish/quickstart/work/branch_predictor/utg_gshare_fa_ras_push_pop_01/utg_gshare_fa_ras_push_pop_01.S
     debug  | Directory for decoder is /home/akrish/quickstart/chromite_uarch_tests/modules/decoder
      info  | Starting plugin Creation for decoder
      info  | Created plugins for decoder
     debug  | Generating assembly tests for decoder
     debug  | Generating test for utg_decoder_i_ext_r_type
     debug  | Finished Generating Assembly Tests for decoder
      info  | Creating test_list for the decoder
     debug  | Current test is /home/akrish/quickstart/work/decoder/utg_decoder_i_ext_r_type/utg_decoder_i_ext_r_type.S
     debug  | Directory for decompressor is /home/akrish/quickstart/chromite_uarch_tests/modules/decompressor
      info  | Starting plugin Creation for decompressor
      info  | Created plugins for decompressor
     debug  | Generating assembly tests for decompressor
     debug  | Generating test for utg_decompressor
     debug  | Finished Generating Assembly Tests for decompressor
      info  | Creating test_list for the decompressor
     debug  | Current test is /home/akrish/quickstart/work/decompressor/utg_decompressor/utg_decompressor.S
      info  | ****** Finished Generating Tests ******
     debug  | Using user specified linker
     debug  | Using user specified model_test file
      info  | Test List was generated by utg. You can find it in the work dir 
     debug  | Checking /home/akrish/quickstart/chromite_uarch_tests/modules/ for modules
      info  | ****** Generating Covergroups ******
     debug  | Generated tbtop, defines and interface files
     debug  | Removing Existing coverpoints SV file
     debug  | Generating CoverPoints for branch_predictor
   warning  | Skipping coverpoint generation for utg_gshare_fa_ras_push_pop_01 as there is no gen_covergroup method 
   warning  | Skipping coverpoint generation for utg_gshare_fa_ghr_alternating_01 as there is no gen_covergroup method 
      info  | Generating coverpoints SV file for utg_gshare_fa_fence_01
      info  | Generating coverpoints SV file for utg_gshare_fa_ghr_zeros_01
   warning  | Skipping coverpoint generation for utg_gshare_fa_ghr_ones_01 as there is no gen_covergroup method 
      info  | Generating coverpoints SV file for utg_gshare_fa_mispredict_loop_01
      info  | Generating coverpoints SV file for utg_gshare_fa_btb_fill_01
   warning  | Skipping coverpoint generation for utg_gshare_fa_btb_selfmodifying_01 as there is no gen_covergroup method 
     debug  | Finished Generating Coverpoints for branch_predictor
     debug  | Generating CoverPoints for decoder
      info  | Generating coverpoints SV file for utg_decoder_i_ext_r_type
     debug  | Finished Generating Coverpoints for decoder
     debug  | Generating CoverPoints for decompressor
   warning  | Skipping coverpoint generation for utg_decompressor as there is no gen_covergroup method 
     debug  | Finished Generating Coverpoints for decompressor
      info  | ****** Finished Generating Covergroups ******


You will find the generated files within the work directory. The directory
structure is as follows.

.. code-block:: bash
  
    work/
    ├── branch_predictor
    │   ├── utg_gshare_fa_btb_fill_01
    │   │   └── utg_gshare_fa_btb_fill_01.S
    │   ├── utg_gshare_fa_btb_selfmodifying_01
    │   │   └── utg_gshare_fa_btb_selfmodifying_01.S
    │   ├── utg_gshare_fa_fence_01
    │   │   └── utg_gshare_fa_fence_01.S
    │   ├── utg_gshare_fa_ghr_alternating_01
    │   │   └── utg_gshare_fa_ghr_alternating_01.S
    │   ├── utg_gshare_fa_ghr_ones_01
    │   │   └── utg_gshare_fa_ghr_ones_01.S
    │   ├── utg_gshare_fa_ghr_zeros_01
    │   │   └── utg_gshare_fa_ghr_zeros_01.S
    │   ├── utg_gshare_fa_mispredict_loop_01
    │   │   └── utg_gshare_fa_mispredict_loop_01.S
    │   └── utg_gshare_fa_ras_push_pop_01
    │       └── utg_gshare_fa_ras_push_pop_01.S
    ├── decoder
    │   └── utg_decoder_i_ext_r_type
    │       └── utg_decoder_i_ext_r_type.S
    ├── decompressor
    │   └── utg_decompressor
    │       └── utg_decompressor.S
    ├── link.ld
    ├── model_test.h
    ├── sv_top
    │   ├── coverpoints.sv
    │   ├── defines.sv
    │   ├── interface.sv
    │   └── tb_top.sv
    └── test_list.yaml

The tests have been generated for decompressor, decoder and branch_predictor 
right now. The number of modules may differ for you if some more tests were 
added to the chromite_uarch_tests repository. 

The ``link.ld`` and ``model_test.h`` files are DUT specific files. It is 
generated assuming that the DUT is Chromite. The user should be providing the
path to his own linker files in the *config.ini* file if he is testing his own
design.

The ``sv_top`` directory contains the system verilog coverpoints generated 
using UTG.

Finally, the ``test_list.yaml`` is used to make list of all the tests generated.
Details about the test_list can be found here,  
:ref:`Configuration files Spec<configuration_files>`.

Congratulations, you have successfully run UTG. 

.. note:: For a detailed tutorial about using UTG to generate tests, check the 
   tutorial section of this documentation.
