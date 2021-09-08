.. _creating_new_tests: 

###############################
Writing Tests for UTG Framework
###############################

The test classes as well the directories containing the classes should 
atricly adhere to certain guidelines for UTG to pick them up during test 
generation. These guidelines are being presented here.

======================
Directory Organization
======================

The tests being writen by the user should be placed withing directories which
stritly follow certain guidelines.

The directory tree of the ``chromite_uarch_tests`` is as follows.

.. code-block:: console

  modules/
  ├── branch_predictor
  │   ├── issues.rst
  │   ├── utg_gshare_fa_btb_fill_01.py
  │   ├── utg_gshare_fa_btb_selfmodifying_01.py
  │   ├── utg_gshare_fa_fence_01.py
  │   ├── utg_gshare_fa_ghr_alternating_01.py
  │   ├── utg_gshare_fa_ghr_ones_01.py
  │   ├── utg_gshare_fa_ghr_zeros_01.py
  │   ├── utg_gshare_fa_mispredict_loop_01.py
  │   └── utg_gshare_fa_ras_push_pop_01.py
  ├── decoder
  │   └── utg_decoder_i_ext_r_type.py
  ├── decompressor
  │   └── utg_decompressor.py
  └── index.yaml
   
Irrespective of the name, every directory purposed to host tests for UTG should
have a similiar structure.

Other than that, it is necessary that the module specific directories. like 
*branch_predictor*, *decoder* and *decompressor* should be named same as the
verilog module name in order to improve comprehension. 

The ``index.yaml`` contains the names of all modules for which tests are to be 
generated. When invoked, UTG reads the *index.yaml* file first and checks only
the directories which were specified in the yaml file for test_classes. Other 
folders are not used to pick up tests.

The structure of the *index.yaml* file is presented as follows,

.. code-block:: yaml
   
   :linenos:

  branch_predictor:
    utg_gshare_fa_btb_fill_01: "fill the BTB with entries"
    utg_gshare_fa_btb_selfmodifying_01: "ASM that modifies itself, also used to verify functioning of fence instruction"
    utg_gshare_fa_fence_01: "Verify the functioning of fence instruction"
    utg_gshare_fa_ghr_alternating_01: "fill the GHR Register with alternating 1-0 pattern"
    utg_gshare_fa_ghr_ones_01: "fill the GHR Register with ones"
    utg_gshare_fa_ghr_zeros_01: "fill the GHR Register with zeros"
    utg_gshare_fa_mispredict_loop_01: ""
    utg_gshare_fa_ras_push_pop_01: "Pushing and Popping the return address stack using call-ret instructions"
  decoder:
    utg_decoder_arithmetic_insts: "tests arithmetic instructions"

  decompressor:
    utg_decompressor: "checks if mis-predictions occur and tests macro's"


The above file contains information required for UTG to pick-up the tests from 
your directory. 

This index file is written based on the modules present in the chromite core. 
The tests for the branch_predictor unit are present in the branch_predictor 
directory as shown earlier. It is important that the name of the directory 
containing the module specific tests is **SAME** as that of the entry(key) in 
the *index.yaml* file.

If the names differ, UTG will ignore the directory with the tests due to this
name mismatch.

.. note:: We require you to create a new directory for every module because
   it makes the directory more organized and handling tests as well as
   yapsy-plugin generation for multiple modules becomes easier.

Organizing your own directory for storing tests
-----------------------------------------------

As an example, let us assume you want to create a test for a module ``stack``.
Let us assume you are in your ``home`` directory. 

First we make a top_level directory called ``tests`` in the 
``home, i.e /home/user/ or ~/`` directory. 

.. code-block:: console

   $ mkdir /home/user/tests

Once you've created the tests directory. ``cd`` into the directory and create
another directory. The name of this new directory should be same as the name of 
the module you are writing the test for. In this case, *stack*.

.. code-block:: console

   $ cd tests
   $ mkdir stack

Upon creating this new directory, ``cd`` into the ``stack directory`` and 
create your test class. The naming guidelines to be followed while creating 
new test_classes will be explained in the later sections of the same document. 
For now, we are creating a test which would overflow the stack.

.. code-block:: console

   $ cd stack
   $ vi utg_stack_overflow.py

Once you have created the test_class, return to your ``~/tests/`` directory and 
create a, ``index.yaml`` file. 

.. code-block:: console

   $ cd ../
   $ vi index.yaml

The content to typed within the yaml file for UTG to recognize the test is this.

.. code-block:: yaml

   stack: 
     utg_stack_overflow: "Overflows the stack"

Here, the first key ``stack`` indicates that the module is a ``stack``, for 
which the tests have been generated. The next key ``utg_stack_overflow`` 
is the name of the actual test_class. 

.. warning:: if the module name or test_class are inconsistent between the 
   index.yaml and actual test files, UTG will not pickup the tests. 

The string value is just a comment which serves the purpose of documentation.

Your directory structure at the end of this activity should be this

.. code-block:: console

  tests/
  ├── index.yaml
  └── stack
      └── utg_stack_overflow.py
     
You can go about adding several tests in a similiar fashion.

================
Adding new tests
================

Before adding new test cases to the framework, one needs to understand the 
conventions that are followed to ensure code compatibility. This document 
attempts to throw some light about writing such tests which comply with the 
requirements of UTG.

Naming Convention and Coding Guidelines
---------------------------------------

Test naming convention:
    The name of the test file is strictly required to comply the following 
    naming structure. The name of the test file should be as follows,
  
  ``utg_<module_name>_<test_name>.py``

    Here, the ``utg`` is to indicate that the test was written for UTG. Without 
    this, the plugin manager **will not** pickup the test file for test 
    generation. Hence, it is imperative to name the file with 
    *utg_...*. The ``module_name`` and ``test_name`` are the name of the module
    being tested and the name given to the test by the user. The user is 
    expected to give a name which reduces the effort required to comprehend 
    the test's purpose. 

    An example name would be,
  
  ``utg_decompressor_compressed_arith_insts.py``

    This name meets the requirements specified earlier. It has the ``utg`` tag 
    which enables the plugin manager to detect the file, the module name is 
    specified and the test name is clear and complements the reader's attempt to 
    discern the test's purpose.

.. note:: The name of the test file and the name of the class within the file 
   should be the same. This will be discussed in the following sections.

Coding Guidelines:
    The user is expected to stick to the guidlines stated in 
    `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_. 

    Further guidelines about specific variable naming conventions will be added. **TO-DO**

Python packages imported by the test file
-----------------------------------------
Required Packages:
  1. **Yapsy: for plugin management**.
     
     This package would have been installed when you installed utg. It is 
     necessary that you import the IPlugin class from the yapsy package in 
     your test. You can see it imported like this 
     ``from yapsy.IPlugin import IPlugin`` in the example that follows.

Optional Packages: 
  2. **re: python regular expression library**.

     This package will come of use when you try to parse the log generated by 
     running your test on your DUT using *Regular Expressions* in the 
     ``check_log()`` method of your test. If you do not wish to check the logs 
     using regular expressions, there is no need to import this package.
   
   .. note:: In the snippet that follows, we also import a module named
      ``regex_formats`` from ``utg``. This is a file which contains all the 
      regular expression formats which we would compare our logs against. 
      Currently the file has few patterns for checking Branch Predictor unit. 
      The user can add new expressions to the same file.

.. code-block:: python

    from yapsy.IPlugin import IPlugin  # class necessary from plugin management
    import regex_formats as rf         # file containing regex_patterns useful for log parsing
    import re                          # inbuilt package for regular expression matching

Python Class Name
-----------------  
The test the user wishes to generate should be returned by a method of the test
class. 

As mentioned earlier, the name of the class should be the **same** as the file. 
For instance, if the user is writing a test to check the decoding of 
*R type Arithmetic instructions* they could name the test as 
``utg_decoder_r_type_arith``. In this case, the name of the class, as well as 
the python file should **same** as the test name, i.e. 
``utg_decoder_r_type_arith``.

.. note:: The ``utg_`` label is mandatory since the plugin manager requires that 
   for picking up the test.

This test class provides features to check if the test is valid on the current 
DUT, generate the ASM files, generate cover_groups and finally, check the DUT 
log for pattern matches. These tasks are perfomed by the ``execute()``, 
``generate_asm()``, ``generate_covergroup()`` and ``check_log()`` methods of the 
class respectively.

In addition to that, it is necessary that the test class 
**inherits the IPlugin class** from the Yapsy Plugin Manager. 
This is done as follows

.. code-block:: python

   class utg_decoder_r_type_arith(IPlugin):
      """ This class generates assembly tests for checking the decoding of r-type arithmetic instructions """
      #methods follow

Now, the ``utg_decoder_r_type_arith`` class has inherited the ``IPlugin`` class 
from Yapsy. This will enable the Yapsy plugin manager to detect and pick up this 
class as a plugin when generating tests. All the tests, irrespective of the 
module/core being tested will be mounted as plugins in the UTG. Hence, importing 
the IPlugin class is paramount to the generation of the tests.

.. warning:: The ``execute``, ``generate_asm``, ``generate_covergroups`` and 
   ``check_log`` functions' implementation within the class are **mandatory**. 
   If not implemented, the program **will error out and exit**.
.. hint:: If the any aforementioned methods are not required, create an empty 
   implementation and make sure it returns its' default value. The default 
   return values are as follows, ``execute()``:``False``, 
   ``generate_asm()``:``''``, ``generate_covergroups()``:``''``, 
   ``check_log()``:``None``.

The purpose of the aforementioned functions are elucidated in the following 
sections.

__init__(self): 
---------------

.. hint:: **PYTHON-HINT**: The self variable is used to represent the instance 
   of the class which is often used in object-oriented programming. It works as 
   a reference to the object. Python uses the self parameter to refer to 
   instance attributes and methods of the class. In this guide we use the self 
   parameter to create and access methods declared across the functions within 
   the same class.


This is the constructor for the test class. 
This function can be used to specify the *self* variables which the user may 
find necessary across the other methods within the class. For example, a user 
may find a variable *xyz* initialized to a fixed value necessary in all the 
methods of their class. In such case the user may declare a *xyz* as 
``self.xyz = <some_value>`` within the init() method.

.. code-block:: python

    def __init__(self):
        """ constructor for the class """
        # The user can specify the internal variables he would need here  or leave it empty"""
        super().__init__()
        self.xyz = 5    # initialize the variables which are needed throughout the class as self.
        self.parameter_name2 = None # The self variable, like any variable, can be of any type.

execute(self, config_dict):
---------------------------
The execute method of the test class requires a dictionary (possibly extracted 
from a yaml file) as an input. The user can parse and select from this 
dictionary the parameters which would make their current test valid to be run on 
the DUT.

.. code-block:: python

    def execute(self, config_dict):
        """ Docstring explaining the rationale behind why the test was created or not based on the chosen parameters"""
        # _block_parameters( in this case config_dict) are the details of the configuration of a particular block given as a dictionary
        self._history_len = config_dict['history_len'] #self variable as _history_len will be used in other methods within the class.
        # obtain the needed external parameters from the input dictionary
        _bpu_enabled = config_dict['instantiate']

        # IMPORTANT: check for conditions in which the test needs to be generated
        if _history_len >= 1 and _bpu_enabled: # Since BPU is an optional feature, we check for it to be enabled. 
                                               # Likewise with the history_register 
          return True
        else:
          return False

The functioning of this method can be explained as follows:
   1. This function returns if the current DUT configuration has the
      necessary hardware implemented for the current test
      to be run on.
   2. Obtain the requisite parameters from the DUT configuration yaml
      file and check if the test should be generated. An example
      parameter could be 'btbdepth' in the case of a 'gshare BPU'. It is
      recommended that the user checks if the hardware unit would be
      **instantiated** before moving on to other cases.
   3. If the requisite hardware is implemented return ``True`` else
      return ``False``

Finally, it is also necessary that the user makes a copy of all the necessary
values present in the DUT configuration for running generating the tests. 
For example, when writing a test for a gshare_BPU, the user should make 
sure he creates a ``self.history_len = config_dict[history_len]`` within this 
method if he thinks he'd need the ``history_len`` somewhere in the following 
methods. **Only** the ``execute()`` method can take in the config_dict among 
all the methods of the test class.

generate_asm(self):
-------------------
This function should be written in a way that it returns a well formatted 
string, which complies with the RISC-V assembly format.

The function does not take in any arguments.

The string returned by this function will be directly written into an assembly 
file titled ``<test_class_name>.S``. Here, the test_class_name is the name of 
the class within which the generate_asm() method is present.

.. code-block:: python

    def generate_asm(self):

        """ Docstring for the generate_asm method explaining the asm code's details"""
        """ Registers used and their functions, instructions called and their purposes etc"""

        hist_len = self._history_len # we reuse the self._history_len variable here.
                                     # Since, it is not possible to access the config_dict from this method, the necessary variables
                                     # are to be stored as self variables to access across the methods of the class.
        asm = ""  # assembly code to be generated as a formatted string. It is left empty, which is the default state.
        for var_i in range(0,hist_len):
            asm = asm + "  addi x0,x0,0\n" # inserting (hist_len)x NOPs

        return asm  # generate_asm returns the assembly code as a string

The string returned from the above function contains a formatted string which 
can be directly dumped into an assembly file. The string will contain *hist_len* 
amount of *NOPs*. 

.. note:: The above snippet is just an example demostrating how to use the 
   generate_asm() method.

generate_covergroups(self, alias_dict):
---------------------------------------
This function takes in a dictionary which the user specifies. This alias_dict is 
obtained from a *yaml* file in which the user may prefer to alias the names of 
the registers, wires, inputs and outputs from the DUT whose status need to be 
monitored for coverage. This feature is provided to the user because, at times, 
the signal names generated by the bluespec compiler may be long and egregious. 
In that case, the user may alias such signals with shorter, easily graspable 
names.

The generate_covergroups(..) function, like generate_asm() will return a 
formatted string which contains all the coverpoints/assertions/covergroups which 
the user finds necessary for his test.

This string will directly be converted into ``System Verilog``. Hence, it is 
imperative that the user complies to SV formatting as necessary.

.. code-block:: python

    def generate_covergroups(self, alias_file):
        
        """ Generates SV covergroups """

        some_param = self.parameter_name1 # reuse a variable from the constructor
        sv = "" # the SV syntax to be returned. "" is the default state.
        return (sv)

This is a representation of how the generate_covergroups() method should look 
like.

check_log(self, log_file_path, reports_dir):
--------------------------------------------
The check_log() function takes in two arguments and returns ``True/False`` based 
on the presence of the pattern required by the user in the DUT logs. 
In addition to that, the method can also creates a yaml file with a report about 
the test result. The user can modify this method to even write into the yaml, 
the cause of why the log parsing failed.

The two parameters required are,
   1. log_file_path -> the path to the location where the log file generated by 
         running the test on the DUT is present.
   2. reports_dir -> the path to the directory to keep the yaml reports in.

The step-by-step functioning of check log is explained as follows
   1. Read the log file from ``log_file_path`` variable.
   2. Using the regex patterns given from the ``regex_formats.py`` file,
      and ``re`` module, parse the log file.
   3. Create conditions that test for successful execution and fail
      cases.
   4. If the assembly test passes, return ``True`` else return
      ``False``.
   5. The reports dir will contain the path where the reports from the check log 
      would be created.

.. note:: If the ``regex-formats.py`` file does not have suitable regex
   patterns, frame the regex pattern and store it in the file with
   suitable naming.

.. code-block:: python

    def check_log(self, log_file_path, reports_dir):

        """ Docstring for check_log, this function checks whether the Device under Test (DUT) has executed appropriately"""
        """
          check if all the ghr values are zero throughout the test
        """
        f = open(log_file_path, "r")  # opens the log file generated by running the test on DUT
        log_file = f.read()           # read it into a variable and close the file.
        f.close()

        # creating a YAML template which can later be updtaed based on test results.
        test_report = {
            "gshare_fa_ghr_zeros_01_report": {
                'Doc': "ASM should have generated 00000... pattern in the GHR "
                       "Register. This report show's the "
                       "results",
                'expected_GHR_pattern': None,
                'executed_GHR_pattern': None,
                'Execution_Status': None
            }
        }
        # updating the 'expected_GHR_pattern' key of the template YAML
        test_report['gshare_fa_ghr_zeros_01_report'][
            'expected_GHR_pattern'] = '0' * self._history_len 
        # default return type of the result is None.
        res = None
        # check the log file for all occurences of the required pattern. Here alloc_newind_pattern is the name of teh pattern
        # re package is used to do the comparison.
        alloc_newind_pattern_result = re.findall(rf.alloc_newind_pattern,
                                                 log_file)
        # some manipulation specific to the current case
        ghr_patterns = [
            i[-self._history_len:] for i in alloc_newind_pattern_result
        ]
        
        # update the Yaml keys with Pass/Fail as well as the number of occurences of required pattern
        for i in ghr_patterns:
            if self._history_len * '0' in i:
                test_report['gshare_fa_ghr_zeros_01_report'][
                    'executed_GHR_pattern'] = i
                test_report['gshare_fa_ghr_zeros_01_report'][
                    'Execution_Status'] = 'Pass'
                res = True
                break
            else:
                res = False
        # updating the YAML with with reasons for test failing 
        if not res:
            test_report['gshare_fa_ghr_zeros_01_report'][
                'executed_GHR_pattern'] = ghr_patterns
            test_report['gshare_fa_ghr_zeros_01_report'][
                'Execution_Status'] = 'Fail: expected pattern not found'
        # create a yaml file in the reports dir and update the results.
        f = open(
            os.path.join(reports_dir, 'gshare_fa_ghr_zeros_01_report.yaml'),
            'w')
        yaml = YAML()
        yaml.default_flow_style = False
        yaml.dump(test_report, f)
        f.close()

        return res # return if the test passed or failed.

This code-block is a representation of how a check_log method would look like. 
The user can use this as a template to write some methods of his own.

==================
Example Test Class
==================

A generic test ``utg_module_test_name.py`` is written in this manner. This test
uses the parameters from the Chromite's default configuration. We write
a test for the BPU here. Hence, we use the BPU parameters obtained from 
chromite's configuration file.

.. note:: The user should consider this as template and modify accordingly to 
   suite their needs.

.. code:: python

    """Docstring for the test explaining the objective and results"""

    from yapsy.IPlugin import IPlugin  # class necessary from plugin management
    import regex_formats as rf         # file containing regex_patterns useful for log parsing
    import re                          # inbuilt package for regular expression matching

    class utg_module_test_name(IPlugin):
      # The name of this class should be the same as the file name, i.e test_name.

      def __init__(self):
        """ constructor for the class """
        # The user can specify the internal variables he would need here """
        super().__init__()
        self.parameter_name1 = 5    # initialize the internal parameters needed for the script
        self.parameter_name2 = None

      def execute(self, config_dict):
        """ Docstring explaining the rationale behind why the test was created or not based on the chosen parameters"""
        # _block_parameters( in this case config_dict) are the details of the configuration of a particular block given as a dictionary
        self._history_len = config_dict['history_len'] #self variable as _history_len will be used in other methods within the class.
        # obtain the needed external parameters from the input dictionary
        _bpu_enabled = config_dict['instantiate']

        # IMPORTANT: check for conditions in which the test needs to be generated
        if _history_len >= 1 and _bpu_enabled: # Since BPU is an optional feature, we check for it to be enabled. 
                                               # Likewise with the history_register 
          return True
        else:
          return False

      def execute(self, config_dict):
        """ Docstring explaining the rationale behind why the test was created or not based on the chosen parameters"""
        # _block_parameters( in this case config_dict) are the details of the configuration of a particular block given as a dictionary
        self._history_len = config_dict['history_len'] #self variable as _history_len will be used in other methods within the class.
        # obtain the needed external parameters from the input dictionary
        _bpu_enabled = config_dict['instantiate']

        # IMPORTANT: check for conditions in which the test needs to be generated
        if _history_len >= 1 and _bpu_enabled: # Since BPU is an optional feature, we check for it to be enabled. 
                                               # Likewise with the history_register 
          return True
        else:
          return False  # generate_asm returns the assembly code as a string
      
      def generate_covergroups(self, alias_file):
        
        """ Generates SV covergroups """

        some_param = self.parameter_name1 # reuse a variable from the constructor
        sv = "" # the SV syntax to be returned. "" is the default state.
        return (sv)

      def check_log(self, log_file_path, reports_dir):

        """ Docstring for check_log, this function checks whether the Device under Test (DUT) has executed appropriately"""
        """
          check if all the ghr values are zero throughout the test
        """
        f = open(log_file_path, "r")  # opens the log file generated by running the test on DUT
        log_file = f.read()           # read it into a variable and close the file.
        f.close()

        # creating a YAML template which can later be updtaed based on test results.
        test_report = {
            "gshare_fa_ghr_zeros_01_report": {
                'Doc': "ASM should have generated 00000... pattern in the GHR "
                       "Register. This report show's the "
                       "results",
                'expected_GHR_pattern': None,
                'executed_GHR_pattern': None,
                'Execution_Status': None
            }
        }
        # updating the 'expected_GHR_pattern' key of the template YAML
        test_report['gshare_fa_ghr_zeros_01_report'][
            'expected_GHR_pattern'] = '0' * self._history_len 
        # default return type of the result is None.
        res = None
        # check the log file for all occurences of the required pattern. Here alloc_newind_pattern is the name of teh pattern
        # re package is used to do the comparison.
        alloc_newind_pattern_result = re.findall(rf.alloc_newind_pattern,
                                                 log_file)
        # some manipulation specific to the current case
        ghr_patterns = [
            i[-self._history_len:] for i in alloc_newind_pattern_result
        ]
        
        # update the Yaml keys with Pass/Fail as well as the number of occurences of required pattern
        for i in ghr_patterns:
            if self._history_len * '0' in i:
                test_report['gshare_fa_ghr_zeros_01_report'][
                    'executed_GHR_pattern'] = i
                test_report['gshare_fa_ghr_zeros_01_report'][
                    'Execution_Status'] = 'Pass'
                res = True
                break
            else:
                res = False
        # updating the YAML with with reasons for test failing 
        if not res:
            test_report['gshare_fa_ghr_zeros_01_report'][
                'executed_GHR_pattern'] = ghr_patterns
            test_report['gshare_fa_ghr_zeros_01_report'][
                'Execution_Status'] = 'Fail: expected pattern not found'
        # create a yaml file in the reports dir and update the results.
        f = open(
            os.path.join(reports_dir, 'gshare_fa_ghr_zeros_01_report.yaml'),
            'w')
        yaml = YAML()
        yaml.default_flow_style = False
        yaml.dump(test_report, f)
        f.close()

        return res # return if the test passed or failed.

.. hint:: User can make use of the `YAPF <https://github.com/google/yapf>`_ 
   formatter to format their test files.


Using the ``rvtest_data`` function
----------------------------------
[UNDER DEVELOPMENT]

The rvtest_data function in utg.utils assists in writing automated assembly file by populating the ``RVTEST_DATA`` section with either random values or algorithmically computed values.
The function has the following parameters.

.. code:: python

    rvtest_data(bit_width=32, num_vals=20, random=True, signed=False, align=4)

``bit_width`` is the width of data values that needs to be stored in the data section. The permitted values for bit_width are 0, 8, 16, 32, 64 and 128. For any other values the function raises exception and quits.

.. note:: if ``bit_width`` is ``0`` then the data section is populated with a single value ``0xbabecafe`` as a default string.

``num_vals`` is the number of data values that needs to be written in the data section. Any number more than 1 is valid.

``random`` is a boolean flag that denotes whether to populate random values or values computed algorithmically [UNDER DEVELOPMENT].

``signed`` is a boolean flag to determine whether to generate signed or unsigned values.

``align`` is the byte boundary that the values should be aligned to.
The function returns a string that contains the ``RVTEST_DATA`` section populated with values.

.. code-block:: python

    print(rvtest_data(bit_width=16, num_vals=2, random=True, signed=False, align=4))
    # The above line generates the following output
    # .align 4
    # RAND_VAL:
    #     .half	0xdb9b
    #     .half	0x5571
    # sample_data:
    #     .word	0xbabecafe

