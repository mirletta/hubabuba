import sys
import struct
import argparse

class Assembler:
    def encode(self, a, b, c, d=0, mode=''):
        val = 0
        if mode == 'LOAD':
            val |= (a & 0x1F)          # Биты 0-4
            val |= (b & 0x1F) << 5     # Биты 5-9
            val |= (c & 0x1FFFFF) << 10 # Биты 10-30
        elif mode == 'READ':
            val |= (a & 0x1F)          # Биты 0-4
            val |= (b & 0x1FFF) << 5    # Биты 5-17
            val |= (c & 0x1F) << 18    # Биты 18-22
            val |= (d & 0x1F) << 23    # Биты 23-27
        elif mode == 'WRITE':
            val |= (a & 0x1F)          # Биты 0-4
            val |= (b & 0x1F) << 5     # Биты 5-9
            val |= (c & 0x7FFFFFF) << 10 # Биты 10-36
        elif mode == 'BITREV':
            val |= (a & 0x1F)          # Биты 0-4
            val |= (b & 0x1F) << 5     # Биты 5-9
            val |= (c & 0x1F) << 10    # Биты 10-14
        return val

    def process(self, input_path, output_path, test_mode=False):
        binary_data = bytearray()
        with open(input_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(';'): continue
                p = line.replace(',', ' ').split()
                cmd = p[0].upper()
                
                if cmd == 'LOAD':
                    a, b, c = 15, int(p[1]), int(p[2])
                    raw = self.encode(a, b, c, mode='LOAD')
                elif cmd == 'READ':
                    a, b, c, d = 17, int(p[3]), int(p[2]), int(p[1])
                    raw = self.encode(a, b, c, d, mode='READ')
                elif cmd == 'WRITE':
                    a, b, c = 8, int(p[1]), int(p[2])
                    raw = self.encode(a, b, c, mode='WRITE')
                elif cmd == 'BITREV':
                    a, b, c = 25, int(p[1]), int(p[2])
                    raw = self.encode(a, b, c, mode='BITREV')

                if test_mode:
                    print(f"{cmd}: {hex(raw)} (bytes: {' '.join(f'{b:02x}' for b in raw.to_bytes(5, 'little'))})")
                binary_data.extend(raw.to_bytes(5, 'little'))

        with open(output_path, 'wb') as f:
            f.write(binary_data)
        print(f"Бинарный файл готов: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    Assembler().process(args.input, args.output, args.test)
