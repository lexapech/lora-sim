import sys




class A:
    def __init__(self):
        self.value=123

    def get(self):
        return Attribute(self,'value')

if __name__ == "__main__":
    a = A()
    v = a.get()
    v.set(321)
    print(v.get())
