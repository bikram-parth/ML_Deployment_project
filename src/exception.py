import sys

def error_message_detail(error,error_detail:sys):
    _,_,exc_tb=error_detail.exc_info()
    error_message="Exception Occured in python Script [{0}], in line number ,[{1}], and the error is [{2}]".format(
        exc_tb.tb_frame.f_code.co_filename,
        exc_tb.tb_lineno,
        str(error)
    )
    return error_message

class Custom_Exception(Exception):
    def __init__(self,error,error_detail:sys):
        super().__init__(error)
        self.error_message=error_message_detail(error=error,error_detail=error_detail)

    def __str__(self):
        return self.error_message