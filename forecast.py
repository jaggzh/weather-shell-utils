#!/usr/bin/env python3
import os, sys
import json
import symbols
from bansi import *
import ipdb

var_cache_fn='owm_cache_forecast_fn'
if var_cache_fn not in os.environ:
	print(f"Missing cache json file VARIABLE '{var_cache_fn}'")
	sys.exit(1)
fn_json=os.environ[var_cache_fn]
print(f"Using json: {fn_json}")

def k2f(kstr):
	kelvin = float(kstr)
	fahrenheit = (kelvin - 273.15) * 9/5 + 32
	return fahrenheit

def k2c(kstr):
	kelvin = float(kstr)
	celsius = (kelvin - 273.15)
	return celsius


# print(fn_json)
with open(fn_json,'rt') as F:
	alldata = json.load(F)
daydata = alldata['list']
cityname = alldata['city']['name']
tz = alldata['city']['timezone']
print(f"{bgblu}                 {gra}==== {whi}{cityname} {rst}{bgblu}{gra}====                 {rst}")
print(f"Date       Time  Hum T  Temp°f")
for di in daydata:
	datetime = di['dt']
	datestr = di['dt_txt']
	weather=di['weather'][0]
	wident = weather['description']
	wcmt = weather['main']
	hum = f"{di['main']['humidity']:3d}"
	hum_color = a24fg(255,255,255)
	tempk = di['main']['temp']
	tempf = k2f(tempk)
	tempkmin = k2f(di['main']['temp_min'])
	tempkmax = k2f(di['main']['temp_max'])
	temp_glyph, temp_color = symbols.temp_f_sym(tempf)
	temp_color = a24fg(*temp_color)
	if wident not in symbols.sym_weather:
		glyph='?'
		gwidth=2
		fg=a24fg(255,255,255)
	else:
		sym = symbols.sym_weather[wident]['day']
		glyph, gwidth = symbols.get_glyph(sym)
		argb = sym['clr_argb']
		fg=a24fg(argb[0], argb[1], argb[2])
	bg=a24bg(0,0,154)

	date,time,daycolor = symbols.date_to_str_color(datetime, tz)
	daycolor = a24bg(*daycolor)
	
	#print(f"{datestr} {gwidth} {temp_color}{temp_glyph}{rst} {tempf:.2f}°f {bg}{fg} {glyph:{gwidth}}{rst} [{wcmt:8}] {wident}")
	print(f"{date} {daycolor}{time}{rst} {hum_color}{hum}{rst} {temp_color}{temp_glyph}{rst} {tempf:5.1f}°f {bg}{fg} {glyph:{gwidth}}{rst} [{wcmt:8}] {wident}")
