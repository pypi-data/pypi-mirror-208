def check_active(func):
    def inner1(*args, **kwargs):
        if not args[0].active:
            raise Exception()
        return func(*args, **kwargs)

    return inner1
