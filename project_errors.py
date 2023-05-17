# make exception class named ActionError
class ActionError(Exception):

    def __bool__(self):
        return False


if __name__ == "__main__":
    a = ActionError("This is an ActionError")
    print(a)
    raise a