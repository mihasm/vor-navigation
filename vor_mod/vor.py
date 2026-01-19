import sys
import os
import argparse
import random
import webbrowser

import requests
from geomag import geomag
import pyproj
from bs4 import BeautifulSoup as bs
import folium

from vor_mod.parse_earth_nav import get_vors, Waypoint
from vor_mod.parse_airports import get_airports, Airport

list_navaids = get_vors()

geodesic = pyproj.Geod(ellps='WGS84')


gm = geomag.GeoMag()

LOCATION_SCRIPT = os.path.dirname(sys.argv[0])

def get_magnetic_variation(lat,lng):
	mag = gm.GeoMag(lat,lng)
	return mag.dec

def get_metar(icao):
	try:
		# Get METAR
		r_metar = requests.get(f"https://aviationweather.gov/api/data/metar?ids={icao}&format=raw")
		metar_text = ""
		if r_metar.status_code == 200:
			metar_text = r_metar.text.strip()

		# Get TAF
		r_taf = requests.get(f"https://aviationweather.gov/api/data/taf?ids={icao}&format=raw")
		taf_text = ""
		if r_taf.status_code == 200:
			taf_text = r_taf.text.strip()

		# Combine METAR and TAF
		result = ""
		if metar_text:
			result += metar_text + "\n"
		if taf_text:
			result += taf_text + "\n"

		return result.replace("\xa0", " ")  # replace non-visible ascii chars
	except Exception as e:
		return f"Error fetching weather data: {str(e)}"

class PathPoint:
	def __init__(self,nav,course_to=0,dist_to=0,dist_end=0,course_deviation=0,course_end=0,prev_course_deviation=0,normalized_course=0):
		self.object = nav
		self.lat = nav.lat
		self.lng = nav.lng
		if isinstance(nav,Waypoint):
			self.ident = nav.ident
			self.shortname = self.ident
			self.type = "waypoint"
		elif isinstance(nav,Airport):
			self.icao = nav.icao
			self.shortname = self.icao
			self.type = "airport"
		self.course_to = course_to
		self.dist_to = dist_to
		self.dist_end = dist_end
		self.course_deviation = course_deviation
		self.course_end = course_end
		self.prev_course_deviation = prev_course_deviation
		self.normalized_course = normalized_course
		self.weather_str = ""
		self.weather = None
		self.wind_speed = None
		self.wind_dir=None
		self.gust = None
		self.wind = None
		self.wind_altitude = None

class Path:
	def __init__(self,start_point,end_point,cruise_altitude):
		self.path = [start_point]
		self.start_point = start_point
		self.end_point = end_point
		self.cruise_altitude = cruise_altitude # in ft

	def add_to_path(self,point):
		self.path.append(point)

	def nav_in_path(self,nav):
		for p in self.path:
			_nav = p.object
			if _nav == nav:
				return True
		return False

	def last_object(self):
		return self.path[-1].object

	def last_point(self):
		return self.path[-1]

	def calculate_next_potential_point(self,nav):
		last_object = self.last_object()
		course_to,dist_to = self.get_course_distance(last_object,nav)
		course_end,dist_end = self.get_course_distance(nav,self.end_point)
		prev_course_deviation = self.getDifference(course_to,self.last_point().course_to)
		course_deviation = self.getDifference(course_to,course_end)
		normalized_course = self.normalize_course(course_to)
		return {"course_to":course_to,"dist_to":dist_to,"course_end":course_end,"dist_end":dist_end,"prev_course_deviation":prev_course_deviation,"course_deviation":course_deviation,"normalized_course":normalized_course}

	def calculate_last_to_destination(self):
		return self.calculate_next_potential_point(self.end_point.object)

	def normalize_course(self,course):
		if course < 0:
			course += 360
		return int(round(course,0))

	def getDifference(self, b1, b2):
		"""
		Get the angle between two bearings b1 and b2,
		where b1 and b2 are <+-180.
		"""
		r = (b2 - b1) % 360.0
		# Python modulus has same sign as divisor, which is positive here,
		# so no need to consider negative case
		if r >= 180.0:
			r -= 360.0
		return r

	def get_course_distance(self, nav1,nav2):
		origin = (nav1.lng,nav1.lat)
		dest = (nav2.lng,nav2.lat)
		course,_,dist = geodesic.inv(*origin,*dest)
		dist = dist/1000/1.852 # in NM
		return course,dist

	def get_weather_data(self):
		print("getting aviation weather data ")
		for p in self.path:
			sys.stdout.write(".")
			sys.stdout.flush()

			p.magvar = get_magnetic_variation(p.lat,p.lng)

			if p.type == "airport":
				try:
					sys.stdout.write("/")
					sys.stdout.flush()

					metar = get_metar(p.object.icao)
					p.metar = metar
				except Exception as e:
					print("Error fetching METARs:",e)
					p.metar = ""
					pass

		sys.stdout.write("\n")

def get_path(start_point,end_point,MAX_COURSE_DEVIATION=45,MAX_TURN_ANGLE=90,OPTIMUM_NEXT_VOR_DISTANCE=50,max_wpts=100,cruise_altitude=10000):
	path = Path(start_point,end_point,cruise_altitude)
	sys.stdout.write(start_point.shortname+" ")

	for i in range(max_wpts): # to mora biti while True
		res_direct = path.calculate_last_to_destination()
		course_direct,dist_direct = res_direct["course_to"],res_direct["dist_to"]

		best = None
		best_nav = None
		best_score = None
		best_point = None

		for j in range(len(list_navaids)):
			nav = list_navaids[j]

			if not path.nav_in_path(nav):
				res = path.calculate_next_potential_point(nav)

				dist = res["dist_to"]
				dist_end = res["dist_end"]
				course_deviation = res["course_deviation"]
				course = res["course_to"]
				prev_course_deviation = res["prev_course_deviation"]

				distance_score = 1e6/((dist-OPTIMUM_NEXT_VOR_DISTANCE)**2+1)
				course_score = 1/((course_deviation/50)**2+1)

				if dist < dist_direct:
					# najprej preverimo, ali je naslednji potencialni VOR dlje od dejanske destinacije
					if abs(course_deviation) < MAX_COURSE_DEVIATION:

						# nato preverimo, ali je razlika med željeno smerjo in smerjo proti potencialnemu VOR sprejemljiva
						if abs(prev_course_deviation) < MAX_TURN_ANGLE or len(path.path) == 1:
							# nato preverimo, ali nismo naredili prevelike spremembe smeri glede na prejsnjo smer.
							# v kolikor je v poti samo ena tocka, to ignoriramo
							score = 0.9*course_score+0.1*distance_score # dolocimo score
							if best == None or best_score < score:
								best = j
								best_score = score

		if best == None:
			break
		else:
			nav_best = list_navaids[best]
			res = path.calculate_next_potential_point(nav_best)
			best_point = PathPoint(nav_best,**res)
			path.add_to_path(best_point)
			sys.stdout.write(nav_best.ident+" ")
			sys.stdout.flush()

	
	res = path.calculate_next_potential_point(path.end_point.object)
	end_point = PathPoint(path.end_point.object,**res)
	path.add_to_path(end_point)
	sys.stdout.write(end_point.shortname)
	sys.stdout.flush()


	sys.stdout.write("\n")
	return path

def print_data(path):
	metars_print = ""
	for i in range(len(path.path)):
		p = path.path[i]
		o = p.object
		if i > 0:
			print("\tHdg: %i°, Dist: %.1f" % (p.normalized_course,round(p.dist_to,1)))
		if p.type == "airport":
			print("%s Elev: %s Lat: %.2f Lng: %.2f Name: %s MagVar: %.1f" % (p.icao,o.elevation,o.lat,o.lng,o.name,p.magvar))
			metars_print+=p.metar

		if p.type == "waypoint":
			print("%s (%.3f MHz) Elevation: %s Range: %s Name: %s MagVar: %.1f" % (o.ident,o.freq,o.ele,o.range,o.name,p.magvar))

	print("\nMETARs/TAFs:\n")
	print(metars_print)
	print("Number of waypoints:",len(path.path))

def get_airports_dict():
	list_airports = get_airports()
	dict_airports = {}
	for a in list_airports:
		dict_airports[a.icao] = a
	return dict_airports

def visualize(path):
	m = folium.Map(location=[45.5236, -122.6750])

	filepath = os.path.join(LOCATION_SCRIPT,"map.html")
	m = folium.Map()
	
	for p in path.path:
		o = p.object
		if p.type == "airport":
			metar = p.metar.replace("\n","<br>")
			popup = "<b>%s (%s)</b><br>Elev: %s Lat: %.2f Lng: %.2f<br>MagVar: %.1f <br>Metar/TAF:<br>%s" % (p.icao,o.name,o.elevation,o.lat,o.lng,p.magvar,metar)
			tooltip = p.icao
		if p.type == "waypoint":
			popup = "<b>%s (%.3f MHz)</b><br>Elevation: %s<br>Range: %s<br>Name: %s<br>MagVar: %.1f" % (o.ident,o.freq,o.ele,o.range,o.name,p.magvar)
			tooltip = "%s (%.3f MHz)" % (o.ident,o.freq)

		iframe = folium.IFrame(popup)
		popup = folium.Popup(iframe,min_width=500,max_width=500)
		folium.Marker([p.lat,p.lng],popup=popup,tooltip=tooltip).add_to(m)

	line_coords = [[p.lat,p.lng] for p in path.path]
	f_line = folium.PolyLine(locations=line_coords,weight=5)

	m.add_child(f_line)

	m.save(filepath)
	webbrowser.open(filepath)

def main():
	
	to_parse = sys.argv[1:]
	#to_parse = ["--random"]
	#to_parse = ["KLAX","KRDU","--max_deviation","45","--max_turn_angle","90","--optimum_vor_distance","200"]	
	parser = argparse.ArgumentParser(description='Get VOR-only route from one airport to another.')

	if "--random" not in to_parse:
		parser.add_argument("departure",help="ICAO code of departure airport.")
		parser.add_argument("destination",help="ICAO code of destination airport.")
	parser.add_argument("--max_deviation",type=float,default=45,help="Absolute value of maximum deviation between Course(WPT to DEST) and Course(WPT to next WPT) [degrees]. Default: 45")
	parser.add_argument("--max_turn_angle",type=float,default=90,help="Maximum turn from one heading to the next [degrees]. Default: 90")
	parser.add_argument("--optimum_vor_distance",type=float,default=50,help="Optimum distance between VOR's [NM]. Default: 50")
	parser.add_argument("--max_wpts",type=int,default=100,help="Maximum number of generated waypoints before error. Default: 100")
	parser.add_argument("--cruise",type=int,default=10000,help="Cruise altitude in ft (for wind reports). Default: 10 000")
	parser.add_argument("--random",action="store_true")
	args = parser.parse_args(to_parse)

	dict_airports = get_airports_dict()

	if args.random:
		departure = random.choice(list(dict_airports.keys()))
		destination = random.choice(list(dict_airports.keys()-{departure}))
		start_point = PathPoint(dict_airports[departure])
		end_point = PathPoint(dict_airports[destination])
	else:
		start_point = PathPoint(dict_airports[args.departure])
		end_point = PathPoint(dict_airports[args.destination])
	path = get_path(start_point,
					end_point,
					args.max_deviation,
					args.max_turn_angle,
					args.optimum_vor_distance,
					args.max_wpts,
					args.cruise)
	path.get_weather_data()

	print_data(path)

if __name__ == "__main__":
	main()