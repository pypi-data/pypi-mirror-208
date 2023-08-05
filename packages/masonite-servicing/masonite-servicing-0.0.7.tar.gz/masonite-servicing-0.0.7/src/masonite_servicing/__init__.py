# flake8: noqa F401
from .providers.ServicingProvider import ServicingProvider
from masonite.validation import Validator

class ServiceResult:
    def __init__(self, *args): 
        self.status = args[0]
        self.message = args[1]
        self.data = args[2]

def result(*args):
   return ServiceResult(*args)

def respond(request, validators, callback):
    errors = request.validate(*validators)

    if errors: 
        return {
            "status"  : "not-ok", 
            "message" : "VALIDATION_ERROR", 
            "errors"  : errors.all()    
        }

    callback()

    return {
        "status" : result.status, 
        "message" : result.message, 
        "data" : result.data
    }

def fetch(cb, *args): 
    return cb(*args).data

class SampleService:
    def add(self, x, y): 
        return result("ok", "added", x + y) 
    
def main():
    sample_service = SampleService()
    sample_service.add(3, 5)

def same(res1, res2): 
    return (
        res1.status == res2.status and
        res1.message == res2.message and
        res1.data == res2.data 
    )
