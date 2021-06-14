## Simple program which loops 15 times. 
## When the GHR width is 8, there will be 8 mispredictions as the Predictor warms up
## After 8 mis predictions, the predictions will be correct except the final prediction when t1 equals 15. 
      addi t0,x0,15
      addi t1,x0,0
loop: 
      addi t1,t1,1
      blt  t1,t0,loop
      
      add  t2,t0,t1
## label_start: 
##   bge  t1,t0, label_end
##   addi t1,t1,1
##   add  t3,t1,x0
##   jal  x0,label_start
##   label_end:
##   add t2,t1,t0   
