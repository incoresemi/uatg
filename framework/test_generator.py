import ruamel
from ruamel.yaml import YAML
from asm_gen import *
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

inp = "config.yaml" #yaml file containing the configuration details
inp_yaml = load_yaml(inp)
bpu = branch_predictor(inp_yaml['branch_predictor'])
bpu.print_config()
