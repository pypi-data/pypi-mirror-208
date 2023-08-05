'''
构造一个对象，可以通过属性访问，类似JavaScript的对象
'''
import json

class JSOBJEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, JSOBJ):
            return o.__dict__
        try:
            return json.JSONEncoder.default(self, o)
        except Exception as e:
            return o.__str__()
    
class JSOBJ:
    def __init__(self, arg=None):
        if arg is None or not arg:
            return
        if type(arg) == str:
            arg = json.loads(arg)
        if type(arg) != dict:
            raise TypeError('arg has to be a `dict`')
        self.__dict__ = arg
        for k in self.__dict__:
            if type(self.__dict__[k]) == dict:
                self.__dict__[k] = JSOBJ(self.__dict__[k])


    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2, ensure_ascii=False, cls=JSOBJEncoder)

    def get_obj(self):
        return json.loads(self.__str__())
    pass

def test():
    # 对象构造
    a = JSOBJ()
    a.name = '詹姆斯'
    a.code = '007'
    b = JSOBJ()
    b.name = '零零发'
    b.code = '008'
    a.b = b
    print(a)

    # 字典构造
    bb = JSOBJ([{
          "b": {
            "code": "008",
            "name": "零零发"
          },
          "code": "007",
          "name": "詹姆斯",
        }])
    print(bb)

if __name__ == '__main__':
    test()
