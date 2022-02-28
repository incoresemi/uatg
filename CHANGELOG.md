# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
