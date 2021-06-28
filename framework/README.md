#Framework structure
The framework is structured in the following manner.

* New folders are to be created for each block that needs to be tested (e.g. ```bpu/```).
* Within each block's folder, a ```tests/``` folder is created to store the generated assembly codes. In addition, the python scripts to automate the assembly file generation are stored in the block's folder.
* For automating the test generating process, we are using ```yapsy``` module which needs a plugin file (e.g. ```test_no_1.yapsy-plugin```) created for each python script. To avoid hassle, we have automated the process of creating the plugin files too. 
  The plugin files are created when ```test_generator.py``` is called. The plugin files are ignored by git.

```shell
Framework/
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
    │      ├── test_no_1.S
    │      ├── test_no_2.S
    │      ├── ...
    │      ├── ...
    │      └── test_no_m.S
    ├── README.md
    └── test_generator.py
```

## Adding new tests
Before adding new test cases to the framework, one needs to understand the conventions that are followed to ensure code compatibility and automation.

A generic test ```test_name.py``` is written in this manner. 

```python
"""Docstring for the test explaining the objective and results""" 

from yapsy.IPlugin import IPlugin
import regex_formats as rf  #file containing regex_patterns useful for log parsing
import re


class test_name(IPlugin):

    def __init__(self):
        self.parameter_name1 = 5  #initialize the internal parameters needed for the script
        self.parameter_name2 = None

    def generate_asm(self, _bpu_dict):
        
        """ Docstring for the generate_asm method explaining the asm code's details"""
        """ Registers used and their functions, instructions called and their purposes etc"""
        
        #_block_parameters( in this case _bpu_dict) are the details of the configuration of a particular block given as a dictionary
        ras_depth = _bpu_dict['ras_depth']  #obtain the needed external parameters from the input dictionary
        bpu_enabled = _bpu_dict['instantiate']
        
        
        #IMPORTANT: check for conditions in which the test needs to be generated
        if ras_depth>=1 and bpu_enabled: 
            recurse_level = self.parameter_name1
            asm = "assembly code to be generated in terms of string"
            return asm # generate_asm returns the assembly code as a string

        else:
            return 0 #if the test is not needed to be generated return 0

    def check_log(self, log_file_path):
        
        """ Docstring for check_log, this function checks whether the Device under Test (DUT) has executed appropriately"""
        
        f = open(log_file_path, "r") #Reading the file from given path
        log_file = f.read()
        f.close()
        
        #parse the log file, extract the needed patterns.
        #based on the occurences and frequency validate the execution
        ghr_update_result = re.findall(rf.ghr_update_pattern, log_file)

        #design your own conditions based on the need and return True if test has passed 
        if len(ghr_update_result) != 8 and \
                len(choosing_top_ras_result) != 4:
            return False #Return False if test has failed.

        return True #Return True if test has passed.

```