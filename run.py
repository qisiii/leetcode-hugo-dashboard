# -*- coding: utf-8 -*-
'''
@Author: KivenChen
@Date: 2019-04-23
@LastEditTime: 2019-05-02
'''
from helper.newMain import Main

if __name__ == "__main__":
    while True:
        print('欢迎使用 LeetCode_Helper, 请选择: ')
        print('1. 更新')
        print('2. 重建')
        print('3. 重写hugo')
        print('4. 测试')
        print('q. 退出')
        key = input()
        if key == 'q':
            break
        elif key == '1':
            Main().update()
            break
        elif key == '2':
            Main('rebuild').rebuild()
            break
        elif key == '3':
            Main('rewrite').hugo()
            break
        elif key == '4':
            Main('test').test()
            break
        else:
            print('请重新选择！')
