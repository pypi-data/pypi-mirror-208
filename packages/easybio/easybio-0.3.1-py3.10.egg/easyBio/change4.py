import os
import re
from collections import defaultdict

txt_file = "/home/data/user/lei/code/python/easyBio_conda/easybio_conda/easyBio/srrlist.txt"
folder_path = "/home/data/user/lei/SRAData/GSE/GSE152048/raw/fq2"  # 修改为你的文件夹路径

# 读取SRR和Name对应关系
with open(txt_file, 'r') as f:
    lines = f.readlines()
    mapping = {line.split()[0]: line.split()[1] for line in lines}

# 获取文件夹中的文件并统计SRR数量
files = os.listdir(folder_path)
srr_counts = defaultdict(int)
for file in files:
    if re.match(r'(SRR\d+)_(\d)', file):
        srr = file.split('_')[0]
        srr_counts[srr] += 1

nameAddmapping = {}
nameAddSrrmapping = {}
# 对文件进行重命名
for file in files:
    srr_match = re.match(r'(SRR\d+)_(\d)', file)
    if srr_match:
        srr, number = file.split('_')[:2]
        srr, number = srr_match.groups()
        name = mapping[srr]
        read_type = ''
        if srr_counts[srr] == 2:
            if number == '1':
                read_type = 'R1'
            elif number == '2':
                read_type = 'R2'
        elif srr_counts[srr] == 3:
            if number == '1':
                read_type = 'I1'
            elif number == '2':
                read_type = 'R1'
            elif number == '3':
                read_type = 'R2'

        # nameAddmapping[name] += 1
        if srr in nameAddSrrmapping:
            lane_number = nameAddSrrmapping[srr]
        else:
            nameAddmapping[name] = nameAddmapping.get(name, 0) + 1
            nameAddSrrmapping[srr] = nameAddmapping[name]
            lane_number = nameAddSrrmapping[srr]

        new_name = f"SRR{name}_S1_L00{lane_number}_{read_type}_001.fastq.gz"
        
        # 重命名文件
        os.rename(f"{folder_path}/{file}", f"{folder_path}/{new_name}")
        print(f'Renamed {file} to {new_name}')
        

print("重命名完成")
