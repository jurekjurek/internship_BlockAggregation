import numpy as np

QBTbl = [q for q in range(10)]




a = [q for q in QBTbl if q%2==0]
b = [q for q in QBTbl if q%2!=0]

c = a+b
d = [a+b]
print(c, '\n', d)