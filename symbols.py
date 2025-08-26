#!/usr/bin/env python3
from bansi import *
from wcwidth import wcwidth
from datetime import datetime, time, timedelta, timezone
import colorsys
import bisect

sym_weather = {
	# Main: 800 Clear
	"clear sky": {
		"day": {
			"glyph": u'\u2600',
			"clr_a256": 226,
			"clr_argb": (255, 245, 0),
			"clr_hex": "#ffd700"
		},
		"night": {
			"glyph": u'\u263D',
			"clr_a256": 255,
			"clr_argb": (160, 160, 160),
			"clr_hex": "#a0a0a0"
		}
	},
	# Main: 80x Clouds
	"few clouds": {
		"day": {
			"glyph": u'\u26C5',
			"clr_a256": 250,
			"clr_argb": (255, 205, 0),
			"clr_hex": "#d2d2d2"
		},
		"night": {
			"glyph": u'\u26C6',
			"clr_a256": 255,
			"clr_argb": (160, 160, 160),
			"clr_hex": "#a0a0a0"
		}
	},
	"scattered clouds": {
		"day": {
			"glyph": u'\u2601',
			"clr_a256": 250,
			"clr_argb": (240, 240, 240),
			"clr_hex": "#d2d2d2"
		},
		"night": {
			"glyph": u'\u2601',
			"clr_a256": 255,
			"clr_argb": (160, 160, 160),
			"clr_hex": "#a0a0a0"
		}
	},
	"broken clouds": {
		"day": {
			"glyph": u'\u2601\u2600',
			# "glyph": u'\u2601',
			"clr_a256": 240,
			"clr_argb": (180, 180, 180),
			"clr_hex": "#b4b4b4"
		},
		"night": {
			"glyph": u'\u2601',
			"clr_a256": 232,
			"clr_argb": (120, 120, 120),
			"clr_hex": "#787878"
		}
	},
	# Main: 50x Rain
	"shower rain": {
		"day": {
			"glyph": u'\u2614',
			"clr_a256": 27,
			"clr_argb": (0, 250, 255),
			"clr_hex": "#0000ff"
		},
		"night": {
			"glyph": u'\u2614',
			"clr_a256": 17,
			"clr_argb": (79, 79, 139),
			"clr_hex": "#00008b"
		}
	},
	"rain": {
		"day": {
			"glyph": u'\u2614',
			"clr_a256": 21,
			"clr_argb": (0, 250, 255),
			"clr_hex": "#0000d2"
		},
		"night": {
			"glyph": u'\u2614',
			"clr_a256": 18,
			"clr_argb": (0, 250, 255),
			"clr_hex": "#00009b"
		}
	},
	"thunderstorm": {
		"day": {
			"glyph": u'\u26A1',
			"clr_a256": 220,
			"clr_argb": (255, 255, 0),
			"clr_hex": "#ffff00"
		},
		"night": {
			"glyph": u'\u26A1',
			"clr_a256": 226,
			"clr_argb": (255, 215, 0),
			"clr_hex": "#ffd700"
		}
	},
	"snow": {
		"day": {
			"glyph": u'\u2744',
			"clr_a256": 15,
			"clr_argb": (255, 255, 255),
			"clr_hex": "#ffffff"
		},
		"night": {
			"glyph": u'\u2744',
			"clr_a256": 15,
			"clr_argb": (255, 255, 255),
			"clr_hex": "#ffffff"
		}
	},
	"mist": {
		"day": {
			"glyph": u'\u2591',
			"clr_a256": 250,
			"clr_argb": (210, 210, 210),
			"clr_hex": "#d2d2d2"
		},
		"night": {
			"glyph": u'\u2591',
			"clr_a256": 232,
			"clr_argb": (120, 120, 120),
			"clr_hex": "#787878"
		}
	},
	"overcast clouds": {
		"day": {
			"glyph": u'\u2601',  # unicode character for cloud
			"clr_a256": 237,  # darker gray
			"clr_argb": (136, 136, 136),  # darker gray
			"clr_hex": "#888888"  # darker gray
		},
		"night": {
			"glyph": u'\u2601',  # unicode character for cloud
			"clr_a256": 232,  # very dark gray
			"clr_argb": (120, 120, 120),  # very dark gray
			"clr_hex": "#787878"  # very dark gray
		}
	},
	"light rain": {
		"day": {
			"glyph": u'\u2614',  # umbrella with rain drops
			"clr_a256": 39,  # light blue
			"clr_argb": (140, 200, 255),
			"clr_hex": "#4682b4"
		},
		"night": {
			"glyph": u'\u2614',
			"clr_a256": 18,
			"clr_argb": (0, 0, 128),
			"clr_hex": "#000080"
		}
	},
	"moderate rain": {
		"day": {
			"glyph": u'\u2614',
			"clr_a256": 27,
			"clr_argb": (80, 140, 255),
			"clr_hex": "#0000ff"
		},
		"night": {
			"glyph": u'\u2614',
			"clr_a256": 18,
			"clr_argb": (0, 0, 128),
			"clr_hex": "#000080"
		}
	},
	"heavy intensity rain": {
		"day": {
			"glyph": u'\u2614',
			"clr_a256": 21,
			"clr_argb": (0, 0, 139),
			"clr_hex": "#00008b"
		},
		"night": {
			"glyph": u'\u2614',
			"clr_a256": 18,
			"clr_argb": (0, 0, 128),
			"clr_hex": "#000080"
		}
	},
	# Main: 30x Drizzle
	"light intensity drizzle": {
		"day": {
			"glyph": u'\u2614',  # umbrella with rain drops
			"clr_a256": 39,  # light blue
			"clr_argb": (70, 130, 180),
			"clr_hex": "#4682b4"
		},
		"night": {
			"glyph": u'\u2614',
			"clr_a256": 18,
			"clr_argb": (0, 0, 128),
			"clr_hex": "#000080"
		}
	},
	"drizzle": {
		"day": {
			"glyph": u'\u2614',
			"clr_a256": 27,
			"clr_argb": (0, 0, 255),
			"clr_hex": "#0000ff"
		},
		"night": {
			"glyph": u'\u2614',
			"clr_a256": 18,
			"clr_argb": (0, 0, 128),
			"clr_hex": "#000080"
		}
	},
	"heavy intensity drizzle": {
		"day": {
			"glyph": u'\u2614',
			"clr_a256": 21,
			"clr_argb": (0, 0, 139),
			"clr_hex": "#00008b"
		},
		"night": {
			"glyph": u'\u2614',
			"clr_a256": 18,
			"clr_argb": (0, 0, 128),
			"clr_hex": "#000080"
		}
	},
	# Main: 2xx Thunderstorm
	"thunderstorm with light rain": {
		"day": {
			"glyph": u'\u26C8',  # thunder cloud and rain
			"clr_a256": 33,  # dark blue
			"clr_argb": (70, 130, 180),
			"clr_hex": "#4682b4"
		},
		"night": {
			"glyph": u'\u26C8',
			"clr_a256": 17,
			"clr_argb": (0, 0, 128),
			"clr_hex": "#000080"
		}
	},
	"thunderstorm with rain": {
		"day": {
			"glyph": u'\u26C8',
			"clr_a256": 27,
			"clr_argb": (0, 0, 255),
			"clr_hex": "#0000ff"
		},
		"night": {
			"glyph": u'\u26C8',
			"clr_a256": 17,
			"clr_argb": (0, 0, 128),
			"clr_hex": "#000080"
		}
	},
	"thunderstorm with heavy rain": {
		"day": {
			"glyph": u'\u26C8',
			"clr_a256": 21,
			"clr_argb": (0, 0, 139),
			"clr_hex": "#00008b"
		},
		"night": {
			"glyph": u'\u26C8',
			"clr_a256": 17,
			"clr_argb": (0, 0, 128),
			"clr_hex": "#000080"
		}
	},
}

def get_glyph(sym):
	glyph = sym['glyph']
	# gwidth=wcwidth(glyph)
	gwidth = sum(map(wcwidth, glyph))
	if gwidth == 1: gwidth=2
	elif gwidth == 2:gwidth = 1
	return glyph, gwidth

def temp_f_sym(temp_f):
	# Define color and glyph ranges
	temp_ranges = [-459.67, 32, 77, 91, 109, 108]
	rgb_ranges = [(255, 255, 255), (255, 255, 255), (255, 255, 0), (255, 128, 0), (255, 0, 0), (255, 0, 0)]
	glyph_ranges = ["▁", "▁", "▄", "▆", "▇", "█"]
	
	# Find the appropriate range for the temperature
	for i in range(len(temp_ranges)-1):
		if temp_ranges[i] <= temp_f < temp_ranges[i+1]:
			# Linearly interpolate RGB values
			t = (temp_f - temp_ranges[i]) / (temp_ranges[i+1] - temp_ranges[i])
			r = int((1-t) * rgb_ranges[i][0] + t * rgb_ranges[i+1][0])
			g = int((1-t) * rgb_ranges[i][1] + t * rgb_ranges[i+1][1])
			b = int((1-t) * rgb_ranges[i][2] + t * rgb_ranges[i+1][2])
			color = (r, g, b)

			# Select the appropriate glyph
			glyph = glyph_ranges[i]
			return glyph, color
	
	# If temperature is above the defined range, return the maximum values
	return "█", (255, 0, 0)

# ---- Color Helpers ---------------------------------------------------------

def _lerp(a, b, t):
    return a + (b - a) * t

def _smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)

def _hsv_to_rgb255(h, s, v):
    r, g, b = colorsys.hsv_to_rgb((h % 360.0) / 360.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))

def _lerp_hue_long_arc(h1, h2, t):
    """Interpolate hue h1->h2 taking the long way (via red) to avoid green.
    Returns hue in [0,360).
    """
    h1 %= 360.0
    h2 %= 360.0
    if h2 < h1:
        h2 += 360.0
    # If crossing green (~120°), force wrap forward one more turn to go via red
    if h1 <= 120.0 <= h2:
        h2 += 360.0
    return (h1 + (h2 - h1) * t) % 360.0

def _lerp_hue_short_arc(h1, h2, t):
    """Shortest-arc hue interpolation. May pass near green depending on endpoints."""
    h1 %= 360.0
    h2 %= 360.0
    d = (h2 - h1 + 540.0) % 360.0 - 180.0
    return (h1 + d * t) % 360.0

# ---- HSVFader --------------------------------------------------------------

class HSVFader:
    """
    Keyframed HSV timeline on t ∈ [0,1) with per-segment options.

    Usage:
        f = HSVFader().set0(t=0.0, h=210, s=0.65, v=0.12)
        f.add_point(t=0.1875, v=0.20)                                    # ~04:30 early pre-dawn
        f.add_point(t=0.29, hsv=(210, 0.55, 0.80), smoothstep=True)      # morning blue
        f.add_point(t=0.5,  hsv=(210, 0.45, 0.92))                       # noon, dark-cyan blue
        f.add_point(t=17/24, hsv=(30, 0.95, 1.00), smoothstep=True, avoidgreen=True)  # 17:00 sunset
        f.add_point(t=21/24, hsv=(30, 0.75, 0.60))                        # dusk
        f.add_point(t=1.0,  hsv=(210, 0.65, 0.12))                        # wrap to midnight
        rgb = f.rgb_at(0.71)  # sample at some t
    """
    def __init__(self):
        # Each point: {t, h, s, v, smoothstep (bool), avoidgreen (bool)}
        self.points = []

    def set0(self, t=0.0, h=None, s=None, v=None, hsv=None, smoothstep=True, avoidgreen=False):
        self.points = []
        return self.add_point(t=t, h=h, s=s, v=v, hsv=hsv, smoothstep=smoothstep, avoidgreen=avoidgreen)

    def add_point(self, t, h=None, s=None, v=None, hsv=None, smoothstep=True, avoidgreen=False):
        t = float(t) % 1.0
        if hsv is not None:
            if isinstance(hsv, (tuple, list)) and len(hsv) == 3:
                h, s, v = hsv
            elif isinstance(hsv, dict):
                h = hsv.get('h', h)
                s = hsv.get('s', s)
                v = hsv.get('v', v)
        pt = {'t': t, 'h': h, 's': s, 'v': v, 'smoothstep': bool(smoothstep), 'avoidgreen': bool(avoidgreen)}
        # insert in sorted order by t; replace if same t
        ts = [p['t'] for p in self.points]
        i = bisect.bisect_right(ts, t)
        if i > 0 and abs(ts[i-1] - t) < 1e-9:
            self.points[i-1] = pt
        else:
            self.points.insert(i, pt)
        return self

    # internal: fetch bracketing points with wrap support
    def _segment_for(self, t):
        if not self.points:
            raise ValueError("No keyframes in HSVFader")
        t = float(t) % 1.0
        ts = [p['t'] for p in self.points]
        i = bisect.bisect_right(ts, t)
        i0 = (i - 1) if i > 0 else len(self.points) - 1
        i1 = i % len(self.points)
        p0 = self.points[i0]
        p1 = self.points[i1]
        t0 = p0['t']
        t1 = p1['t'] if p1['t'] > t0 else p1['t'] + 1.0
        u = 0.0 if t1 == t0 else ((t - t0) % 1.0) / (t1 - t0)
        return p0, p1, u

    def hsv_at(self, t):
        p0, p1, u = self._segment_for(t)
        # carry-forward unspecified channels
        def carry(name):
            a = p0[name]
            b = p1[name] if p1[name] is not None else a
            return a, b
        h0, h1 = carry('h')
        s0, s1 = carry('s')
        v0, v1 = carry('v')
        # easing
        if p1.get('smoothstep', False):
            u_e = _smoothstep(u)
        else:
            u_e = u
        # hue interpolation
        if h0 is None and h1 is None:
            h = 0.0
        elif h0 is None:
            h = float(h1)
        elif h1 is None:
            h = float(h0)
        else:
            if p1.get('avoidgreen', False):
                h = _lerp_hue_long_arc(float(h0), float(h1), u_e)
            else:
                h = _lerp_hue_short_arc(float(h0), float(h1), u_e)
        # s, v
        s = _lerp(float(s0 if s0 is not None else 0.0), float(s1 if s1 is not None else s0), u_e)
        v = _lerp(float(v0 if v0 is not None else 0.0), float(v1 if v1 is not None else v0), u_e)
        # clamp s,v
        s = max(0.0, min(1.0, s))
        v = max(0.0, min(1.0, v))
        return (h, s, v)

    def rgb_at(self, t):
        return _hsv_to_rgb255(*self.hsv_at(t))

# ---- Example: date_to_str_color using HSVFader -----------------------------

H_BLUE   = 210.0
H_ORANGE =  30.0
H_RED    =   4.0

# You can adjust these once and keep date_to_str_color tiny.
_fader = (
    HSVFader()
      .set0(     t=0.0,      h=H_BLUE,  s=0.65, v=0.12)    # midnight plateau (readable, not black)
      .add_point(t=4.5/24,                      v=0.20)    # ~04:30 slightly brighter pre-dawn
      .add_point(t=  6/24, hsv=(H_RED,    0.75,   0.52), avoidgreen=True) 
      .add_point(t=  7/24, hsv=(H_ORANGE, 0.75,   0.60))
      .add_point(t=  8/24, hsv=(H_BLUE,   0.55,   0.50))
      .add_point(t= 10/24, hsv=(H_BLUE,   0.55,   0.80))
      .add_point(t= 12/24, hsv=(H_BLUE,   0.45,   0.92))   # noon: dark-cyan blue
      .add_point(t= 15/24, hsv=(H_BLUE,   0.45,   0.70))   # 3pm
      .add_point(t= 18/24, hsv=(H_BLUE,   0.45,   0.50))   # 6pm
      .add_point(t= 19/24, hsv=(H_ORANGE, 0.75,   0.60), avoidgreen=True)    # 21:00 dusk
      .add_point(t= 20/24, hsv=(H_RED,    0.75,   0.52), avoidgreen=True) 
      .add_point(t= 21/24, hsv=(H_BLUE,   0.65,   0.18), avoidgreen=True)
      .add_point(t= 24/24, hsv=(H_BLUE,   0.65,   0.12))    # wrap back to midnight
)

def date_to_str_color(unixtime_utc, timezone_offset_seconds):
    tz = timezone(timedelta(seconds=timezone_offset_seconds))
    date = datetime.fromtimestamp(unixtime_utc, tz)
    year, month, day = date.year, date.month, date.day
    hour, minute = date.hour, date.minute

    # Fraction of the day in [0,1)
    t = ((hour * 60) + minute) / (24.0 * 60.0)

    color = _fader.rgb_at(t)
    return f"{year}-{month:02d}-{day:02d}", f"{hour:02d}:{minute:02d}", color
	# Return the date, time, and color

def show_syms_weather():
	for s in sym_weather:
		a256=sym_weather[s]['day']['clr_a256']
		argb=sym_weather[s]['day']['clr_argb']
		glyph=sym_weather[s]['day']['glyph']
		hex=sym_weather[s]['day']['clr_hex']
		fg=a24fg(argb[0], argb[1], argb[2])
		bg=a24bg(255,50,50)
		# gwidth=wcwidth(glyph)
		gwidth = sum(map(wcwidth, glyph))
		if gwidth == 1: gwidth=2
		else: gwidth = 1
		print(f"{s:17} {gwidth} {bg}{fg}{glyph:{gwidth}}{rst}")

def sym_temp_str(glyph, color):
	fg = a24fg(*color)
	bg = a24bg(0, 0, 0) # black background
	return f'{bg}{fg}{glyph}{rst}'

def print_sym_temp(glyph, color):
	print(sym_temp_str(glyph, color))

# ▁        9601     2581     Lower one eighth block
# ▂        9602     2582     Lower one quarter block
# ▃        9603     2583     Lower three eighths block
# ▄        9604     2584     Lower half block
# ▅        9605     2585     Lower five eighths block
# ▆        9606     2586     Lower three quarters block
# ▇        9607     2587     Lower seven eighths block
# █        9608     2588     Full block

def show_syms_temperature():
	print_sym_temp(*temp_f_sym(-100))	# ('▁', (255, 255, 255))
	print_sym_temp(*temp_f_sym(32))	# ('▁', (255, 255, 255))
	print_sym_temp(*temp_f_sym(45))	# ('▁', (255, 204, 0))
	print_sym_temp(*temp_f_sym(60))	# ('▃', (255, 204, 0))
	print_sym_temp(*temp_f_sym(77))	# ('▄', (255, 255, 0))
	print_sym_temp(*temp_f_sym(79))	# ('▅', (255, 128, 0))
	print_sym_temp(*temp_f_sym(95))	# ('▇', (255, 50, 0))
	print_sym_temp(*temp_f_sym(108))	# ('█', (255, 0, 0))
	print_sym_temp(*temp_f_sym(120))	# ('█', (255, 0, 0))

if __name__ == '__main__':
	# show_syms_weather()
	show_syms_temperature()
