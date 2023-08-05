import itertools

_case_list = ['用户名', '密码']
_value_list = ['正确', '不正确', '特殊符号', '超过最大长度']


def add_one(number):
    return number + 1


def gen_case(item=_case_list, value=_value_list):
    '''输出笛卡尔用例集合'''
    for i in itertools.product(item, value):
        print('输入'.join(i))


def _test_print():
    print("欢迎搜索关注公众号: 「测试开发技术」!")


if __name__ == '__main__':
    _test_print()
