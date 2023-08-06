def info():
    print("""
from typing import Union
def return_int_or_str(flag:bool)->Union[str,int]:
  if flag:
    return 'I am a string!'
  else:
    return 'I am an Integer'
a=return_int_or_str(1)
print(a)
b=return_int_or_str(0)
print(b)
    """)