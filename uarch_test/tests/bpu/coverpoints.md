## coverpoints will be added here

All cases assume that rg_initialize is zero.

1. gshare_fa_btb_fill_01: Fills the BTB with different types of instructions. The number of instructions is dependent on the depth of the BTB
   - Coverpoint : 1. reg **rg_allocate** should change from *0 to `btb_depth -1* also check if the BTB Tags become valid. **LSB of all v_reg_btb_tag_XX should change from 0 to 1** 2. bits **2 and 3** of the v_reg_btb_entry_XX should contain 01,00,10 and 11 (across the 32 entries) 
2. gshare_fa_btb_self_modifying_01, gshare_fa_btb_fence_01: Fences the core atleast twice. 
   - Coverpoint : 1. **rg_initialize** should toggle from 0->1 2. **rg_allocate** should become zero 3. **v_reg_btb_tag_XX** should become 0 (the entire 63bit reg) 4. **rg_ghr_port1__read** should become zeros. 5. Stack will be cleared (proper signal names will be updated)
3. gshare_fa_btb_mispredict_01: makes sure there was atleast one misprediction
   - Coverpoint : 1. MSB of reg **ma_mispredict_g** should be 1 atleast once. When, the MSB is one, the MSB-1 bit of the register should be toggled.
4. gshare_fa_ras_push_pop: ToDo
