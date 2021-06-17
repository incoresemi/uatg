#python script to automate test 11 in microarch test

def gshare_fa_ras_push_pop_01(recurse_level=31):

    asm = 'call x1, lab1\n\n'
    for i in range(1, recurse_level+1):
        asm += 'lab' + str(i) + ':\n'
        asm += '\tnop\n\tcall x' + str(i+1) + ', lab' + str(i+1) +'\n\tnop'
        asm += '\n\tret\n'
    print(asm)

gshare_fa_ras_push_pop_01(8)
