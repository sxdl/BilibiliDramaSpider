import time
import os
import shutil


def read(file_name):
    with open(file_name, 'r') as f:
        data = f.read().split('\n')
        data = [i for i in data if i]
    return data


def add_content(file_name, content):
    with open(file_name, 'a', encoding='utf-8') as f:
        f.write('{}'.format(content) + '\n')


def add_log(file_name, content):
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(file_name, 'a', encoding='utf-8') as f:
        f.write('[{}]{}'.format(localtime, content) + '\n')


def query(file_name):
    lines = read(file_name)
    print('查询结果为{}条'.format(len(lines)))
    for index, line in enumerate(lines):
        print("{}\t{}".format(index + 1, line))


def deleteline(file_name, linenum):
    lines = read(file_name)
    counter = 1
    for line in lines:
        if counter == linenum:
            lines.remove(line)
            print('Line {} successfully delete'.format(linenum))
            break
        counter += 1
    else:
        print('Line {} delete error! Line number out of range!'.format(linenum))
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def modify(file_name):
    input_website = input('Input modify website:')

    lines = read(file_name)
    for line in lines:
        read_website = line.split('\t')[0]
        if read_website == input_website:
            print('current 【{}】 exist，value is 【{}】'.format(input_website, line))
            new_website = input('Input new website:')
            new_password = input('Input new password:')
            lines[lines.index(line)] = "{}\t{}".format(new_website, new_password)
            print('modify success!')
            break
    else:
        print('current 【{}】 not find！,modify failed!'.format(input_website))
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    query(file_name)


def move_file(srcfile, dstpath):  # 移动函数
    if not os.path.isfile(srcfile):
        print("%s not exist!" % srcfile)
    else:
        fpath, fname = os.path.split(srcfile)             # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)                       # 创建路径
        shutil.move(srcfile, dstpath + fname)          # 移动文件
        print("move %s -> %s" % (srcfile, dstpath + fname))

if __name__ == "__main__":
    deleteline('./undownload_list.txt', 2)
