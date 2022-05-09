#!/usr/bin/python  
#coding=UTF-8                                                                                                                                                                                                                                                              
import sys
import re
import subprocess
import os


# Crash backtrace 样例
#2022-05-08 18:26:38.315 17364-17364/? A/DEBUG: backtrace:
#2022-05-08 18:26:38.315 17364-17364/? A/DEBUG:       #00 pc 00081d4c  /data/app/~~o1==/xxx==/base.apk!xxx.so (offset 0x1810000) (File::mkdirs(char*)+180)
#2022-05-08 18:26:38.315 17364-17364/? A/DEBUG:       #01 pc 00081bec  /data/app/~~o1==/xxx==/base.apk!xxx.so (offset 0x1810000) (File::writeIO()+72)


# 环境样例
#ADDR2LINE_BINARY='/ndk/21.1.6352462/toolchains/x86-4.9/prebuilt/darwin-x86_64/bin/i686-linux-android-addr2line'
#LIBRARY='/app/build/intermediates/merged_native_libs/debug/out/lib/armeabi-v7a/liblearn.so'

ADDR2LINE_BINARY='' # full path to arm-linux-androideabi-addr2line
LIBRARY='' # full path to your .so file

def main():
    print '本脚本会利用 android-addr2line 将 Android Native Crash 地址批量转换成代码堆栈。'
    if len(ADDR2LINE_BINARY) == 0 or len(LIBRARY) == 0:
        print '大佬，请先编辑本脚本，配置 ADDR2LINE_BINARY & LIBRARY 路径（so文件路径)再使用。'
        return
    print 'LIBRARY = [%s]' % LIBRARY
    print 'ADDR2LINE_BINARY = [%s]' % ADDR2LINE_BINARY
    print '大佬，贴入堆栈信息并按下回车，CTRL + D 提交。CTRL + C 退出。'

    lines = []

    while True:
        try:
            line = raw_input()
        except KeyboardInterrupt:
            sys.exit()
        except EOFError:
            break
        lines.append(line)

  

    addresses = []
    functions = []
    files = []

    print '\n'

    for line in lines:
        address = get_address(line)
        if address is not None:
            source = get_source_line(address)
            if source is not None:
                addresses.append(address)
                functions.append(source[0])
                files.append(source[1])

    if len(addresses) == 0 or len(files) == 0:
        print '没有从 %s 中找到映射地址。' % os.path.basename(LIBRARY)
        return

    longest_address = len(max(addresses, key=len))
    longest_file = len(max(files, key=len))

    for i in range(0, len(addresses)):
        print addresses[i].ljust(longest_address + 1),
        print files[i].ljust(longest_file + 1),
        print functions[i]

def get_address(line):
    search = re.search('#[0-9]{2} +pc +([0-9A-Fa-f]{8}) +/data', line)
    if search is None:
        return None
    else:
        return search.groups(1)[0]

def get_source_line(address):
    output = subprocess.check_output([ADDR2LINE_BINARY, '-C', '-f', '-e', LIBRARY, address]).split('\n')
    return (output[0], output[1])

if __name__ == '__main__':
    main()
