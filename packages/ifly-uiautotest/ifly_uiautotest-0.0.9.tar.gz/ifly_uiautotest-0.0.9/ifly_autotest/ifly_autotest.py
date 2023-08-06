# -*- coding: utf-8 -*-
import os

def get_code():
    val = input("选择模式：\n 1. 已有业务，下载代码进行测试或者补充/修改测试用例\n 2. 新业务，新增模块 \n")
    if val == "1":
        clone_path = input("输入clone到的路径：")
        if clone_path is '':
            print("输入路径错误")
        else:
            try:
                if not os.path.exists(clone_path):
                    os.mkdir(clone_path)
                os.system("git clone https://code.iflytek.com/ST_TC_TEST_PLATFORM/ui_autotest.git %s" % clone_path)
                print("代码已clone到"+clone_path+"路径中")
            except Exception as e:
                print("出现错误："+str(e))

    elif val == "2":
        cookiecutter_path = input("输入保存到的路径：")
        if cookiecutter_path is '':
            print("输入路径错误")
        else:
            try:
                if not os.path.exists(cookiecutter_path):
                    os.mkdir(cookiecutter_path)
                os.system("cookiecutter https://code.iflytek.com/ST_TC_TEST_PLATFORM/cookiecutter-uiautotest.git -o %s" % cookiecutter_path)
                print("代码已保存到" + cookiecutter_path + "路径中")
            except Exception as e:
                print("出现错误："+str(e))

def main():
    get_code()

if __name__ == '__main__':
    main()