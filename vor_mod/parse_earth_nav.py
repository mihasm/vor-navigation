import re
import os

this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir,"data")

class Waypoint:
	def __init__(self,_type,lat,lng,ele,freq,_range,ident,ident_parent,name):
		self.type = _type
		self.lat = lat
		self.lng = lng
		self.ele = ele
		self.freq = freq
		self.range = _range
		self.ident = ident
		self.ident_parent = ident_parent
		self.name = name

def get_vors():
	"""
	Based on
	http://developer.x-plane.com/wp-content/uploads/2020/03/XP-NAV1150-Spec.pdf
	"""
	f = open(os.path.join(DATA_PATH,"earth_nav.dat"))

	lines = f.readlines()[3:-1]

	out = []

	for l in lines:
		l = re.sub(r' +',' ',l)
		l = re.sub(r'^ ',"",l)
		l = re.sub(r'\n','',l)
		data = l.split(" ")

		w = None

		if data[0] == "2":
			#NDB
			row_code,lat,lng,ele,freq,NDB_class,_,ident,ident_terminal,region_code,name = [d for d in data[:10]]+[" ".join(data[10:])]
			freq = float(freq)/100
			lat = float(lat)
			lng = float(lng)
			w = Waypoint("NDB",lat,lng,ele,freq,NDB_class,ident,ident_terminal,name)
			#out.append(w)
		elif data[0] == "3":
			#VOR
			row_code,lat,lng,ele,freq,VOR_class,slaved_var,ident,ENRT,region,name = [d for d in data[:10]]+[" ".join(data[10:])]
			freq = float(freq)/100
			lat = float(lat)
			lng = float(lng)
			w = Waypoint("VOR",lat,lng,ele,freq,VOR_class,ident,ENRT,name)
			out.append(w)
		elif data[0] == "4" or data[0] == "5":
			# LOC + LDA + SDF
			row_code,lat,lng,ele,freq,rec_range,bearing_true,ident,apt_icao,region,rwy_num,name = [d for d in data[:11]]+[" ".join(data[11:])]
			freq = float(freq)/100
			lat = float(lat)
			lng = float(lng)
			w = Waypoint("ILS",lat,lng,ele,freq,rec_range,ident,apt_icao,name)
			#out.append(w)
		elif data[0] == "6":
			# ILS glideslope
			row_code,lat,lng,ele,freq,rec_range,bearing_true,ident,apt_icao,region,rwy_num,name = [d for d in data[:11]]+[" ".join(data[11:])]
			freq = float(freq)/100
		elif data[0] in ("7","8","9"):
			# Marker beacons
			row_code,lat,lng,ele,_,_,bearing_true,approach_ident,apt_icao,region,rwy_num,name = [d for d in data[:11]]+[" ".join(data[11:])]
		elif data[0] == "12" or data[0]=="13":
			#DME
			row_code,lat,lng,ele,freq,DME_service_volume,bias_NM,ident,apt_icao,region,name = [d for d in data[:10]]+[" ".join(data[10:])]
			freq = float(freq)/100
			#
		elif data[0] == "14":
			#FRAP (Final Approach Course Alignment Point) or SBAS or GBAS point
			row_code,lat,lng,ortho_height,channel,length_offset,app_course,approach_ident,apt_icao,region,rwy_num,perf_ind = [d for d in data[:11]]+[" ".join(data[11:])]
		elif data[0] == "16":
			#LTP/FTP
			row_code,lat,lng,ortho_height,channel,threshold_crossing_height,app_course,approach_ident,apt_icao,region,rwy_num,provider = [d for d in data[:11]]+[" ".join(data[11:])]
	return out