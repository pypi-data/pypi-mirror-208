#coding=utf-8
import os

class SamsungExynos():
    """Apple sosi"""
    def __init__(self):
        ...
    
    def __str__(self):
        print("ГОРЯЧАЯ ХУЙНЯ.")

class GoogleTensor(SamsungExynos):
    '''
    Google Tensor object. Idi naxuy.
    
    '''
    
    def __init__(self, temp: int = 0):
        self.temp = temp


    def throttle(self):
        '''
        троттлить
        '''
        print("иди нахуй, я холодный")

class TensorG1(GoogleTensor):
    '''
    Tensor model G1. 
    
    '''
    def __init__(self):
        self.__cores = ['Cortex-X1', 'Cortex-X1', 'Cortex A76', 'Cortex A76', 'Cortex A55', 'Cortex A55', 'Cortex A55', 'Cortex A55']
        self.clock = 2.8
        self.gpu = 'Mali-G78 MP20'
        self.antutu = 713536
        self.apu = 'Tensor Processing Unit'

    def info(self):
        '''
        print info
        '''
        print(f"Инфо о Tensor G1:\nЯдра: {', '.join(self.__cores)}\nЧастота: {self.clock}\nГрафика: {self.gpu}\nAntutu v9: {self.antutu}\nAPU: {self.apu}")


class TensorG2(GoogleTensor):
    '''
    Tensor model G2. 
    
    '''
    def __init__(self):
        self.__cores = ['Cortex-X1', 'Cortex-X1', 'Cortex A78', 'Cortex A78', 'Cortex A55', 'Cortex A55', 'Cortex A55', 'Cortex A55']
        self.clock = 2.85
        self.gpu = 'Mali-G710 MP7'
        self.antutu = 789237
        self.apu = 'Next-gen Tensor Processing Unit'

    def info(self):
        '''
        print info
        '''
        print(f"Инфо о Tensor G2:\nЯдра: {', '.join(self.__cores)}\nЧастота: {self.clock}\nГрафика: {self.gpu}\nAntutu v9: {self.antutu}\nAPU: {self.apu}")