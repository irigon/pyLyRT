class Core:
    def __init__(self):
        self.roles={}


class Player(Core):
    def __init__(self):
        super().__init__()

    def type(self):
        return 'player'
    '''
    def __getattribute__(self, name):
        attr = Core.__getattribute__(self, name)
        if hasattr(attr, '__call__'):
            def newfunc(*args, **kwargs):
                print('before calling %s' % attr.__name__)
                result = attr(*args, **kwargs)
                print('done calling %s' % attr.__name__)
                return result

            return newfunc
        else:
            return attr
    '''
class Role:
    def __init__(self):
        self.roles={}
    def type(self):
        return 'role'

class Compartment(Core):
    def __init__(self):
        super().__init__()

    def type(self):
        return 'compartment'

