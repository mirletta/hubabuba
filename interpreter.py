import sys
import csv
import argparse

class VM:
    def __init__(self, mem_size=1024):
        self.memory = [0] * mem_size
        self.registers = [0] * 32

    def run(self, bin_path, csv_path, m_range):
        with open(bin_path, 'rb') as f:
            code = f.read()

        pc = 0
        while pc + 5 <= len(code):
            val = int.from_bytes(code[pc:pc+5], 'little')
            a = val & 0x1F
            
            if a == 15: # LOAD
                b, c = (val >> 5) & 0x1F, (val >> 10) & 0x1FFFFF
                self.registers[b] = c
            elif a == 17: # READ
                b, c, d = (val >> 5) & 0x1FFF, (val >> 18) & 0x1F, (val >> 23) & 0x1F
                addr = self.registers[c] + b
                self.registers[d] = self.memory[addr] if addr < len(self.memory) else 0
            elif a == 8: # WRITE
                b, c = (val >> 5) & 0x1F, (val >> 10) & 0x7FFFFFF
                if c < len(self.memory): self.memory[c] = self.registers[b]
            elif a == 25: # BITREV
                b, c = (val >> 5) & 0x1F, (val >> 10) & 0x1F
                orig = self.registers[b] & 0xFFFFFFFF
                rev = int('{:032b}'.format(orig)[::-1], 2)
                addr = self.registers[c]
                if addr < len(self.memory): self.memory[addr] = rev
            pc += 5

        start, end = map(int, m_range.split('-'))
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Address', 'Value'])
            for i in range(start, end + 1):
                writer.writerow([i, self.memory[i]])
        print(f"Дамп памяти сохранен в {csv_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("binary")
    parser.add_argument("csv")
    parser.add_argument("range")
    args = parser.parse_args()
    VM().run(args.binary, args.csv, args.range)
