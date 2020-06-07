

s = []


def my_decorator(name):
    def imy_decorator(func):
        print(name)
        print("this is before the function called")
        s.append("init")

        def wrapper():
            print("Something is happening before the function is called.")
            func()
            print("Something is happening after the function is called.")
        return wrapper
    return imy_decorator


@my_decorator(name="s")
def test1():
    print("asd")


@my_decorator
def test2():
    print("asd")


if __name__ == "__main__":
    print("up and running")
    test1()
    print(s)

    x = 1
