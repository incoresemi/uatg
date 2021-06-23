import ruamel
from ruamel.yaml import YAML
import os
from yapsy.PluginManager import PluginManager


def yapsy_test(test_file_dir="bpu/"):
    # specify the location where the python test files are located with a following /
    # load the plugins from the plugin directory and create the asm testfiles in a new directory
    manager = PluginManager()
    manager.setPluginPlaces([test_file_dir])
    manager.collectPlugins()
    os.makedirs(test_file_dir + "tests/", exist_ok = True)
    # Loop around and find the plugins and writes the contents from the plugins into an asm file
    for plugin in manager.getAllPlugins():
        name = (str(plugin.plugin_object).split(".",1))
        f = open('tests/tests/'+((name[1].split(" ",1))[0])+'.S',"w")
        asm = asm_header + plugin.plugin_object.generate_asm() + asm_footer
        f.write(asm)
        f.close()

def create_plugins(work_dir):
    files = os.listdir(work_dir)
    for i in files:
        if('.py' in i):
            module_name = i[0:-3]
            f = open(work_dir+'/'+module_name + '.yapsy-plugin', "w")
            f.write("[Core]\nName="+module_name+"\nModule="+module_name)
            f.close()


class branch_predictor(object):
    """Branch Predictor's parameters
        branch_predictor:
          instantiate: True //boolean value indicating if the predictor needs to be instantiated
          predictor: gshare //string indicating the type of predictor to be implemented. Valid values are: ‘gshare’
          on_reset: enable  //Indicates if the predictor should be enabled on system-reset or not.
          btb_depth: 32     //integer indicating the size of the branch target buffer
          bht_depth: 512    //integer indicating the size of the bracnh history buffer
          history_len: 8    //integer indicating the size of the global history register
          history_bits: 5   //integer indicating the number of bits used for indexing bht/btb
          ras_depth: 8      //integer indicating the size of the return address stack
      """

    def __init__(self, bpu_instance):
        super (branch_predictor, self).__init__()
        self.instantiate = bpu_instance['instantiate']
        self.predictor = bpu_instance['predictor']
        self.on_reset = bpu_instance['on_reset']
        self.btb_depth = bpu_instance['btb_depth']
        self.bht_depth = bpu_instance['bht_depth']
        self.history_len = bpu_instance['history_len']
        self.history_bits = bpu_instance['history_bits']
        self.ras_depth = bpu_instance['ras_depth']

    def print_config(self):
        print(self.instantiate, self.predictor, self.on_reset, self.btb_depth, \
        self.bht_depth, self.history_len, self.history_bits)

    def test_create():
        if(instantiate==True):
            pass

def load_yaml(foo):
    yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    try:
        with open(foo, "r") as file:
            return yaml.load(file)
    except ruamel.yaml.constructor.DuplicateKeyError as msg:
            print("error")
def main():

    inp = "../target/default.yaml" #yaml file containing the configuration details
    inp_yaml = load_yaml(inp)

    isa = inp_yaml['ISA']

    bpu = branch_predictor(inp_yaml['branch_predictor'])

    global asm_header
    global asm_footer

    asm_header = "\n#include \"model_test.h\"\n#include \"arch_test.h\"\n" \
    + "RVTEST_ISA(\""+ isa +"\")\n\n" + ".section .text.init" \
    + "\n.globl rvtest_entry_point\nrvtest_entry_point:\n" \
    + "RVMODEL_BOOT\nRVTEST_CODE_BEGIN\n\n"

    asm_footer = "\nRVTEST_CODE_END\nRVMODEL_HALT\n\nRVTEST_DATA_BEGIN" \
    + "\n.align 4\nrvtest_data:\n.word 0xbabecafe\nRVTEST_DATA_END\n"  \
    + "\nRVMODEL_DATA_BEGIN\nRVMODEL_DATA_END\n"

    create_plugins('bpu/')
    yapsy_test(test_file_dir="bpu/")

if __name__ == "__main__":
    main()
