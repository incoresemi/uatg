
.. _overview:

========
Overview
========

Micro Arch Tests or ``uarch_test`` or ``utg`` is a framework build at InCore to generate RISC-V Assembly tests for functionally verfiying the cores designed in house. Uarch-tests generates the Assembly files by invoking several python scripts containing the Assembly syntax for the specific tests. 

Micro-arch-tests also supports the generation of SV Coverpoints for the test using the syntax specified in the python scripts generating the test. 

The python scripts used for test generation can be found in the uarch_modules repository. The micro-arch-tests makes use of the scripts in that repo to generate the tests as well as SV covergroups.

The tests generated using Uarch-test can be run on the DUT in the conventional way or by using a framework like `RiVer Core <https://github.com/incoresemi/river_core>`_. RiVer Core would automatically use the utg plugin to generate the tests, run it on the DUT, obtain coverage as well as compare the logs from DUT and a refernce and provide a comprehensive report of your test's results. 

Steps to install and run the tests can be found in the ``quickstart`` section of this document. Steps to create tests can be found here in the ``Micro-Arch-Test Framework`` section. 
