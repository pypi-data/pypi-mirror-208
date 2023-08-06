import os
import re
from collections import defaultdict


def read_mapping_file(txt_file):
    with open(txt_file, 'r') as f:
        lines = f.readlines()
        mapping = {line.split()[0]: line.split()[1] for line in lines}
    return mapping


def count_srr_occurrences(folder_path):
    files = os.listdir(folder_path)
    srr_counts = defaultdict(int)
    for file in files:
        srr_match = re.match(r'(SRR\d+)_(\d)', file)
        if srr_match:
            srr = srr_match.group(1)
            srr_counts[srr] += 1
    return files, srr_counts


def rename_files(files, folder_path, mapping, srr_counts):
    name_add_mapping = {}
    name_add_srr_mapping = {}
    for file in files:
        srr_match = re.match(r'(SRR\d+)_(\d)', file)
        if srr_match:
            srr, number = srr_match.groups()
            name = mapping[srr]
            read_type = ''
            if srr_counts[srr] == 2:
                read_type = 'R1' if number == '1' else 'R2'
            elif srr_counts[srr] == 3:
                read_type = 'I1' if number == '1' else (
                    'R1' if number == '2' else 'R2')

            if srr in name_add_srr_mapping:
                lane_number = name_add_srr_mapping[srr]
            else:
                name_add_mapping[name] = name_add_mapping.get(name, 0) + 1
                name_add_srr_mapping[srr] = name_add_mapping[name]
                lane_number = name_add_srr_mapping[srr]

            new_name = f"SRR{name}_S1_L00{lane_number}_{read_type}_001.fastq.gz"
            os.rename(f"{folder_path}/{file}", f"{folder_path}/{new_name}")
            print(f'Renamed {file} to {new_name}')


def changeName2(txt_file, folder_path):
    mapping = read_mapping_file(txt_file)
    files, srr_counts = count_srr_occurrences(folder_path)
    rename_files(files, folder_path, mapping, srr_counts)
    print("重命名完成")


if __name__ == '__main__':
    txt_file = "/home/data/user/lei/code/python/easyBio_conda/easybio_conda/easyBio/srrlist.txt"
    folder_path = "/home/data/user/lei/SRAData/GSE/GSE152048/raw/fq"
    changeName2(txt_file, folder_path)
