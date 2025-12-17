import sys
import struct

class Assembler:
    def __init__(self):
        self.commands = []
        
    def parse_line(self, line):
        line = line.strip()
        if not line or line.startswith(';'):
            return None
            
        parts = line.split()
        if not parts:
            return None
            
        opcode = parts[0].upper()
        args = [arg.strip() for arg in ' '.join(parts[1:]).split(',')] if len(parts) > 1 else []
        args = [arg for arg in args if arg]
        
        return self.translate_command(opcode, args)
    
    def translate_command(self, opcode, args):
        if opcode == 'LOAD' and len(args) == 2:
            reg = int(args[0])
            value = int(args[1])
            a = 15
            b = reg
            c = value
            return self.encode_command(a, b, c, 0)
            
        elif opcode == 'READ' and len(args) == 3:
            dst_reg = int(args[0])
            src_reg = int(args[1])
            offset = int(args[2])
            a = 17
            b = offset
            c = src_reg
            d = dst_reg
            c_field = (d << 5) | c
            b_field = (c_field << 13) | b
            return self.encode_command(a, b_field, 0, 0)
            
        elif opcode == 'WRITE' and len(args) == 2:
            src_reg = int(args[0])
            address = int(args[1])
            a = 8
            b = src_reg
            c = address
            return self.encode_command(a, b, c, 0)
            
        elif opcode == 'BITREV' and len(args) == 2:
            src_reg = int(args[0])
            dst_reg = int(args[1])
            a = 25
            b = src_reg
            c = dst_reg
            return self.encode_command(a, b, c, 0)
            
        else:
            raise ValueError(f"Неизвестная команда или неправильные аргументы: {opcode} {args}")
    
    def encode_command(self, a, b, c, d):
        command = 0
        command |= (a & 0x1F)
        command |= (b & 0x1FF) << 5
        command |= (c & 0x7FFFFF) << 14
        command |= (d & 0x1F) << 37
        
        bytes_data = struct.pack('<Q', command)[:5]
        return bytes_data
    
    def assemble(self, source_file, output_file, test_mode=False):
        with open(source_file, 'r') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            try:
                command_bytes = self.parse_line(line)
                if command_bytes:
                    self.commands.append(command_bytes)
            except Exception as e:
                print(f"Ошибка в строке {line_num}: {e}")
                return
        
        with open(output_file, 'wb') as f:
            for cmd in self.commands:
                f.write(cmd)
        
        if test_mode:
            self.print_test_output()
    
    def print_test_output(self):
        print("Внутреннее представление команд:")
        for cmd in self.commands:
            hex_str = ' '.join([f'0x{b:02X}' for b in cmd])
            print(hex_str)

def main():
    if len(sys.argv) < 4:
        print("Использование: python stage1_assembler.py <входной_файл> <выходной_файл> <тестовый_режим>")
        print("Тестовый режим: 1 - включен, 0 - выключен")
        return
    
    source_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = sys.argv[3] == '1'
    
    assembler = Assembler()
    assembler.assemble(source_file, output_file, test_mode)

if __name__ == "__main__":
    main()
