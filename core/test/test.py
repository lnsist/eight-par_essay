import random


def test_20240612152929():
    def _func_run(name: str, age: int, is_man: bool) -> str:
        is_man_str = '是' if is_man else '不是'
        return f'姓名: {name}, 年龄: {age}, {is_man_str}男人.'

    temp_result = _func_run(1, '2', 'True')
    print(temp_result)
    print(1_000)
    print(id(_func_run))
    print(type(_func_run))
    print(id(None))
    print(type(None))
    temp_dict = {'1': 1, 2: '2', 0: 0}
    print(temp_dict)
    # print(temp_dict[1])  # 是'1'
    print(str(bool(1)))


def test_20240613102411():
    class RevealAccess(object):
        def __init__(self, init_val=None, name='var'):
            self.val = init_val
            self.name = name

        def __get__(self, obj, obj_type):
            print('Retrieving', self.name)
            return self.val

        def __set__(self, obj, value):
            print('Updating', self.name)
            self.val = value

    class MyClass(object):
        x = RevealAccess(10, 'var "x"')
        y = 5

    m = MyClass()
    print(m.x)
    m.x = 20
    print(m.x)
    print(m.y)


def test_20240613103800():
    class C(object):
        def getx(self):
            print('===获取')
            return self.__x

        def setx(self, value):
            print('===设置')
            self.__x = value

        def delx(self):
            print('===删除')
            del self.__x

        def re_getx(self):
            print('===重写获取')
            return f'值为: {self.getx()}'

        x = property(getx, setx, delx, "I'm the 'x' property.")
        y = property(re_getx)

    c = C()
    c.x = 'test_20240613103800'
    print(c.x)
    print(c.y)


def test_20240613165720():
    min_num = 1
    max_num = 100
    r_num = random.randint(1, 100)
    while True:
        input_num = int(input(f'请输入猜测数字({min_num} ~ {max_num}): '))
        if r_num > input_num:
            min_num = input_num
            print('猜小了')
        elif r_num < input_num:
            max_num = input_num
            print('猜大了')
        else:
            print('猜对了')
            break


def test_20240613175345():
    def _run(a, b=1):
        print(a, b)

    _run(1, a=2)  # TypeError: _run() got multiple values for argument 'a'


def test_20240614094342():
    def make_incrementor(n):
        return lambda x: x + n

    f = make_incrementor('42')
    print(f)
    print(make_incrementor('42'))
    print(f('0'))
    print(make_incrementor('0'))
    print(f('1'))
    print(make_incrementor('42')('1'))


if __name__ == '__main__':
    pass
    test_20240614094342()
