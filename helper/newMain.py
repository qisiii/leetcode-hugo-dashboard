from .problem import Problem
from .submisson import Submisson
from .store import Store


class Main:
    '''主程序'''

    def __init__(self,type='default'):
        self.problems = Problem(type)
        self.submisson= Submisson(type)
        self.store=Store(type)

    def __info(self):
        print(self.problems.info)

    def update(self):
        '''更新数据'''
        self.__info()
        self.problems.update()
        self.submisson.update()
        self.store.store()

    def rebuild(self):
        '''重建数据'''
        self.__info()
        self.store.clearDB()
        self.update()
        
    def test(self):
        self.store.clearDB()
        self.update()

    def hugo(self):
        self.store.store()
