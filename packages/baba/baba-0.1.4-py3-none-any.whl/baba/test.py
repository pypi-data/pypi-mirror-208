from taskbase import TaskBase
import time

class testSubClass(TaskBase):
    def my_method(self, arg1, arg2, arg3):
        time.sleep(0.5)
        print("猜猜看，父类做了些什么？")

    def error_test(self):
        time.sleep(1.2)
        try:
            print(1/0)            
        except Exception as e:
            print(e)
        print(1/0)
        print("hello")

a=testSubClass()
a.my_method(10086,time,"第三个参数")
a.error_test()