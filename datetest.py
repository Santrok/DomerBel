from datetime import datetime, timedelta
#
# print((datetime.now() - timedelta(days=50)) > (datetime.now() - timedelta(days=51)))


x= datetime.now()
y = x + timedelta(1)

print(y<x)