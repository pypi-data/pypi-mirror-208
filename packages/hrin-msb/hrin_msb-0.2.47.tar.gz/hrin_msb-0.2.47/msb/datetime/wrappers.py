import logging
from datetime import datetime, timedelta

import pytz

from .constants import *


def current_time(frmt=DEFAULT_TIME_FORMAT):
	return datetime.now().time().strftime(frmt)


def current_date(frmt=DEFAULT_DATE_FORMAT):
	return datetime.now().date().strftime(frmt)


def current_timestamp(frmt=TIMESTAMP_FORMAT):
	return datetime.now().strftime(frmt)


def timestamp_diff(latest=None, old=None, return_in='sec|min|hr|day'):
	diff_data = dict(sec=0, min=0, hr=0, day=0)
	return_in = 'sec' if return_in not in ['sec', 'min', 'hr', 'day'] else return_in
	try:
		latest = datetime.strptime(latest, TIMESTAMP_FORMAT)
		old = datetime.strptime(old, TIMESTAMP_FORMAT)
		diff = (latest - old)
		diff_data['sec'] = diff.total_seconds()
		diff_data['min'] = (diff_data.get('sec') / 60)
		diff_data['hr'] = (diff_data.get('min') / 60)
		diff_data['day'] = diff.days
	# print (diff_data)
	except Exception as e:
		logging.exception(e)
	return diff_data.get(return_in)


def create_datetime(inp_dtime=None, hours=0, mins=0, secs=0, days=0, inp_fmt=TIMESTAMP_FORMAT, out_fmt=None):
	try:
		out_fmt = inp_fmt if out_fmt is None else out_fmt
		inp_dtime = str(datetime.now().strftime(inp_fmt)) if inp_dtime is None else inp_dtime
		return (
			datetime.strptime(inp_dtime, inp_fmt) +
			timedelta(
				hours=hours, days=days,
				minutes=mins,
				seconds=secs
			)
		).strftime(out_fmt)
	except Exception as e:
		print(e)


def parse_datetime(inp_dtime=None, inp_fmt=TIMESTAMP_FORMAT):
	result = None
	try:
		result = datetime.strptime(str(inp_dtime), inp_fmt)

	except Exception as e:
		logging.exception(e)
	return result


def convert_to_utc(inp_dtime=None, inp_fmt=TIMESTAMP_FORMAT, out_fmt=None, ist_time_diff='0:00'):
	try:
		out_fmt = inp_fmt if out_fmt is None else out_fmt
		dt = parse_datetime(str(inp_dtime), inp_fmt=inp_fmt)
		hour_diff, mins_diff = ist_time_diff.split(":")
		utc_time = create_datetime(
			dt.__str__(), hours=-int(hour_diff), mins=-int(mins_diff),
			inp_fmt=inp_fmt
		)
		return parse_datetime(utc_time, inp_fmt=inp_fmt).strftime(out_fmt)


	except Exception as e:
		logging.exception(e)


def timezone_offset(timezone=DEFAULT_TIMEZONE):
	offset = 0
	try:
		offset = (datetime.now(pytz.timezone(timezone)).utcoffset().total_seconds() / 3600)
	except Exception as e:
		logging.exception(e)
	return offset
