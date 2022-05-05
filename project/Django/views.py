## Copyright: King's College London
## Author: Hefeng Zhou

import json
import sqlite3

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

# Create your views here.


def index(request):

    return render(request, 'jr.html')

id0 = 1
id1 = 2
id2 = 3


@csrf_exempt
def ssgj(request):
    global id0
    global id1
    global id2

    data = JSONParser().parse(request)
    stockId = data['stockId']
    con = sqlite3.connect("D:/study/PythonProjects/jr/jrs/jrs")
    cur = con.cursor()
    if stockId == 0:
        cur.execute("select * from stock_price where id = ? and stock_id = ?", (id0, stockId))
        con.commit()
        id0 += 3
    elif stockId == 1:
        cur.execute("select * from stock_price where id = ? and stock_id = ?", (id1, stockId))
        con.commit()
        id1 += 3
    else:
        cur.execute("select * from stock_price where id = ? and stock_id = ?", (id2, stockId))
        con.commit()
        id2 += 3
    result = cur.fetchone()
    cur.close()
    con.close()
    return JsonResponse(data=result,safe = False)