.. See LICENSE.incore for details

.. highlight:: shell

.. _tutorial:

############
UTG Tutorial
############

.. note:: utg is interchangeably denoted as 'framework' in this section.

This section provides a deeper insight about using the UTG Tool.
We will be using the generate command as an alternative to the from-config 
command. It is assumed that you have followed the :ref:`Quickstart<quickstart>`
before trying this out.
Successfully getting through quick start should indicate that the UTG framework
is successsfully installed in your computer.

We will be continuing in the same ``myquickstart`` directory which we had 
created for the quickstart. Right now, the directory structure will be 
something like this

.. code-block:: console

    myquickstart/
    ├── aliasing.yaml
    ├── chromite_uarch_tests
    │   ├── aliasing.yaml
    │   ├── modules
    │   │   ├── branch_predictor
    │   │   │   ├── issues.rst
    │   │   │   ├── utg_gshare_fa_btb_fill_01.py
    │   │   │   ├── utg_gshare_fa_btb_selfmodifying_01.py
    │   │   │   ├── utg_gshare_fa_fence_01.py
    │   │   │   ├── utg_gshare_fa_ghr_alternating_01.py
    │   │   │   ├── utg_gshare_fa_ghr_ones_01.py
    │   │   │   ├── utg_gshare_fa_ghr_zeros_01.py
    │   │   │   ├── utg_gshare_fa_mispredict_loop_01.py
    │   │   │   └── utg_gshare_fa_ras_push_pop_01.py
    │   │   ├── decoder
    │   │   │   └── utg_decoder_i_ext_r_type.py
    │   │   ├── decompressor
    │   │   │   └── utg_decompressor.py
    │   │   └── index.yaml
    │   └── README.rst
    ├── config.ini
    ├── dut_config.yaml
    └── work

If you had gone through the quickstart, you may find some more ``.yapsy_plugin``
files, ``__pycache__`` directories and you will find several tests within the 
``work`` directory. It is okay for your directory tree to be so. It will not
impact your workflow with UTG.

Here, the *aliasing.yaml*, *dut_config.yaml* and *config.ini* were created by 
the ``utg setup`` command.

Detailed description about the options used along with the subcommands has been 
discussed in the :ref:`CLI docs<utg_cli>`. We will be breifly explaining the 
flags in this section.
       
Now, let's start by generating the tests.

.. note:: All paths are absolute.

=======================
**Generate** ASM tests 
=======================

.. code-block:: console

  $ utg generate -v debug -m all -wd ~/myquickstart/work/ \
    -ld ~/myquickstart/work/ -t -gc \ 
    -md ~/myquickstart/chromite_uarch_tests/modules/ \ 
    -dc ~/myquickstart/dut_config.yaml -af ~/myquickstart/aliasing.yaml

- Here the ``-v`` option is used to control the verbosity of the log. Debug logs
  everything which will be useful in debugging the code.
- ``-wd`` UTG will create the test files within this directory. 
  It will also create a `model_test.h` and `link.ld` file in the same directory 
  by default. [REQUIRED]
- ``-ld`` is an optional parameter. If not specified, the ``-wd`` parameter is 
  reused. If the user has his own linker files, he may rename the linker file as
  ``link.ld`` and pass the path to the directory containing the ``link.ld`` file
  along with the ``-ld`` option.
- ``-t`` is a flag used to generate a test_list.yaml file. Information about the 
  test_list format can be found :ref:`here <configuration_files>`.
- ``-gc`` flag is used to specify the generation of SV covergroup and TB files. 
  It is required to pass the `-gc` flag along with the alias file (`-af`).
  The SV files will be found within the ``sv_top`` directory in the ``work`` 
  directory.
- ``-md`` is the path to the modules directory containing the test_classes. The
  test_classes will be sorted into directories based on the module being tested.
- ``-dc`` is the path to the dut_config.yaml generated using ``utg setup``.
- ``-af`` is the path to the aliasing.yaml file generated using ``utg setup``.

Running this command should generate this log in your terminal.

.. code-block:: console

          info  | ****** Micro Architectural Tests *******
          info  | Version : dev-0.0.1
          info  | Copyright (c) 2021, InCore Semiconductors Pvt. Ltd.
          info  | All Rights Reserved.
          info  | utg dir is /home/akrish/work/InCore/micro-arch-tests/utg
          info  | work_dir is /home/akrish/myquickstart/work
         debug  | Checking /home/akrish/myquickstart/chromite_uarch_tests/modules for modules
         debug  | The modules are ['branch_predictor', 'decoder', 'decompressor']
          info  | ****** Generating Tests ******
         debug  | Directory for branch_predictor is /home/akrish/myquickstart/chromite_uarch_tests/modules/branch_predictor
          info  | Starting plugin Creation for branch_predictor
          info  | Created plugins for branch_predictor
         debug  | Generating assembly tests for branch_predictor
         debug  | Generating test for utg_gshare_fa_btb_fill_01
         debug  | Generating test for utg_gshare_fa_mispredict_loop_01
         debug  | Generating test for utg_gshare_fa_ghr_ones_01
         debug  | Generating test for utg_gshare_fa_ras_push_pop_01
         debug  | Generating test for utg_gshare_fa_ghr_alternating_01
         debug  | Generating test for utg_gshare_fa_ghr_zeros_01
         debug  | Generating test for utg_gshare_fa_fence_01
         debug  | Generating test for utg_gshare_fa_btb_selfmodifying_01
         debug  | Finished Generating Assembly Tests for branch_predictor
          info  | Creating test_list for the branch_predictor
         debug  | Current test is /home/akrish/myquickstart/work/branch_predictor/utg_gshare_fa_btb_fill_01/utg_gshare_fa_btb_fill_01.S
         debug  | Current test is /home/akrish/myquickstart/work/branch_predictor/utg_gshare_fa_mispredict_loop_01/utg_gshare_fa_mispredict_loop_01.S
         debug  | Current test is /home/akrish/myquickstart/work/branch_predictor/utg_gshare_fa_ghr_ones_01/utg_gshare_fa_ghr_ones_01.S
         debug  | Current test is /home/akrish/myquickstart/work/branch_predictor/utg_gshare_fa_ras_push_pop_01/utg_gshare_fa_ras_push_pop_01.S
         debug  | Current test is /home/akrish/myquickstart/work/branch_predictor/utg_gshare_fa_ghr_alternating_01/utg_gshare_fa_ghr_alternating_01.S
         debug  | Current test is /home/akrish/myquickstart/work/branch_predictor/utg_gshare_fa_ghr_zeros_01/utg_gshare_fa_ghr_zeros_01.S
         debug  | Current test is /home/akrish/myquickstart/work/branch_predictor/utg_gshare_fa_fence_01/utg_gshare_fa_fence_01.S
         debug  | Current test is /home/akrish/myquickstart/work/branch_predictor/utg_gshare_fa_btb_selfmodifying_01/utg_gshare_fa_btb_selfmodifying_01.S
         debug  | Directory for decoder is /home/akrish/myquickstart/chromite_uarch_tests/modules/decoder
          info  | Starting plugin Creation for decoder
          info  | Created plugins for decoder
         debug  | Generating assembly tests for decoder
         debug  | Generating test for utg_decoder_i_ext_r_type
         debug  | Finished Generating Assembly Tests for decoder
          info  | Creating test_list for the decoder
         debug  | Current test is /home/akrish/myquickstart/work/decoder/utg_decoder_i_ext_r_type/utg_decoder_i_ext_r_type.S
         debug  | Directory for decompressor is /home/akrish/myquickstart/chromite_uarch_tests/modules/decompressor
          info  | Starting plugin Creation for decompressor
          info  | Created plugins for decompressor
         debug  | Generating assembly tests for decompressor
         debug  | Generating test for utg_decompressor
         debug  | Finished Generating Assembly Tests for decompressor
          info  | Creating test_list for the decompressor
         debug  | Current test is /home/akrish/myquickstart/work/decompressor/utg_decompressor/utg_decompressor.S
          info  | ****** Finished Generating Tests ******
         debug  | Creating a linker file at /home/akrish/myquickstart/work
         debug  | Creating Model_test.h file at /home/akrish/myquickstart/work
          info  | Test List was generated by utg. You can find it in the work dir 
         debug  | Checking /home/akrish/myquickstart/chromite_uarch_tests/modules for modules
          info  | ****** Generating Covergroups ******
         debug  | Generated tbtop, defines and interface files
         debug  | Generating CoverPoints for branch_predictor
          info  | Generating coverpoints SV file for utg_gshare_fa_mispredict_loop_01
       warning  | Skipping coverpoint generation for utg_gshare_fa_ras_push_pop_01 as there is no gen_covergroup method 
       warning  | Skipping coverpoint generation for utg_gshare_fa_ghr_ones_01 as there is no gen_covergroup method 
          info  | Generating coverpoints SV file for utg_gshare_fa_ghr_zeros_01
       warning  | Skipping coverpoint generation for utg_gshare_fa_btb_selfmodifying_01 as there is no gen_covergroup method 
       warning  | Skipping coverpoint generation for utg_gshare_fa_ghr_alternating_01 as there is no gen_covergroup method 
          info  | Generating coverpoints SV file for utg_gshare_fa_btb_fill_01
          info  | Generating coverpoints SV file for utg_gshare_fa_fence_01
         debug  | Finished Generating Coverpoints for branch_predictor
         debug  | Generating CoverPoints for decoder
          info  | Generating coverpoints SV file for utg_decoder_i_ext_r_type
         debug  | Finished Generating Coverpoints for decoder
         debug  | Generating CoverPoints for decompressor
       warning  | Skipping coverpoint generation for utg_decompressor as there is no gen_covergroup method 
         debug  | Finished Generating Coverpoints for decompressor
          info  | ****** Finished Generating Covergroups ******

Now your directory structure should be like this. 

.. code-block:: console

    myquickstart/
    ├── aliasing.yaml
    ├── chromite_uarch_tests
    │   ├── aliasing.yaml
    │   ├── modules
    │   │   ├── branch_predictor
    │   │   │   ├── issues.rst
    │   │   │   ├── __pycache__
    │   │   │   │   ├── utg_gshare_fa_btb_fill_01.cpython-39.pyc
    │   │   │   │   ├── utg_gshare_fa_btb_selfmodifying_01.cpython-39.pyc
    │   │   │   │   ├── utg_gshare_fa_fence_01.cpython-39.pyc
    │   │   │   │   ├── utg_gshare_fa_ghr_alternating_01.cpython-39.pyc
    │   │   │   │   ├── utg_gshare_fa_ghr_ones_01.cpython-39.pyc
    │   │   │   │   ├── utg_gshare_fa_ghr_zeros_01.cpython-39.pyc
    │   │   │   │   ├── utg_gshare_fa_mispredict_loop_01.cpython-39.pyc
    │   │   │   │   └── utg_gshare_fa_ras_push_pop_01.cpython-39.pyc
    │   │   │   ├── utg_gshare_fa_btb_fill_01.py
    │   │   │   ├── utg_gshare_fa_btb_fill_01.yapsy-plugin
    │   │   │   ├── utg_gshare_fa_btb_selfmodifying_01.py
    │   │   │   ├── utg_gshare_fa_btb_selfmodifying_01.yapsy-plugin
    │   │   │   ├── utg_gshare_fa_fence_01.py
    │   │   │   ├── utg_gshare_fa_fence_01.yapsy-plugin
    │   │   │   ├── utg_gshare_fa_ghr_alternating_01.py
    │   │   │   ├── utg_gshare_fa_ghr_alternating_01.yapsy-plugin
    │   │   │   ├── utg_gshare_fa_ghr_ones_01.py
    │   │   │   ├── utg_gshare_fa_ghr_ones_01.yapsy-plugin
    │   │   │   ├── utg_gshare_fa_ghr_zeros_01.py
    │   │   │   ├── utg_gshare_fa_ghr_zeros_01.yapsy-plugin
    │   │   │   ├── utg_gshare_fa_mispredict_loop_01.py
    │   │   │   ├── utg_gshare_fa_mispredict_loop_01.yapsy-plugin
    │   │   │   ├── utg_gshare_fa_ras_push_pop_01.py
    │   │   │   └── utg_gshare_fa_ras_push_pop_01.yapsy-plugin
    │   │   ├── decoder
    │   │   │   ├── __pycache__
    │   │   │   │   └── utg_decoder_i_ext_r_type.cpython-39.pyc
    │   │   │   ├── utg_decoder_i_ext_r_type.py
    │   │   │   └── utg_decoder_i_ext_r_type.yapsy-plugin
    │   │   ├── decompressor
    │   │   │   ├── __pycache__
    │   │   │   │   └── utg_decompressor.cpython-39.pyc
    │   │   │   ├── utg_decompressor.py
    │   │   │   └── utg_decompressor.yapsy-plugin
    │   │   └── index.yaml
    │   └── README.rst
    ├── config.ini
    ├── dut_config.yaml
    └── work
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

You can find all the test files within the ``work`` directory. The test names 
will be same as the test_class. The test will be located within the directory 
named same as the module for which the test is written. 

For example, a test written for ``decoder`` will be present at 
``~/myquickstart/work/decoder/``. 

You can also find that the *link.ld* and *model_test.h* files have been 
generated by UTG. This is because the directory passed along with ``-ld`` option
did not already contain a linker file. If it had, these files would have not 
been generated.
