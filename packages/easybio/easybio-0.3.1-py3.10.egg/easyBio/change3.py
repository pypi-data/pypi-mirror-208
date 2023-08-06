import os
import re
from collections import defaultdict

# 从txt文件中读取SRR和Name的映射关系

def read_srr_name_mapping(txt_file):
    mapping = defaultdict(list)
    with open(txt_file, 'r') as f:
        for line in f:
            srr, name = line.strip().split()
            if srr not in mapping:
                # mapping[srr] = name
                mapping[srr].append(name)
    return mapping

# 检查SRR编号对应的文件数


def count_srr_files(files):
    counter = defaultdict(int)
    for file in files:
        srr = re.match(r'(SRR\d+)_\d', file)
        if srr:
            counter[srr.group(1)] += 1
    return counter

# 重命名文件


def rename_files(files, srr_name_mapping, srr_file_counts):
    for file in files:
        srr_match = re.match(r'(SRR\d+)_(\d)', file)
        if srr_match:
            srr, num = srr_match.groups()
            name = srr_name_mapping[srr][0]
            lane_num = srr_name_mapping[srr].index(name) + 1
            srr_name_mapping[srr].remove(name)

            if srr_file_counts[srr] == 2:
                read_type = "R" + num
            else:
                read_type = "I1" if num == "1" else "R" + str(int(num) - 1)

            new_name = f"SRR{name}_S1_L00{lane_num}_{read_type}_001.fastq.gz"
            # os.rename(file, new_name)
            print(new_name)


def main():
    txt_file = "/home/data/user/lei/code/python/easyBio_conda/easybio_conda/easyBio/srrlist.txt"
    folder_path = "/home/data/user/lei/SRAData/GSE/GSE152048/raw/fq2"  # 修改为你的文件夹路径

    os.chdir(folder_path)
    files = os.listdir()
    srr_name_mapping = read_srr_name_mapping(txt_file)
    srr_file_counts = count_srr_files(files)
    rename_files(files, srr_name_mapping, srr_file_counts)


if __name__ == "__main__":
    main()
