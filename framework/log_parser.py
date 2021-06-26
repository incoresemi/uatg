import re
from regex_formats import *


def main():
    f = open('../asm_tests/build/log', "r")
    log_file = f.read()

    bpu_match_result = re.findall(bpu_match_pattern, log_file)
    btb_hit_result = re.findall(btb_hit_pattern, log_file)
    pred_req_result = re.findall(pred_req_pattern, log_file)
    train_data_result = re.findall(train_data_pattern, log_file)
    train_existing_result = re.findall(train_existing_pattern, log_file)
    alloc_newind_result = re.findall(alloc_newind_pattern, log_file)
    conflict_result = re.findall(conflict_pattern, log_file)
    pushing_to_ras_result = re.findall(pushing_to_ras_pattern, log_file)
    choosing_top_ras_result = re.findall(choosing_top_ras_pattern, log_file)
    new_ghr_result = re.findall(new_ghr_pattern, log_file)
    bht_ind_target_result = re.findall(bht_ind_target_pattern, log_file)
    misprediction_result = re.findall(misprediction_pattern, log_file)
    fence_executed_result = re.findall(fence_executed_pattern, log_file)
    f.close()
    
    for i in bpu_match_result:
        print(i)


if __name__ == '__main__':
    main()
