#!/usr/bin/env python3
import os, sys
import json
import symbols
from bansi import *
import bisect

verbose=0
def pe(*x,**y):
    print(*x,**y, file=sys.stderr)
def pel(l,*x,**y):
    if verbose>=l: print(*x,*y, file=sys.stderr)

color=True
if '-C' in sys.argv:
    color=False
    uncolor()
    # from bansi import *
    # print(f"{bred}bred{rst}")
    # sys.exit()

var_cache_fn='owm_cache_forecast_fn'
if var_cache_fn not in os.environ:
	pe(f"Missing cache json file VARIABLE '{var_cache_fn}'")
	sys.exit(1)
fn_json=os.environ[var_cache_fn]
pel(1, f"Using json: {fn_json}")

def k2f(kstr):
	kelvin = float(kstr)
	fahrenheit = (kelvin - 273.15) * 9/5 + 32
	return fahrenheit

def k2c(kstr):
	kelvin = float(kstr)
	celsius = (kelvin - 273.15)
	return celsius

def build_nearest_weather(daydata):
    """
    Returns a function nearest_weather(t_utc) -> (glyph, gwidth, (r,g,b), desc, main)
    that chooses the nearest OWM 3h entry to the given UTC unix time.
    """
    times = []
    items = []
    for di in daydata:
        t_utc = int(di['dt'])
        w = di['weather'][0]
        items.append({
            'desc': w['description'],
            'main': w['main'],
        })
        times.append(t_utc)

    def nearest_weather(t_utc):
        i = bisect.bisect_left(times, int(t_utc))
        if i == 0:
            idx = 0
        elif i == len(times):
            idx = len(times) - 1
        else:
            before = times[i-1]; after = times[i]
            idx = i-1 if (t_utc - before) <= (after - t_utc) else i

        desc = items[idx]['desc']
        main = items[idx]['main']

        if desc in symbols.sym_weather:
            sym = symbols.sym_weather[desc]['day']   # keep using 'day' style as you do
            glyph, gwidth = symbols.get_glyph(sym)
            argb = sym['clr_argb']
            rgb = (argb[0], argb[1], argb[2])
        else:
            glyph, gwidth, rgb = '?', 2, (255, 255, 255)

        return glyph, gwidth, rgb, desc, main

    return nearest_weather

# --- Monotone cubic (Fritsch–Carlson) shape-preserving spline ----------------
def _fritsch_carlson_slopes(x, y):
    n = len(x)
    d = [(y[i+1]-y[i]) / (x[i+1]-x[i]) for i in range(n-1)]  # secants
    m = [0.0]*n
    m[0] = d[0]
    m[-1] = d[-1]
    for i in range(1, n-1):
        if d[i-1] == 0.0 or d[i] == 0.0 or (d[i-1] > 0) != (d[i] > 0):
            m[i] = 0.0  # local extremum → flat (horizontal) tangent
        else:
            w1 = 2*(x[i+1]-x[i]) + (x[i]-x[i-1])
            w2 = (x[i+1]-x[i]) + 2*(x[i]-x[i-1])
            m[i] = (w1 + w2) / (w1/d[i-1] + w2/d[i])  # weighted harmonic mean
    # Limit tangents to avoid overshoot (Fritsch–Carlson limiter)
    for i in range(n-1):
        if d[i] == 0.0:
            m[i] = 0.0
            m[i+1] = 0.0
        else:
            a = m[i] / d[i]
            b = m[i+1] / d[i]
            s = a*a + b*b
            if s > 9.0:  # cap: a^2 + b^2 <= 9
                t = 3.0 / (s**0.5)
                m[i]   = t * a * d[i]
                m[i+1] = t * b * d[i]
    return m, d

def build_monotone_spline(x, y):
    """Return a callable s(t) for t in [x0, xN] with no overshoot and flat peaks."""
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Need >= 2 points")
    # Ensure strictly increasing x
    for i in range(len(x)-1):
        if not x[i+1] > x[i]:
            raise ValueError("x must be strictly increasing")
    m, d = _fritsch_carlson_slopes(x, y)
    # Precompute interval coefficients (Hermite cubic)
    coeffs = []  # per-interval: (x_i, h, y_i, y_{i+1}, m_i, m_{i+1})
    for i in range(len(x)-1):
        h = x[i+1]-x[i]
        coeffs.append((x[i], h, y[i], y[i+1], m[i], m[i+1]))
    def s(t):
        if t <= x[0]: return y[0]
        if t >= x[-1]: return y[-1]
        # binary search for interval
        lo, hi = 0, len(coeffs)-1
        while lo <= hi:
            mid = (lo+hi)//2
            xi, h, yi, yi1, mi, mi1 = coeffs[mid]
            if t < xi:
                hi = mid - 1
            elif t > xi + h:
                lo = mid + 1
            else:
                # Hermite basis
                u = (t - xi)/h
                u2 = u*u; u3 = u2*u
                h00 =  2*u3 - 3*u2 + 1
                h10 =      u3 - 2*u2 + u
                h01 = -2*u3 + 3*u2
                h11 =      u3 -   u2
                return (h00*yi + h10*h*mi + h01*yi1 + h11*h*mi1)
        # fallback
        return y[-1]
    return s

# --- Convenience: hourly interpolation for temp (°F) and humidity (%) --------
def hourly_interp_from_owm(daydata, tz_offset_seconds):
    """
    daydata: list of OWM 'list' entries at 3h cadence.
    Returns dict keyed by unix hour (int) with {'temp_f':..., 'humidity':...}.
    """
    # Collect knots
    xs = []     # hours since epoch (float)
    tF = []     # temperature in F
    hu = []     # humidity in %
    for di in daydata:
        t = int(di['dt']) + int(tz_offset_seconds)  # local wall-clock seconds
        xh = t / 3600.0
        xs.append(xh)
        tF.append((float(di['main']['temp']) - 273.15) * 9/5 + 32.0)
        hu.append(float(di['main']['humidity']))

    # Build splines (shape-preserving, flat at peaks)
    s_temp = build_monotone_spline(xs, tF)
    s_hum  = build_monotone_spline(xs, hu)

    # Fill every hour in range (inclusive of endpoints)
    h0 = int(xs[0])
    h1 = int(xs[-1])
    out = {}
    for H in range(h0, h1+1):
        tf = s_temp(H)
        hm = s_hum(H)
        # clamp to plausible ranges
        hm = max(0.0, min(100.0, hm))
        out[H*3600 - int(tz_offset_seconds)] = {  # back to UTC unix seconds as key
            'temp_f': tf,
            'humidity': hm,
        }
    return out

# print(fn_json)

with open(fn_json,'rt') as F:
	alldata = json.load(F)
daydata = alldata['list']
cityname = alldata['city']['name']
tz = alldata['city']['timezone']
# print(f"{bgblu}                 {gra}==== {whi}{cityname} {rst}{bgblu}{gra}====                 {rst}")
# print(f"Date       Time  Hum T  Temp°f")

#for di in daydata:
#	datetime = di['dt']
#	datestr = di['dt_txt']
#	weather=di['weather'][0]
#	wident = weather['description']
#	wcmt = weather['main']
#	hum = f"{di['main']['humidity']:3d}"
#	hum_color = a24fg(255,255,255)
#	tempk = di['main']['temp']
#	tempf = k2f(tempk)
#	tempkmin = k2f(di['main']['temp_min'])
#	tempkmax = k2f(di['main']['temp_max'])
#	temp_glyph, temp_color = symbols.temp_f_sym(tempf)
#	temp_color = a24fg(*temp_color) if color else ''
#	if wident not in symbols.sym_weather:
#		glyph='?'
#		gwidth=2
#		fg=a24fg(255,255,255) if color else ''
#	else:
#		sym = symbols.sym_weather[wident]['day']
#		glyph, gwidth = symbols.get_glyph(sym)
#		argb = sym['clr_argb']
#		fg=a24fg(argb[0], argb[1], argb[2]) if color else ''
#	bg=a24bg(0,0,154) if color else ''

#	date,time,daycolor = symbols.date_to_str_color(datetime, tz)
#	daycolor = a24bg(*daycolor) if color else ''

#	#print(f"{datestr} {gwidth} {temp_color}{temp_glyph}{rst} {tempf:.2f}°f {bg}{fg} {glyph:{gwidth}}{rst} [{wcmt:8}] {wident}")
#	print(f"{date} {daycolor}{time}{rst} {hum_color}{hum}{rst} {temp_color}{temp_glyph} {tempf:5.1f}°f{rst} {bg}{fg} {glyph:{gwidth}}{rst} [{wcmt:8}] {wident}")

print(f"Date       Time  Hum T  Temp°f")
nearest_weather = build_nearest_weather(daydata)
hourly = hourly_interp_from_owm(daydata, tz)

for t_utc in sorted(hourly.keys()):
	date, time, bg_rgb = symbols.date_to_str_color(t_utc, tz)
	vals = hourly[t_utc]
	tempf = vals['temp_f']
	hum   = int(round(vals['humidity']))
	temp_glyph, temp_rgb = symbols.temp_f_sym(tempf)
	temp_color = a24fg(*temp_rgb) if color else ''
	hum_color  = a24fg(255,255,255) if color else ''
	glyph, gwidth, w_rgb, desc, main = nearest_weather(t_utc)
	fg = a24fg(*w_rgb) if color else ''
	bg = a24bg(*bg_rgb) if color else ''
	print(f"{date} {bg}{time}{rst} {hum_color}{hum:3d}{rst} "
		f"{temp_color}{temp_glyph} {tempf:5.1f}°f{rst} "
		f"{fg}{glyph:{gwidth}}{rst} [{main:8}] {desc}")
