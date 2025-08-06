import json
import random
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def index(request):
    """首页信息接口"""
    time.sleep(0.2)
    return JsonResponse({
        "product_name": "油滋滋汉堡",
        "product_price": "16元",
        "description": "汉堡赛高！"
    })

def films(request):
    """电影数据接口"""
    try:
        with open('./films.json', 'r', encoding='utf-8') as f:
            dic = json.load(f)
        return JsonResponse(dic)
    except Exception as e:
        logger.exception("获取电影数据失败")
        return JsonResponse({
            'code': 500,
            'msg': f'获取电影数据失败: {str(e)}',
            'result': None
        })

def random_t_views(request):
    """随机数接口"""
    try:
        ii = []
        for i in range(3):
            ii.append(random.randint(1, 99999999))
        return JsonResponse(ii, safe=False)
    except Exception as e:
        logger.exception("生成随机数失败")
        return JsonResponse({
            'code': 500,
            'msg': f'生成随机数失败: {str(e)}',
            'result': None
        })