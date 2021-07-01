# Micro-Arch-Test Framework
## Framework Structure 
The framework is structured in the following manner.

* New folders are to be created for each block that needs to be tested (e.g. ```bpu/```).
* Within each block's folder, a ```tests/``` folder is created to store the generated assembly codes. In addition, the python scripts to automate the assembly file generation are stored in the block's folder.
* For automating the test generating process, we are using ```yapsy``` module which needs a plugin file (e.g. ```test_no_1.yapsy-plugin```) created for each python script. To avoid hassle, we have automated the process of creating the plugin files too. 
  The plugin files are created when ```test_generator.py``` is called. The plugin files are ignored by git.

```shell
framework/
    ├──bpu/
    │   ├── test_no_1.py
    │   ├── test_no_2.py
    │   ├── ...
    │   ├── ...
    │   ├── ...
    │   ├── test_no_n.py
    │   ├── *(test_no_1-n).yapsy-plugin
    │   ├── log_parser.py
    │   ├── regex_formats.py
    │   └── tests/
    │      ├── test_no_1/
    |      |   ├── test_no_1.S
    |      |   ├── ...
    |      |   └── logfile
    │      ├── test_no_2/
    |      |   ├── test_no_2.S
    |      |   ├── ...
    |      |   └── logfile
    │      ├── ...
    │      ├── ...
    │      └── test_no_m/
    |          ├── test_no_m.S
    |          ├── ...
               └── logfile
    ├──block2/
    ├──block3/
    ├── ...
    ├── ...
    ├── path.txt
    ├── README.md
    └── test_generator.py
```
## Generating the tests and executing them on [RiVer Core](https://github.com/incoresemi/river_core)

Installl the required python packages. This can be done by running the command 
```shell
pip3 install -r ../requirements.txt
```
If required, the user scan replace the `dut_config.yaml` file with the configuration file of their DUT in the `micro-arch-test/target/` directory. The test generator looks for a `dut_config.yaml` in the directory. 

Now, To run the tests on RiVer Core, it is necessary that the user creates a `path.txt` file in this directory (`micro-arch-tests/framework`).

The first line of the `path.txt` file should be the path to the working directory of RiVer Core. This directory would have been created by the user while setting up RiVerCore. This directory contains the `river_core.ini` file and the the `mywork` directory. More information of how to setup RiVer Core can be found [here](https://river-core.readthedocs.io/en/stable/installation.html) 

Once the `path.txt` file is updated with the correct path to the working directory of RiVer Core, the tests can be generated and executed on RiVer Core using the command

```shell
python test_generator.py
```

This will generate the Assembly programs, invoke RiVer Core, run the tests on the preferred DUT, compare the results with the reference, and finally generate a report stating if the tests passed or not. 

In addition to RiVer Core, we also parse the log generated from the DUT using regular expressions to check if the log contains a minimal expression which should be present if the test was executed properly. It is necessary that the RiVer core's DUT plugin is suitably modified to dump the log. (By default no log is dumped by RiVer core)

This result from parsing the log is also displayed. 

## Adding new tests
Before adding new test cases to the framework, one needs to understand the conventions that are followed to ensure code compatibility and automation.

Note : The execute,generate_asm and check_log functions are necessary. If the user decides to not implement them, it is advised to return `False` from the __execute__ method. 

  1. Packages Imported by the test_generator
     1. Yapsy: for plugin management (version>=1.12.2)
     2. regex_formats: file containing regex expressions for commonly used log patterns ()
     3. re: python regular expression library


  2. Creating a class with same name as that of the test_name and initializing with default parameters that might be needed for generating the assembly program.
 
  3. Defining the `execute` function:
     1. This function returns if the current DUT configuration has the necessary hardware implemented for this(new test to be added) test to be run on.
     2. Obtain the requisite parameters from the DUT configuration yaml file and check if the test should be generated. An example parameter could be 'btbdepth' in the case of a 'gshare BPU'. It is recommended that the user checks if the harware unit would be __instantiated__ before moving on to other cases.
     3. If the requisite hardware is implemented return `True` else return `False`


  4. Defining the `generate_asm` function:
     * This function should return a formatted string. This string will be directly written as the assembly test program.  


  5. Defining the `check_log` function:
      1. Read the log file from `log_file_path` variable.
      2. Using the regex patterns given from the `regex_formats.py` file, and `re` module, parse the log file.
      3. Create conditions that test for successful execution and fail cases.
      4. If the assembly test passes, return `True` else return `False `.


  5. If the `regex-formats.py` file does not have suitable regex patterns, frame the regex pattern and store it in the file with suitable naming.

A generic test `test_name.py` is written in this manner. This test uses the parameters from the Chromite's default configuration. We write a test for the BPU here. The user should modify this test accordingly to suite their needs.

```python
"""Docstring for the test explaining the objective and results"""

from yapsy.IPlugin import IPlugin
import regex_formats as rf  # file containing regex_patterns useful for log parsing
import re

class test_name(IPlugin):

  def __init__(self):
    super().__init__()
    self.parameter_name1 = 5  # initialize the internal parameters needed for the script
    self.parameter_name2 = None

  def execute(self, _bpu_dict):
    """ Docstring explaining the rationale behind why the test was created or not based on the chosen parameters"""
    # _block_parameters( in this case _bpu_dict) are the details of the configuration of a particular block given as a dictionary
    ras_depth = _bpu_dict['ras_depth']
    # obtain the needed external parameters from the input dictionary
    _bpu_enabled = _bpu_dict['instantiate']

    # IMPORTANT: check for conditions in which the test needs to be generated
    if ras_depth >= 1 and bpu_enabled:
      return True
    else:
      return False

  def generate_asm(self):

    """ Docstring for the generate_asm method explaining the asm code's details"""
    """ Registers used and their functions, instructions called and their purposes etc"""

    recurse_level = self.parameter_name1
    asm = "assembly code to be generated in terms of string"
    return asm  # generate_asm returns the assembly code as a string

  def check_log(self, log_file_path):

    """ Docstring for check_log, this function checks whether the Device under Test (DUT) has executed appropriately"""

    f = open(log_file_path, "r")  # Reading the file from given path
    log_file = f.read()
    f.close()

    # parse the log file, extract the needed patterns.
    # based on the occurrences and frequency validate the execution
    ghr_update_result = re.findall(rf.ghr_update_pattern, log_file)

    # design your own conditions based on the need and return True if test has passed 
    if len(ghr_update_result) != 8:
      return False  # Return False if test has failed.
    return True  # Return True if test has passed.

```

