# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.13.1] - 2023-12-9
- patch to revert back click version constriant

## [1.13.0] - 2023-11-16
- march generation to account for Smrnmi in isa string

## [1.12.2] - 2023-11-16
- Added python-constraint to requirements

## [1.12.1] - 2023-11-10
- Forced click to 7.0.0

## [1.12.0] - 2023-09-27
- Added function to return rs1,rs2 and rd values to pbox saturating mul instructions plugin
- Added condition to check if the plugin name starts with "uatg_" in utils.py

## [1.11.0] - 2023-09-20
- Added psimd instruction dictionary to instruction_constants.py
- Added methods to return ASM strings for instructions with couple registers
 
## [1.10.0] - 2023-06-6
- Execute method for UATG plugins to take not only ispec and cspec but all config files
- Removed `Zicsr` filter while populating test_list

## [1.9.0] - 2023-04-25
- Added feature that checks for self-checking flag in plugins and accordingly updates the test list

## [1.8.0] - 2023-03-30
- Added functions that generate special lists of binaries for bit marcher, pattern walk, alternate 0s and 1s and
  signed specials

## [1.7.0] - 2023-03-29
- added functions in instruction_constants.py to generate ASM strings for various instruction sequences

## [1.6.0] - 2022-11-25
- fix march and mabi generation

## [1.5.1] - 2022-09-08
- path added to MANIFEST.in to include isem.yaml 

## [1.5.0] - 2022-05-06
- UATG can generate tests with all possible page table configurations.
- UATG can generate aligned and misaligned superpages
- UATG now verifies if the ``compile macros`` listed by the plugin are legal before generating the test list
- split the arch_test header into privileged and unprivileged header files
- interrupt handling capability in trap handler
- new supervisor trap handler
- page fault handling in trap handler(s)

## [1.4.2] - 2022-03-02
- updates to trap handler
- fixes to instruction constants

## [1.4.1] - 2022-02-28
- fix bug with configuration yaml CLI
- update colorlog requirement
- update pypi package requirements for docs generation
- minor cleanup

## [1.4.0] - 2022-02-25
- Reduce memory usage by using generators in the plugins.
- UATG will display the number of tests generated per module and in total.
- Feature to generate config.ini with valid paths using ``uatg setup``.
- Support for custom index.yaml file.
- Individual entries for core configuration YAMLs in config.ini
- ``test_compile`` node in config.ini to enable dry compile runs of generated assembly.
- ``jobs`` node in config.ini to control the number of processes spawned.
- make paths in generated test-list absolute.
- add macros and utility functions to run and generate supervisor/user tests.
- fix issue with displaying plugin syntax errors (YAPSY).
- add instruction generator.
- fix multiple bugs.
- minor updates to the trap handler.
- minor documentation

## [1.3.0] - 2021-11-24
- Fix docs
- Add multi-processing support at the test plugin level.
- Add Assembly Syntax checking feature through makefile.
- Add illegal opcode generation functions.
- Add 'A' extesion instructions in instruction constants

## [1.2.1] - 2021-10-28
- update click version

## [1.2.0] - 2021-10-27
- documentation.
- feature to use index.yaml for test selection.
- update instruction constants.
- add custom minimal trap handler for illegal insts and misaligned access.
- add feature to generate multiple tests from one plugin.
- update test_list generation for compile macros and march.
- Fix generate_asm return types for rvtest_data, name_postfix and signature.

## [1.1.0] - 2021-09-24
- add support for updated chromite's config YAMLs
- update documentation for the new changes 

## [1.0.2] - 2021-09-18
- update readthedocs link

## [1.0.1] - 2021-09-16
- update links to chromite_uatg_tests

## [1.0.0] - 2021-09-15
- initial release of the UATG framework.
