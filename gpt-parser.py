import struct
import sys

def read_guid(file, offset):
    file.seek(offset, 0)
    part1 = struct.unpack(">Q", file.read(8))[0]
    part2 = struct.unpack(">Q", file.read(8))[0]
    return part1, part2

def read_file_bytes(file, offset, num_bytes):
    file.seek(offset, 0)
    result = 0
    for i in range(num_bytes):
        byte = struct.unpack("<B", file.read(1))[0]
        result |= byte << (i * 8)
    return result

def main(image_path):
    try:
        with open(image_path, 'rb') as file:
            # Read GPT header signature
            signature = read_file_bytes(file, 512, 8)
            if signature != 0x5452415020494645:
                print("only process the gpt file system")
                return

            LBAstart = read_file_bytes(file, 584, 8)
            LBAend = read_file_bytes(file, 592, 4)
            entrySize = read_file_bytes(file, 596, 4)
            i = 0

            while True:
                i += 1
                offset = LBAstart * 512 + i * entrySize
                if offset >= LBAend * 512:
                    break

                part1, part2 = read_guid(file, offset)
                if part1 == 0 and part2 == 0:
                    continue

                partitionLBA_start = read_file_bytes(file, offset + 32, 8)
                partitionLBA_end = read_file_bytes(file, offset + 40, 8)
                partSize = (partitionLBA_end - partitionLBA_start + 1) * 512
                jumpcode = read_file_bytes(file, partitionLBA_start * 512, 3)
                sysType = "Unknown"

                if jumpcode == 0x9052EB:
                    sysType = "NTFS"
                elif jumpcode == 0x9058EB:
                    sysType = "FAT32"

                print(f'{part1:016X}{part2:016X} {sysType} {partitionLBA_start} {partSize}')

    except FileNotFoundError:
        print(f"Error: File '{image_path}' not found.")
    except Exception as e:
        print(f"Error reading file '{image_path}': {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <image_path>')
        sys.exit(1)

    main(sys.argv[1])
