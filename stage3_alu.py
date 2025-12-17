import sys
import csv
import struct

class VirtualMachineALU:
    def __init__(self, memory_size=1024):
        self.memory = [0] * memory_size
        self.registers = [0] * 32
        self.program_counter = 0
        
    def load_program(self, program_file):
        with open(program_file, 'rb') as f:
            data = f.read()
        
        for i in range(0, len(data), 5):
            chunk = data[i:i+5]
            if len(chunk) == 5:
                self.memory[i//4] = struct.unpack('<I', chunk[:4])[0]
    
    def decode_command(self, command_bytes):
        value = 0
        for i, byte in enumerate(command_bytes):
            value |= byte << (i * 8)
        
        a = value & 0x1F
        b = (value >> 5) & 0x1F
        c = (value >> 10) & 0x1F
        
        return a, b, c
    
    def bitreverse(self, value):
        result = 0
        for i in range(32):
            if value & (1 << i):
                result |= 1 << (31 - i)
        return result
    
    def execute_load(self, b, c):
        if 0 <= b < len(self.registers):
            self.registers[b] = c
        self.program_counter += 5
    
    def execute_read(self, b, c, d):
        address_reg = c
        offset = b
        dst_reg = d
        
        if 0 <= address_reg < len(self.registers):
            address = self.registers[address_reg] + offset
            if 0 <= address < len(self.memory):
                if 0 <= dst_reg < len(self.registers):
                    self.registers[dst_reg] = self.memory[address]
        
        self.program_counter += 5
    
    def execute_write(self, b, c):
        src_reg = b
        address = c
        
        if 0 <= src_reg < len(self.registers):
            value = self.registers[src_reg]
            if 0 <= address < len(self.memory):
                self.memory[address] = value
        
        self.program_counter += 5
    
    def execute_bitreverse(self, b, c):
        src_reg = b
        dst_reg = c
        
        if 0 <= src_reg < len(self.registers):
            value = self.registers[src_reg]
            reversed_value = self.bitreverse(value)
            
            if 0 <= dst_reg < len(self.registers):
                address = self.registers[dst_reg]
                if 0 <= address < len(self.memory):
                    self.memory[address] = reversed_value
        
        self.program_counter += 5
    
    def run(self, program_file, dump_file=None, dump_range=None):
        self.load_program(program_file)
        
        while True:
            if self.program_counter >= len(self.memory) * 4:
                break
                
            command_bytes = bytes([
                self.memory[self.program_counter // 4] & 0xFF,
                (self.memory[self.program_counter // 4] >> 8) & 0xFF,
                (self.memory[self.program_counter // 4] >> 16) & 0xFF,
                (self.memory[self.program_counter // 4] >> 24) & 0xFF,
                0
            ])
            
            a, b, c = self.decode_command(command_bytes[:5])
            
            if a == 15:
                self.execute_load(b, c)
            elif a == 17:
                d = (c >> 5) & 0x1F
                c_field = c & 0x1F
                b_field = b
                self.execute_read(b_field, c_field, d)
            elif a == 8:
                self.execute_write(b, c)
            elif a == 25:
                self.execute_bitreverse(b, c)
            else:
                break
        
        if dump_file and dump_range:
            self.dump_memory(dump_file, dump_range)
    
    def dump_memory(self, dump_file, dump_range):
        start, end = map(int, dump_range.split('-'))
        
        with open(dump_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Адрес', 'Значение'])
            
            for addr in range(start, end + 1):
                if 0 <= addr < len(self.memory):
                    writer.writerow([addr, self.memory[addr]])

def main():
    if len(sys.argv) < 4:
        print("Использование: python stage3_alu.py <программа> <дамп_файл> <диапазон>")
        print("Пример диапазона: 0-100")
        return
    
    program_file = sys.argv[1]
    dump_file = sys.argv[2]
    dump_range = sys.argv[3]
    
    vm = VirtualMachineALU()
    vm.run(program_file, dump_file, dump_range)

if __name__ == "__main__":
    main()
