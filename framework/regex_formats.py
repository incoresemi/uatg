bpu_match_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sMatch\:\d{8}"

btb_hit_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sBTB\sHit\:\sBTBEntry" \
+ "\s\{\starget\:\s'h[0-9a-z]+\,\sci:\s\w*\,\sinstr16:\s\w*\,\shi\:\s\w*\s\}"

pred_req_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sReceived\sRequest\:" \
+ "\sPredictionRequest\s\{\spc\:\s'h[0-9a-z]+\,\sfence\:\s\w+\,\sdiscard\:\s" \
+ "\w+\s\}\sghr\:\s\d+"

train_data_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sReceived\s"\
+ "Training\:\sTraining_data\s\{\spc\:\s'h[0-9a-z]+\,\starget\:\s'h[0-9a-z]+" \
+ "\,\sstate:\s'h\d{1}\,\sci\:\s\w+\,\sbtbhit\:\s\w+\,\sinstr16\:\s\w+\," \
+ "\shistory\:\s'h\d{2}\s\}"

train_existing_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sTraining\s"\
+ "existing\sEntry\sindex\:\s+[0-9]+\sghr\:\s\d+"

alloc_newind_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sAllocating\snew\s"\
+ "index\:\s+[0-9]+\sghr\:\s\d+"

conflict_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sConflict\sDetected"

pushing_to_ras_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sPushing\s" \
+ "into\sRAS\:[0-9a-z]+"

choosing_top_ras_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sChoosing\s" \
+ "from\stop\sRAS\:[0-9a-z]+"

new_ghr_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\sNew\sGHR\:\s\d+"

bht_ind_target_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\s" \
+ "BHTindex_\:\d+\sTarget\:\s*\d+\sPred\:\d+\sghr\:\s\d+"

misprediction_pattern = "\[\s*[0-9]*\]\s\[\s*[0-9]*\]BPU\s\:\s" \
+ "Misprediction\sfired\.\sRestoring\sghr\:\s\d+"