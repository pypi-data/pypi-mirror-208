#!/Users/christmas/opt/anaconda3/bin/python3
# -*- coding: utf-8 -*-
#  日期 : 2023/3/25 10:54
#  作者 : Christmas
#  邮箱 : 273519355@qq.com
#  项目 : Project
#  版本 : python 3
#  摘要 :
"""

"""
import datetime


def build_date(_date):   # sourcery skip: inline-immediately-returned-variable
	"""
	根据要跑模型的日期推出附近日期
	:param _date: 要跑模型的日期
	:return: 附近日期信息
	"""
	today = str(_date)
	ymd_yes = (datetime.datetime.strptime(today, '%Y%m%d') - datetime.timedelta(days=1)).strftime('%Y%m%d')
	ymd_yes2 = (datetime.datetime.strptime(today, '%Y%m%d') - datetime.timedelta(days=2)).strftime('%Y%m%d')
	ymd_yes3 = (datetime.datetime.strptime(today, '%Y%m%d') - datetime.timedelta(days=3)).strftime('%Y%m%d')
	year_yes = ymd_yes[:4]
	month_yes = ymd_yes[4:6]
	year_yes2 = ymd_yes2[:4]
	month_yes2 = ymd_yes2[4:6]
	year_yes3 = ymd_yes3[:4]
	month_yes3 = ymd_yes3[4:6]
	ymd_tom = (datetime.datetime.strptime(today, '%Y%m%d') + datetime.timedelta(days=1)).strftime('%Y%m%d')
	ymd_tom2 = (datetime.datetime.strptime(today, '%Y%m%d') + datetime.timedelta(days=2)).strftime('%Y%m%d')
	ymd_tom3 = (datetime.datetime.strptime(today, '%Y%m%d') + datetime.timedelta(days=3)).strftime('%Y%m%d')
	year_tom = ymd_tom[:4]
	month_tom = ymd_tom[4:6]
	year_tom2 = ymd_tom2[:4]
	month_tom2 = ymd_tom2[4:6]
	year_tom3 = ymd_tom3[:4]
	month_tom3 = ymd_tom3[4:6]
	Nearby_date = {
		'ymd_yes': ymd_yes,
		'year_yes': year_yes,
		'month_yes': month_yes,
		'ymd_yes2': ymd_yes2,
		'year_yes2': year_yes2,
		'month_yes2': month_yes2,
		'ymd_yes3': ymd_yes3,
		'year_yes3': year_yes3,
		'month_yes3': month_yes3,
		'ymd_tom': ymd_tom,
		'year_tom': year_tom,
		'month_tom': month_tom,
		'ymd_tom2': ymd_tom2,
		'year_tom2': year_tom2,
		'month_tom2': month_tom2,
		'ymd_tom3': ymd_tom3,
		'year_tom3': year_tom3,
		'month_tom3': month_tom3
	}
	return Nearby_date
