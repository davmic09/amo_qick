#All I am doing is making a class that allows me to write some easier functions


class ASM_to_Assemb(AveragerProgramV2):
 
    def dmem_to_wmem(self, dreg, wreg):
        self.asm_inst({
            'CMD':    'REG_WR',
            'DST':    'reg',      # signals wreg destination
            'SRC':    'wmem',        # wmem path handles wreg destinations
            'OP':     'r5',          # source dreg (r0–r31)
            'ADDR':   '&0',          # wmem address (required even if not used for transfer)
        })
    def wmem_to_dmem(self, wreg, dreg):
        reg_dest = self.return_addr(dreg)
        reg_src = self.return_addr(wreg)
        self.asm_inst({
            'CMD':    'REG_WR',
            'DST':    f'{reg_dest}',      # signals wreg destination
            'SRC':    'r5',        
            'OP':     'wmem',          # source dreg (r0–r31)
            'ADDR':   f'{reg_src}',          # wmem address (required even if not used for transfer)
        })
    def return_addr(self, reg:str):
        """
        Given a register returns the address assigned to it (im using it for asm_inst)
        """
        try:
            # is name of register?
            reg = self.reg_dict[reg].full_addr()
        except:
            #
            if 'w' in reg:
                #is waveform memory return physical address marker
                reg = '&' + reg[-1] 
            
        return reg
    def add(self, rd, rs1, rs2):
        '''copying the structure of RISCV to help myself out'''
        reg_dest = self.return_addr(rd)
        reg_src1 = self.return_addr(rs1)
        reg_src2 = self.return_addr(rs2)
        self.asm_inst({'CMD': 'REG_WR', 'DST': f'{reg_dest}', 'SRC': 'op', 'OP':f'{reg_src1} + {reg_src2}'})
    def addi(self, rd, rs1, imm):
        '''copying the structure of RISCV to help myself out'''
        reg_dest = self.return_addr(rd)
        reg_src1 = self.return_addr(rs1)
        self.asm_inst({'CMD': 'REG_WR', 'DST': f'{reg_dest}', 'SRC': 'op', 'OP':f'{reg_src1} + {imm}'})   
    def sub(self, rd, rs1, rs2):
        '''copying the structure of RISCV to help myself out'''
        reg_dest = self.return_addr(rd)
        reg_src1 = self.return_addr(rs1)
        reg_src2 = self.return_addr(rs2)
        self.asm_inst({'CMD': 'REG_WR', 'DST': f'{reg_dest}', 'SRC': 'op', 'OP':f'{reg_src1} - {reg_src2}'})
    def srli(self, rd, rs1 ,imm):
        '''copying the structure of RISCV to help myself out'''
        reg_dest = self.return_addr(rd)
        reg_src1 = self.return_addr(rs1)
        self.asm_inst({'CMD': 'REG_WR', 'DST': f'{reg_dest}', 'SRC': 'op', 'OP':f'{reg_src1} >> {imm}'}) 
    def Kp_error(self, control_reg, set_reg, error_reg, measure_reg, kp:int):
        #This assumes that the registers have already been read/finished
        #get the signed error
        self.sub(error_reg, set_reg, measure_reg)
        #treat signs differently
        self.cond_jump('neg', error_reg, 'S')

        #error is positive
        self.cond_jump('finish', error_reg, 'S', '-', 'threshold')
        self.srli(error_reg, error_reg, f'#{kp}')
        self.jump('change_cntrl')


        #error is negative
        self.label('neg')
        self.sub(error_reg, 'zero', error_reg)
        self.cond_jump('finish', error_reg, 'S', '-', 'threshold')
        self.srli(error_reg, error_reg, f'#{kp}')
        self.sub(error_reg, 'zero', error_reg)
        self.jump('change_cntrl')
        


        self.label('change_cntrl')
        self.add(control_reg, control_reg, error_reg)


config = {'gen_ch': 1,
          'ro_ch': 0,
          'freq': 124,
          #last delay for pd was .545 us (plus the 0.4 of the original offset)
          'trig_time': 0.425,
          'read_wait': 0.1,
          'ro_len': .15,
          'pulse_len': 0.1,
          'pulse_phase': 0,
          'ro_phase': 0,
          'gain': 1.0
         }

# prog = ReadProgram(soccfg, reps=100, final_delay=0.5, cfg=config)
# iq_list = prog.acquire(soc, rounds=1, progress=False)
# phase_offset = np.angle(iq_list[0][0].dot([1,1j]), deg=True)
# config['ro_phase'] = -phase_offset

prog = ReadProgram(soccfg, reps=1, final_delay=0.5, cfg=config)
print(prog)
iq_list = prog.acquire_decimated(soc, rounds=1)
t = prog.get_time_axis(ro_index=0)

plt.plot(t, iq_list[0][:,0], label="I value")
plt.plot(t, iq_list[0][:,1], label="Q value")
plt.plot(t, np.abs(iq_list[0].dot([1,1j])), label="mag")
plt.legend()
plt.ylabel("a.u.")
plt.xlabel("us");

phase_offset = np.angle(iq_list[0].sum(axis=0).dot([1,1j]), deg=True)
print("phase offset:", phase_offset)

print("buffered readout:", iq_list[0].sum(axis=0))
print("feedback readout:", soc.read_mem(2,'dmem'))