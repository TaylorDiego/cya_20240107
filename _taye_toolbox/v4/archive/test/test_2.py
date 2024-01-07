from test_1 import star, percent

@star
@percent
def printer(msg):
    print(msg)

printer("Hello")