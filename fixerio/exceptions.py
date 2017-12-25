class FixerioException(Exception):
    """ General Fixerio exception """
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class FixerioCurrencyUnavailable(FixerioException):
    """ Wrong or unavailable base currency """
    pass

class FixerioInvalidDate(FixerioException):
    """ Wrong or unavailable date """
    pass