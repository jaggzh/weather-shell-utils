#!/usr/bin/env python3
from bansi import *
from wcwidth import wcwidth
from datetime import datetime, time, timedelta, timezone

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

def date_to_str_color(unixtime_utc, timezone_offset_seconds):
	# Timezone object for conversion:
	tz = timezone(timedelta(seconds=timezone_offset_seconds))
	date = datetime.fromtimestamp(unixtime_utc, tz)
	# Get the datetime components
	year, month, day = date.year, date.month, date.day
	hour, minute = date.hour, date.minute

	# Define the RGB color values for midnight, morning, noon, and evening
	midnight_color = (0, 0, 0)	# black
	morning_color = (0, 0, 255)  # blue
	noon_color = (0, 205, 235)	# cyan
	evening_color = (255, 165, 0)  # orange

	# Calculate the time of day as a percentage of 24 hours
	time_percent = ((hour * 60) + minute) / (24 * 60)

	# Interpolate the RGB values based on the time of day
	if time_percent < 0.25:  # Morning (0.00-0.25)
		weight = time_percent / 0.25
		color = tuple(int((morning_color[i] - midnight_color[i]) * weight + midnight_color[i]) for i in range(3))
	elif time_percent < 0.5:  # Noon (0.25-0.50)
		weight = (time_percent - 0.25) / 0.25
		color = tuple(int((noon_color[i] - morning_color[i]) * weight + morning_color[i]) for i in range(3))
	elif time_percent < 0.75:  # Evening (0.50-0.75)
		weight = (time_percent - 0.5) / 0.25
		color = tuple(int((evening_color[i] - noon_color[i]) * weight + noon_color[i]) for i in range(3))
	else:  # Midnight (0.75-1.00)
		weight = (time_percent - 0.75) / 0.25
		color = tuple(int((midnight_color[i] - evening_color[i]) * weight + evening_color[i]) for i in range(3))

	# Return the date, time, and color
	return f'{year}-{month:02d}-{day:02d}', f'{hour:02d}:{minute:02d}', color

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

def show_syms_temperature():
	print_sym_temp(*temp_f_sym(-100))	# ('▁', (255, 255, 255))
	print_sym_temp(*temp_f_sym(32))	# ('▁', (255, 255, 255))
	print_sym_temp(*temp_f_sym(45))	# ('▁', (255, 204, 0))
	print_sym_temp(*temp_f_sym(60))	# ('▁', (255, 204, 0))
	print_sym_temp(*temp_f_sym(77))	# ('▄', (255, 255, 0))
	print_sym_temp(*temp_f_sym(81))	# ('▆', (255, 128, 0))
	print_sym_temp(*temp_f_sym(95))	# ('▇', (255, 50, 0))
	print_sym_temp(*temp_f_sym(108))	# ('█', (255, 0, 0))
	print_sym_temp(*temp_f_sym(120))	# ('█', (255, 0, 0))

if __name__ == '__main__':
	# show_syms_weather()
	show_syms_temperature()
