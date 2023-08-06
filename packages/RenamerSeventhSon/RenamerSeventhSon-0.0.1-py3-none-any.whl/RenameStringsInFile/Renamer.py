import sys
import re
import os
import threading

def copy_with_different_name(src_path, src_file_name, dst_path, dst_file_name, inner_res_name):

    src_res_full_path = os.path.join(src_path, src_file_name)
    dst_res_full_path = os.path.join(dst_path, dst_file_name)

    output = open(dst_res_full_path,"w")
    input = open(src_res_full_path)


    for line in input:
        output.write(re.sub(r"# DocumentName \w*", r"# DocumentName " + inner_res_name, line))


    input.close()
    output.close()

def do_rename(parameters):

    src_path = parameters[0]
    src_file_name = parameters[1]

    dst_path = parameters[2]
    dst_file_name = parameters[3]

    inner_res_name = parameters[4]

    if  len(parameters)>5:
        src_path2 = parameters[5]
        src_file_name2 = parameters[6]

        dst_path2 = parameters[7]
        dst_file_name2 = parameters[8]

        inner_res_name2 = parameters[9]

    inputThread = threading.Thread(target=copy_with_different_name(src_path, src_file_name, dst_path, dst_file_name, inner_res_name), daemon=True)
    timeoutThread = threading.Thread(target=copy_with_different_name(src_path2, src_file_name2, dst_path2, dst_file_name2, inner_res_name2), daemon=True)

    inputThread.start()
    timeoutThread.start()

    continue_check_threads = True

    while continue_check_threads == True:
        if inputThread.is_alive() == False or timeoutThread.is_alive() == False:
            continue_check_threads = False

if __name__ == '__main__':
        do_rename(sys.argv[1:])