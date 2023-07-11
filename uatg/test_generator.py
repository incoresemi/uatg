# See LICENSE.incore for license details

from datetime import datetime
from getpass import getuser
from glob import glob
from multiprocessing import Pool, Manager
from os import mkdir, makedirs, remove
from os.path import join, dirname, abspath, exists, isdir, isfile
from shutil import rmtree, copyfile
from sys import exit

from ruamel.yaml import dump
from yapsy.PluginManager import PluginManager, PluginInfo

from uatg import __file__
from uatg.log import logger
from uatg.utils import create_plugins, generate_test_list, create_linker, \
    create_model_test_h, join_yaml_reports, generate_sv_components, \
    list_of_modules, rvtest_data, dump_makefile, setup_pages, \
    select_paging_modes, macros_parser

# create a manager for shared resources
process_manager = Manager()


def asm_generation_process(args):
    """
        for every plugin, a process shall be spawned.
        The new process shall create an Assembly test file.
    """
    # unpacking the args tuple
    plugin, config_dict, isa, test_format_string, work_tests_dir, \
    make_file, module, linker_dir, uarch_dir, work_dir, \
    compile_macros_dict, self_checking_dict, module_test_count_dict, page_modes = args

    # actual generation process
    check = plugin.plugin_object.execute(config_dict)

    name = (str(plugin.plugin_object).split(".", 1))
    t_name = ((name[1].split(" ", 1))[0])

    # data section for paging pages
    priv_asm_code = ['', '', '']
    priv_asm_data = ""

    if check:
        test_gen = plugin.plugin_object.generate_asm()

        seq = '001'
        for ret_list_of_dicts in test_gen:
            test_name = t_name + '-' + seq

            assert isinstance(ret_list_of_dicts, dict)
            # Checking for the returned sections from each test
            asm_code = ret_list_of_dicts['asm_code']

            try:
                if ret_list_of_dicts['name_postfix']:
                    inst_name_postfix = '-' + ret_list_of_dicts['name_postfix']
                else:
                    inst_name_postfix = ''
            except KeyError:
                inst_name_postfix = ''

            # add inst name to test name as postfix
            test_name = test_name + inst_name_postfix
            logger.debug(f'Selected test: {test_name}')

            try:
                asm_data = ret_list_of_dicts['asm_data']
            except KeyError:
                asm_data = rvtest_data(bit_width=0, num_vals=1, random=True)

            try:
                asm_sig = ret_list_of_dicts['asm_sig']
            except KeyError:
                asm_sig = '\n'

            # create an entry in the compile_macros dict
            if 'rv64' in isa.lower():
                compile_macros_dict[test_name] = ['XLEN=64']
            else:
                compile_macros_dict[test_name] = ['XLEN=32']
            
            # if self_checking is included in returned dictionary, set the value accordingly
            # else, default it to False
            try:
                self_checking_dict[test_name] = ret_list_of_dicts['self_checking']
            except KeyError:
                self_checking_dict[test_name] = False

            list_of_env_paths = [join(dirname(__file__), 'env/arch_test_unpriv.h'),
                                 join(dirname(__file__), 'env/arch_test_priv.h')]
            
            try:
                available_macros = macros_parser(list_of_env_paths)
                for i in ret_list_of_dicts['compile_macros']:
                    if i not in available_macros:
                        logger.error(f'{i}: Macro undefined in arch_test.h ')
                        raise Exception('Undefined Macro')
                        exit()
                compile_macros_dict[test_name] += ret_list_of_dicts[
                    'compile_macros']
            except KeyError:
                logger.debug(f'No custom Compile macros specified for '
                             f'{test_name}')

            # generate and setup page tables based on info from plugin
            privileged_dict = {'page_size': 4096,
                               'll_pages': 64,
                               'paging_mode': 'sv39',
                               'mode': 'machine',
                               'enable': False}
            try:
                privileged_dict = ret_list_of_dicts['privileged_test']
            except KeyError:
                privileged_dict['enable'] = False
            
            # check to add privileged_test macro in compile macros list

            if privileged_dict['enable'] == True or \
               ('rvtest_mtrap_routine' in compile_macros_dict[test_name]) or \
               ('rvtest_strap_routine' in compile_macros_dict[test_name]):
                   logger.debug('This test is a privileged test. Including arch_test_priv header')
                   compile_macros_dict[test_name] += ['privileged_test_enable']

            try:
                pt_fault = privileged_dict['fault']
            except KeyError:
                logger.debug("test does not generate a PT fault")
                pt_fault = False
                pass

            try:
                pt_mem_fault = privileged_dict['mem_fault']
            except KeyError:
                pt_mem_fault = False
                pass

            try:
                pte_bit_dict = privileged_dict['pte_dict']
            except KeyError:
                pte_bit_dict = None
                pass

            try:
                pt_megapage = privileged_dict['megapage']
            except KeyError:
                pt_megapage = False
                pass

            try:
                pt_gigapage = privileged_dict['gigapage']
            except KeyError:
                pt_gigapage = False
                pass

            try:
                pt_terapage = privileged_dict['terapage']
            except KeyError:
                pt_terapage = False
                pass

            try:
                pt_petapage = privileged_dict['petapage']
            except KeyError:
                pt_petapage = False
                pass

            try:
                pt_user_superpage = privileged_dict['user_superpage']
            except KeyError:
                pt_user_superpage = False
                pass

            try:
                pt_user_supervisor_superpage = privileged_dict['user_supervisor_superpage']
            except KeyError:
                pt_user_supervisor_superpage =  False
                pass

            try:
                pt_misaligned_superpage = privileged_dict['misaligned_superpage']
            except KeyError:
                pt_misaligned_superpage = False
                pass

            required_paging_modes = select_paging_modes(page_modes)
            current_paging_mode = privileged_dict['paging_mode']

            if privileged_dict['enable']:
                if (privileged_dict['paging_mode'] == 'sv39') and \
                        (privileged_dict['mode'] == 'machine'):
                    current_paging_mode = required_paging_modes[0]

                if current_paging_mode in required_paging_modes:
                    logger.debug(f"{current_paging_mode} is in user listed " \
                                 "paging modes")
                    priv_asm_code, priv_asm_data = setup_pages(
                        pte_dict=pte_bit_dict,
                        page_size=privileged_dict['page_size'],
                        paging_mode=current_paging_mode,
                        valid_ll_pages=privileged_dict['ll_pages'],
                        mode=privileged_dict['mode'],
                        megapage=pt_megapage,
                        gigapage=pt_gigapage,
                        terapage=pt_terapage,
                        petapage=pt_petapage,
                        user_superpage=pt_user_superpage,
                        user_supervisor_superpage=pt_user_supervisor_superpage,
                        fault=pt_fault,
                        mem_fault=pt_mem_fault,
                        misaligned_superpage=pt_misaligned_superpage
                    )

                else:
                    logger.warning(
                        f'{current_paging_mode} is not in user listed' \
                        ' paging modes')
                    logger.warning(f'skipping test generation for {test_name}')
                    continue

            # Adding License, includes and macros
            # asm = license_str + includes + test_entry
            asm = (test_format_string[0] + test_format_string[1] +
                   test_format_string[2])

            # Appending Coding Macros & Instructions
            # asm += rvcode_begin + asm_code + rvcode_end

            asm += test_format_string[3] + priv_asm_code[0] + \
                   priv_asm_code[1] + asm_code + \
                   priv_asm_code[2] + test_format_string[4]

            # Appending RVTEST_DATA macros and data values
            # asm += rvtest_data_begin + asm_data + rvtest_data_end
            asm += test_format_string[5] + asm_data + priv_asm_data + \
                   test_format_string[6]

            # Appending RVMODEL macros
            # asm += rvmodel_data_begin + asm_sig + rvmodel_data_end

            asm += test_format_string[7] + asm_sig + \
                   test_format_string[8]

            mkdir(join(work_tests_dir, test_name))
            with open(join(work_tests_dir, test_name, test_name + '.S'),
                      'w') as f:
                f.write(asm)
            seq = '%03d' % (int(seq, 10) + 1)
            logger.debug(f'Generating test for {test_name}')

            try:
                make_file[module].append(test_name)

            except KeyError:
                make_file[module] = process_manager.list([test_name])

            make_file['tests'].append(
                (test_name,
                 dump_makefile(isa=isa,
                               link_path=linker_dir,
                               test_path=join(work_tests_dir, test_name,
                                              test_name + '.S'),
                               test_name=test_name,
                               compile_macros=compile_macros_dict[test_name],
                               env_path=join(uarch_dir, 'env'),
                               work_dir=work_dir)))

        module_test_count_dict[f'{t_name}'] = (int(seq)) - 1

    else:
        logger.warning(f'{t_name} is not valid for the current core '
                       'configuration')

    logger.debug(f'Finished Generating Assembly Files for {t_name}')

    return True


def sv_generation_process(args):
    """
        for every plugin, a process shall be spawned.
        The process shall generate System Verilog coverpoints
    """
    # unpack the args
    plugin = args[0]
    config_dict = args[1]
    alias_dict = args[3]
    cover_list = args[4]

    _check = plugin.plugin_object.execute(config_dict)
    _name = (str(plugin.plugin_object).split(".", 1))
    _test_name = ((_name[1].split(" ", 1))[0])
    if _check:
        try:
            _sv = plugin.plugin_object.generate_covergroups(alias_dict)
            cover_list.append(_sv)
            logger.debug(f'Generating coverpoints SV file for {_test_name}')

        except AttributeError:
            logger.warn(f'Skipping coverpoint generation for {_test_name} as '
                        f'there is no gen_covergroup method ')
            pass

    else:
        logger.critical(f'Skipped {_test_name} as this test is not '
                        f'created for the current DUT configuration ')

    return True


def generate_tests(work_dir, linker_dir, modules, config_dict, test_list,
                   modules_dir, index_path, paging_modes, jobs):
    """
    The function generates ASM files for all the test classes specified within
    the module_dir. The user can also select the modules for which he would want
    the tests to be generated for. The YAPSY plugins for the tests are generated
    by the function automatically.

    The tests are created within the work directory passed by the user. A
    test_list is also created in the yaml format by the function. The test
    generator also creates a linker file as well as the header files for running
    the ASM files on the DUT, when required. Finally, the test generator only
    generates the tests whose targets are implemented in the DUT.
    """
    uarch_dir = dirname(__file__)

    if work_dir:
        pass
    else:
        work_dir = abspath((join(uarch_dir, '../work/')))

    makedirs(work_dir, exist_ok=True)

    logger.info(f'uatg dir is {uarch_dir}')
    logger.info(f'work_dir is {work_dir}')
    isa = 'RV64I'
    # yaml file containing the ISA parmaeters of the DUT
    isa_yaml = config_dict['isa_dict']
    try:
        isa = isa_yaml['hart0']['ISA']
    except Exception as e:
        logger.error(e)
        logger.error('Exiting UATG. ISA cannot be found/understood')
        exit(0)

    logger.info('The modules are {0}'.format((', '.join(modules))))

    # creating a shared dictionary which can be accessed by all processes
    # stores the makefile commands

    make_file = process_manager.dict({
        'all': modules,
        'tests': (process_manager.list())
    })

    # creating a shared dict to store test_list info
    # test_list_dict = process_manager.dict()
    test_list_dict = {}

    # creating a shared compile_macros dict
    # this dictionary will contain all the compile macros for each test
    compile_macros_dict = process_manager.dict()

    # Create a shared self_checking flag dict
    # this dictionary will store the status of self_check flag for each test
    self_checking_dict = process_manager.dict()

    if exists(join(work_dir, 'makefile')):
        remove(join(work_dir, 'makefile'))

    logger.info('****** Generating Tests ******')

    total_test_count_dict = {}

    for module in modules:

        # creating a shared list to display the number of tests generated
        # per module
        module_test_count_dict = process_manager.dict()

        module_dir = join(modules_dir, module)
        work_tests_dir = join(work_dir, module)

        # initializing make commands for individual modules

        logger.debug(f'Directory for {module} is {module_dir}')
        logger.info(f'Starting plugin Creation for {module}')
        create_plugins(plugins_path=module_dir,
                       index_yaml=index_path,
                       module=module)
        logger.info(f'Created plugins for {module}')
        username = getuser()
        time = ((str(datetime.now())).split("."))[0]
        license_str = f'# Licensing information can be found at ' \
                      f'LICENSE.incore\n# Test generated by user - {username}' \
                      f' at {time}\n\n'
        includes = f'#include \"model_test.h\" \n#include \"arch_test_unpriv.h\"\n'
        test_entry = f'RVTEST_ISA(\"{isa}\")\n\n.section .text.init\n.globl' \
                     f' rvtest_entry_point\nrvtest_entry_point:'

        rvcode_begin = '\nRVMODEL_BOOT\nRVTEST_CODE_BEGIN\n'
        rvcode_end = '\nRVTEST_CODE_END\nRVMODEL_HALT\n\n'
        rvtest_data_begin = '\nRVTEST_DATA_BEGIN\n'
        rvtest_data_end = '\nRVTEST_DATA_END\n\n'
        rvmodel_data_begin = '\nRVMODEL_DATA_BEGIN\n'
        rvmodel_data_end = '\nRVMODEL_DATA_END\n\n'

        # This function adds module directory to python path
        def add_module_to_path(plugin_info):
            import sys
            from os.path import dirname
            sys.path.insert(0, dirname(plugin_info.path))

        manager = PluginManager()
        logger.debug('Loaded PluginManager')
        manager.setPluginPlaces([module_dir])
        # plugins are stored in module_dir
        manager.locatePlugins()
        
        # passing add_module_to_path to callback ensures the run of the function
        # before the plugin is loaded
        x = manager.loadPlugins(callback=add_module_to_path)
        error_status = [i.error for i in x if i.error is not None]

        if len(error_status) > 0:
            for i in error_status:
                logger.error(str(i[0]) + ' : ' + str(i[1]))
            exit('Python Errors at one/multiple files')

        # check if prior test files are present and remove them. create new dir.
        if (isdir(work_tests_dir)) and \
                exists(work_tests_dir):
            rmtree(work_tests_dir)

        mkdir(work_tests_dir)

        logger.info(f'Generating assembly tests for {module}')

        # test format strings
        test_format_string = [
            license_str, includes, test_entry, rvcode_begin, rvcode_end,
            rvtest_data_begin, rvtest_data_end, rvmodel_data_begin,
            rvmodel_data_end
        ]

        # Loop around and find the plugins and writes the contents from the
        # plugins into an asm file
        arg_list = []
        for plugin in manager.getAllPlugins():
            arg_list.append(
                (plugin, config_dict, isa, test_format_string,
                 work_tests_dir, make_file, module, linker_dir, uarch_dir,
                 work_dir, compile_macros_dict, self_checking_dict, module_test_count_dict,
                 paging_modes))

        # multi processing process pool
        logger.info(f"Spawning {jobs} processes")
        process_pool = Pool(jobs)
        # creating a map of processes
        process_pool.map(asm_generation_process, arg_list)
        process_pool.close()

        logger.info('\n****** Count of assembly tests generated (per plugin) '
                    f'for {module} ******')

        s_no = 1
        for k, v in module_test_count_dict.items():
            logger.info(f'{s_no} | {k} : {v}')
            s_no = s_no + 1

        total_test_count_dict[f'{module}'] = sum(
            [v for v in module_test_count_dict.values()])
        logger.info(
            f'\nTotal number of tests generated for {module} : '
            f'{total_test_count_dict[module]}\n\n')

        logger.info(f'Finished Generating Assembly Tests for {module}')

        if test_list:
            logger.info(f'Creating test_list for the {module}')
            test_list_dict.update(
                generate_test_list(work_tests_dir, uarch_dir, module_dir, isa,
                                   test_list_dict, compile_macros_dict, self_checking_dict))

    logger.info('Assembly generation for all modules completed')

    with open(join(work_dir, 'makefile'), 'w') as f:
        logger.info('Dumping makefile')
        f.write('all' + ': ')
        f.write(' \\\n\t'.join(make_file['all']))
        f.write('\n')
        for i in modules:
            f.write(i + ': ')
            try:
                f.write(' \\\n\t'.join(make_file[i]))
            except KeyError:
                logger.critical(f"\"{i}\" is a part of the module list. \n"
                                f"But, No tests were generated by UATG for "
                                f"module \"{i}\"")
                logger.critical("If this was uninteded, "
                                "Please enable the required test(s) in the "
                                "index.yaml file")
            f.write('\n')
        f.write('\n')
        for i in make_file['tests']:
            f.write(i[0] + ': \n\t')
            f.write(i[1] + '\n')

    if linker_dir and isfile(join(linker_dir, 'link.ld')):
        logger.info('Using user specified linker: ' +
                    join(linker_dir, 'link.ld'))
        copyfile(join(linker_dir, 'link.ld'), work_dir + '/link.ld')
    else:
        create_linker(target_dir=work_dir)
        logger.info(f'Creating a linker file at {work_dir}')

    if linker_dir and isfile(join(linker_dir, 'model_test.h')):
        logger.info('Using user specified model_test file: ' +
                    join(linker_dir, 'model_test.h'))
        copyfile(join(linker_dir, 'model_test.h'), work_dir + '/model_test.h')
    else:
        create_model_test_h(target_dir=work_dir)
        logger.info(f'Creating Model_test.h file at {work_dir}')
    if test_list:
        logger.info('Test List was generated by UATG. You can find it in '
                    f'the work dir{work_dir}')
        with open(join(work_dir, 'test_list.yaml'), 'w') as outfile:
            dump(test_list_dict, outfile)
    else:
        logger.info('Test list will not be generated by uatg')

    logger.info('\n****** Number of tests generated (per module) '
                'by UATG ******')

    s_no = 1
    for k, v in total_test_count_dict.items():
        logger.info(f'{s_no} | {k} - {v}')
        s_no = s_no + 1

    logger.info(
        f'\nTotal number of tests generated by UATG in this run : '
        f'{sum([v for v in total_test_count_dict.values()])}\n\n')

    logger.info('****** Finished Generating Tests and other dependencies'
                ' ******')


def generate_sv(work_dir, config_dict, modules, modules_dir, alias_dict, jobs):
    """
    The generate_sv function dumps the covergroups written by the user into a
    'coverpoints.sv' file present within the 'sv_top' directory within the work
    directory.
    This function dumps into an SV file only if the test_class contains the
    generate_covergroups method. This function, like generate_asm also allows to
    select the modules for which covergroups are to be generated.
    In addition, the method also takes in an alias_dict which can be used to
    alias the BSV signal names to something even more comprehensible.
    """
    uarch_dir = dirname(__file__)

    if work_dir:
        pass
    else:
        work_dir = abspath((join(uarch_dir, '../work/')))

    # yaml containing ISA parameters of DUT
    isa_yaml = config_dict['isa_dict']
    logger.info('****** Generating Covergroups ******')

    sv_dir = join(work_dir, 'sv_top')
    makedirs(sv_dir, exist_ok=True)

    # generate the tbtop and interface files
    generate_sv_components(sv_dir, alias_dict)
    logger.debug("Generated tbtop, defines and interface files")
    sv_file = join(sv_dir, 'coverpoints.sv')

    if isfile(sv_file):
        logger.debug("Removing Existing coverpoints SV file")
        remove(sv_file)

    # create a shared list for storing the coverpoints
    cover_list = process_manager.list()

    for module in modules:
        logger.debug(f'Generating CoverPoints for {module}')

        module_dir = join(modules_dir, module)

        # yaml file with core parameters
        core_yaml = config_dict['core_config']

        manager = PluginManager()
        manager.setPluginPlaces([module_dir])
        manager.locatePlugins()
        x = manager.loadPlugins()
        error_status = [i.error for i in x if i.error is not None]

        if len(error_status) > 0:
            for i in error_status:
                logger.error(str(i[0]) + ' : ' + str(i[1]))
            exit('Python Errors at one/multiple files')

        # Loop around and find the plugins and writes the contents from the
        # plugins into an asm file
        arg_list = []
        for plugin in manager.getAllPlugins():
            arg_list.append(
                (plugin, core_yaml, isa_yaml, alias_dict, cover_list))

        # multi processing process pool
        logger.debug(f"Spawning {jobs} processes")
        process_pool = Pool(jobs)
        # creating a map of processes
        process_pool.map(sv_generation_process, arg_list)
        process_pool.close()

        logger.debug(f'Finished Generating Coverpoints for {module}')

    with open(sv_file, 'w') as f:
        logger.info('Dumping the covergroups into SV file')
        f.write('\n'.join(cover_list))

    logger.info('****** Finished Generating Covergroups ******')


def validate_tests(modules, config_dict, work_dir, modules_dir):
    """
       Parses the log returned from the DUT for finding if the tests
       were successful.
       The user should have created regular expressions for the patterns he's
       expecting to be seen in the log generated by the DUT.
       In addition to just the checking, it can also be set up to provide a
       report for every test for which the user tries to validate.
    """

    uarch_dir = dirname(__file__)

    logger.info('****** Validating Test results, Minimal log checking ******')

    if modules == ['all']:
        logger.debug(f'Checking {modules_dir} for modules')
        modules = list_of_modules(modules_dir)
        # del modules[-1]
        # Needed if list_of_modules returns 'all' along with other modules
    if work_dir:
        pass
    else:
        work_dir = abspath((join(uarch_dir, '../work/')))

    _pass_ct = 0
    _fail_ct = 0
    _tot_ct = 1

    for module in modules:
        module_dir = join(modules_dir, module)
        # module_tests_dir = join(module_dir, 'tests')
        work_tests_dir = join(work_dir, module)
        reports_dir = join(work_dir, 'reports', module)
        makedirs(reports_dir, exist_ok=True)
        # YAML with ISA paramters
        core_yaml = config_dict['core_config']
        # isa yaml with ISA paramters
        isa_yaml = config_dict['isa_dict']
        manager = PluginManager()
        manager.setPluginPlaces([module_dir])
        manager.locatePlugins()
        x = manager.loadPlugins()
        error_status = [i.error for i in x if i.error is not None]

        if len(error_status) > 0:
            for i in error_status:
                logger.error(str(i[0]) + ' : ' + str(i[1]))
            exit('Python Errors at one/multiple files')

        logger.debug(f'Minimal Log Checking for {module}')

        for plugin in manager.getAllPlugins():
            _name = (str(plugin.plugin_object).split(".", 1))
            _test_name = ((_name[1].split(" ", 1))[0])
            _check = plugin.plugin_object.execute(core_yaml, isa_yaml)
            _log_file_path = join(work_tests_dir, _test_name, 'log')
            if _check:
                try:
                    _result = plugin.plugin_object.check_log(
                        _log_file_path, reports_dir)
                    if _result:
                        logger.info(f'{_tot_ct}. Minimal test: {_test_name} '
                                    f'has passed.')
                        _pass_ct += 1
                        _tot_ct += 1
                    else:
                        logger.critical(f"{_tot_ct}. Minimal test: "
                                        f"{_test_name} has failed.")
                        _fail_ct += 1
                        _tot_ct += 1
                except FileNotFoundError:
                    logger.error(f'Log for {_test_name} not found. Run the '
                                 f'test on DUT and generate log or check '
                                 f'the path.')
            else:
                logger.warn(f'No asm generated for {_test_name}. Skipping')
        logger.debug(f'Minimal log Checking for {module} complete')

    logger.info("Minimal Verification Results")
    logger.info("=" * 28)
    logger.info(f"Total Tests : {_tot_ct - 1}")

    if _tot_ct - 1:
        logger.info(f"Tests Passed : {_pass_ct} - "
                    f"[{_pass_ct // (_tot_ct - 1)} %]")
        logger.warn(f"Tests Failed : {_fail_ct} - "
                    f"[{100 * _fail_ct // (_tot_ct - 1)} %]")
    else:
        logger.warn("No tests were created")

    logger.info('****** Finished Validating Test results ******')
    join_yaml_reports(work_dir)
    logger.info('Joined Yaml reports')


def clean_dirs(work_dir, modules_dir):
    """
    This function cleans the files generated by UATG.
    Presently it removes __pycache__, work_dir directory and also removes
    the '.yapsy plugins' files in the module's directories.
    """
    uarch_dir = dirname(__file__)
    if work_dir:
        pass
    else:
        work_dir = abspath((join(uarch_dir, '../work/')))

    module_dir = join(work_dir, '**')
    # module_tests_dir = join(module_dir, 'tests')

    logger.info('****** Cleaning ******')
    logger.debug(f'work_dir is {module_dir}')
    yapsy_dir = join(modules_dir, '**/*.yapsy-plugin')
    pycache_dir = join(modules_dir, '**/__pycache__')
    logger.debug(f'yapsy_dir is {yapsy_dir}')
    logger.debug(f'pycache_dir is {pycache_dir}')
    tf = glob(module_dir)
    pf = glob(pycache_dir) + glob(join(uarch_dir, '__pycache__'))
    yf = glob(yapsy_dir, recursive=True)
    logger.debug(f'removing {tf}, {yf} and {pf}')
    for element in tf + pf:
        if isdir(element):
            rmtree(element)
        else:
            remove(element)

    for element in yf:
        remove(element)
    logger.info("Generated Test files/folders removed")
