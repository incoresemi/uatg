# See LICENSE.incore for license details

# [      8000] [ 0]BPU : Match:00000000
bpu_match_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sMatch\:\d{8}"

# [ 5570] [ 0]BPU : BTB Hit: BTBEntry { target: 'h00000000800003ac,
#                                        ci: Branch, instr16: False, hi: False }
btb_hit_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sBTB\sHit\:\sBTBEntry" \
                       + "\s\{\starget\:\s'h[0-9a-z]+\,\sci:\s\w*\,\sinstr16:\s\w*\,\shi\:\s\w*\s\}"

# [120] [ 0]BPU : Received Request: PredictionRequest { pc: 'h0000000000001000,
#                                   fence: False, discard: False } ghr: 00000000
pred_req_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sReceived\sRequest\:" \
                        + "\sPredictionRequest\s\{\spc\:\s'h[0-9a-z]+\,\sfence\:\s\w+\,\sdiscard\:\s" \
                        + "\w+\s\}\sghr\:\s\d+"

# [ 1240] [ 0]BPU : Received Training: Training_data { pc: 'h0000000000001010,
# target: 'h0000000080000000, state: 'h3, ci: JAL, btbhit: False, instr16: False
#                                                              , history: 'h00 }
train_data_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sReceived\s" \
                          + "Training\:\sTraining_data\s\{\spc\:\s'h[0-9a-z]+\,\starget\:\s'h[0-9a-z]+" \
                          + "\,\sstate:\s'h\d{1}\,\sci\:\s\w+\,\sbtbhit\:\s\w+\,\sinstr16\:\s\w+\," \
                          + "\shistory\:\s'h\d{2}\s\}"

# [ 5580] [ 0]BPU : Training existing Entry index:  2 ghr: 00000000
train_existing_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sTraining\sexisting\sEntry\sindex\:\s+\d+\s+ghr\:\s\d+"

# [ 5430] [ 0]BPU : Allocating new index:  1 ghr: 00000000
alloc_newind_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sAllocating\snew\s" \
                            + "index\:\s+[0-9]+\sghr\:\s\d+"

# [      7880] [ 0]BPU : Conflict Detected
conflict_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sConflict\sDetected"

# [      6320] [ 0]BPU : Pushing into RAS:00000000800003c8
pushing_to_ras_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sPushing\s" \
                              + "into\sRAS\:[0-9a-z]+"

# [      6540] [ 0]BPU : Choosing from top RAS:0000000080000404
choosing_top_ras_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sChoosing\s" \
                                + "from\stop\sRAS\:[0-9a-z]+"

# [      6000] [ 0]BPU : New GHR: 01111100
new_ghr_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sNew\sGHR\:\s\d+"

# [      5920] [ 0]BPU : BHTindex_:233 Target:0000000080000396 Pred:3
#                                                                  ghr: 11110000
bht_ind_target_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\s" \
                              + "BHTindex_\:\d+\sTarget\:\s*\d+\sPred\:\d+\sghr\:\s\d+"

# [      7950] [ 0]BPU : Misprediction fired. Restoring ghr: 01111111
misprediction_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\s" \
                             + "Misprediction\sfired\.\sRestoring\sghr\:\s\d+"

# fence executed result for log level 5
"""
[     10980] [ 0]BPU : Fenced, Valid Bits -> 0 
[     10980] [ 0]BPU : Match:00000000 
[     10980] [ 0]BPU : rg_allocate -> 00 
[     10980] [ 0]BPU : current_ghr -> 00000000 
"""
fence_executed_pattern = "(\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sFenced\," \
                         "\sValid\sBits\s\-\>\s0)(.*\n){2}(\[\s*[0-9]*\]\s\[" \
                         "\s*[0-9]*\]BPU\s\:\srg\_allocate\s\-\>\s[0-9]*\n)(" \
                         "\[\s*[0-9]*\]\s\[\s*[" \
                         "0-9]*\]BPU\s\:\scurrent_ghr\s\-\>\s0+)"
