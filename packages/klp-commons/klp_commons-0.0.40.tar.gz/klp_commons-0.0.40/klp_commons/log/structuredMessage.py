from json import dumps


class StructuredMessage:
    '''
    Clase que define una strtura JSON para la información
    que se envía a los logs

    '''

    def __init__(self, message, /, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return '%s >>> %s' % (self.message, dumps(self.kwargs))
