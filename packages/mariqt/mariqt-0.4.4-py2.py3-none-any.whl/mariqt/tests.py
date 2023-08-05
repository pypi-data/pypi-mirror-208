""" This file contains various validation functions to check whether given parameters adhere to the MareHub AG V/I conventions"""

import os
import datetime
import copy

import mariqt.variables as miqtv
import mariqt.directories as miqtd
import mariqt.core as miqtc
import mariqt.image as miqti

def isValidPerson(o:dict,msg=[]):
	""" Checks whether the dict contains the fields needed to identify a person"""
	if not isinstance(o,dict):
		msg.append("person is not a dict")
		return False
	req = miqtv.req_person_fields
	for r in req:
		if not r in o or o[r] == "":
			continue
		
		if r == "email" and not isValidEmail(o[r]):
			msg.append("invalid email")
			return False
		if r == "orcid" and not isValidOrcid(o[r]):
			msg.append("invalid orcid")
			return False
	return True


def isValidDatapath(path:str):
	""" Check whether a path leads to a proper leaf data folder (raw, processed, etc.)"""
	try:
		d = miqtd.Dir(path)
		return d.validDataDir()
	except:
		return False


def isValidEventName(event:str):
	""" Check whether an event name follows the conventions: <project>[-<project part>]_<event-id>[-<event-id-index>][_<device acronym>]"""
	tmp = event.split("_")
	if len(tmp) < 2 or len(tmp) > 3:
		return False
	tmp2 = tmp[0].split("-")
	if len(tmp2) == 2:
		try:
			int(tmp2[1])
		except:
			return False

	tmp2 = tmp[1].split("-")
	if len(tmp2) == 1:
		try:
			int(tmp2[0])
		except:
			return False
	elif len(tmp2) == 2:
		try:
			int(tmp2[0])
			int(tmp2[1])
		except:
			return False
	else:
		return False
	return True


def isValidEquipmentID(eqid:str):
	""" Check whether an equipment id follows the convention: <owner>_<type>-<type index[_<subtype>[_<name>]]>"""
	eq = eqid.split("_")
	if len(eq) < 2:
		print("too short")
		return False
	eq2 = eq[1].split("-")
	if len(eq2) != 2:
		print("second too short")
		return False
	try:
		int(eq2[1])
	except:
		print("second second no int")
		return False
	if eq2[0] not in miqtv.equipment_types:
		print(eq2[0],"not in eq types")
		return False
	return True


def isValidImageName(name:str):
	""" Check whether an image filename adheres to the convention: <event>_<sensor>_<date>_<time>.<ext>.
		Returns [valid:bool,msg:str] """
	event, sensor = miqti.parseImageFileName(name)
	if event == "" and sensor == "":
		return [False, "invalid equipment type, could not parse image file name"]
	
	# check if from field before sensor part till timestamp is valid equipment id (e.g. GMR_CAM-12)
	if not isValidEquipmentID(sensor):
		return [False, "\'" + sensor + "\' is not a valid equipment id"]

	if not isValidEventName(event):
		return [False, "\'" + event + "\' is not a valid event name"]

	# check if file extension in miqtv.image_types
	tmp = name.split("_")
	pos = tmp[-1].rfind(".")
	ext = tmp[-1][pos+1:].lower()
	if not ext in miqtv.image_types:
		return [False, "\'" + ext + "\'  is not a valid image type"]


	try:
		miqtc.parseFileDateTimeAsUTC(name)
	except:
		return [False,"cannot parse date time"]

	return [True, ""]


def isValidiFDOField(field,value,fieldDefinition=miqtv.ifdo_fields):
	""" Tries to parse value to field's dataType and throws exception if it does not succeed """
	
	if 'valid' in fieldDefinition[field] and value not in fieldDefinition[field]['valid']:
		raise miqtc.IfdoException(field+": value \"" + str(value) + "\" not in " + str(fieldDefinition[field]['valid']))
	elif field in ['image-filename']:
		if not isValidImageName(value)[0]:
			raise miqtc.IfdoException('Invalid item name',str(value),isValidImageName(value)[1])
	elif field in ['image-datetime']:
		try:
			format = miqtv.date_formats['mariqt']
			datetime.datetime.strptime(value,format)
		except:
			raise miqtc.IfdoException('Invalid datetime value',str(value), "does not match format:",format)
	
	elif field in ['image-longitude']:
		try:
			value = float(value)
		except:
			raise miqtc.IfdoException(field,'value is not a float',str(value))
		if value < -180 or value > 180:
			raise miqtc.IfdoException(field,'value is out of bounds',str(value))
	elif field in ['image-latitude']:
		try:
			value = float(value)
		except:
			raise miqtc.IfdoException(field,'value is not a float',str(value))
		if value < -90 or value > 90:
			raise miqtc.IfdoException(field,'value is out of bounds',str(value))
	elif field in ['image-depth']:
		try:
			value = float(value)
		except:
			raise miqtc.IfdoException(field,'value is not a float',str(value))
		if value < -1: # it can happen that pressure sensors measure small negative depth at surface
			raise miqtc.IfdoException(field,'value is out of bounds',str(value))
	elif field in ['image-altitude']:
		try:
			value = float(value)
		except:
			raise miqtc.IfdoException(field,'value is not a float',str(value))
		if value < 0:
			raise miqtc.IfdoException(field,'value is out of bounds',str(value))
	elif field in ['image-abstract']:
		if len(value) < 500 or len(value) > 2000:
			raise miqtc.IfdoException("Length of the abstract ("+ str(len(value)) +") is too long (max. 2000 chars) or too short (min 500 chars)")
	elif field in ['image-pi']:
		msg = []
		if not isValidPerson(value,msg):
			raise miqtc.IfdoException("Not a valid person description for the pi: "+msg[0],str(value))
	elif field in ['image-creators']:
		for p in value:
			msg = []
			if not isValidPerson(p,msg):
				raise miqtc.IfdoException("Not a valid person description for one of the creators: "+msg[0],str(value))
	elif field in ['image-coordinate-uncertainty-meters']:
		try:
			value = float(value)
		except:
			raise miqtc.IfdoException(field,'value is not a float',str(value))
		if value < 0:
			raise miqtc.IfdoException(field,'value is out of bounds',str(value))
	elif field in fieldDefinition:
		if 'dataType' in fieldDefinition[field]:
			if fieldDefinition[field]['dataType'] == miqtv.dataTypes.float:
				try:
					value = float(value)
				except:
					raise miqtc.IfdoException(field,'value is not a float',str(value))
			if fieldDefinition[field]['dataType'] == miqtv.dataTypes.int:
				try:
					value = int(value)
				except:
					raise miqtc.IfdoException(field,'value is not a float',str(value))
			elif fieldDefinition[field]['dataType'] == miqtv.dataTypes.uuid:
				if not miqtc.is_valid_uuid(value):
					raise miqtc.IfdoException(field,"invalid uuid 4:",str(value))
	else:
		print("Unknown field \"" + field + "\"")
	
	return value


def isValidiFDOItem(item:dict,header:dict,reqFields:dict=miqtv.ifdo_item_core_fields):
	""" Returns list of fields which are missing to achieve FAIRness for the item and throws Exception if any field is filled invalidly. """
	missingFieldsForFairness = []
	for req in [ k for k,v in reqFields.items() if v['fairnessReq']]:

		field_found_in = None

		# add alt fields
		altFields = []
		if 'alt-fields' in reqFields[req]:
			altFields = [alt for alt in reqFields[req]['alt-fields'] if alt != '']
		reqAndAlts = [req] + altFields
		fieldName = ""
		for field in reqAndAlts:

			fieldName = field
			# check in item
			if field in item and item[field] != "":
				field_found_in = item
				break
			# check in header
			if field in header and header[field] != "":
				field_found_in = header
				break

		# A required field nor its alternative was not found in item or header
		if field_found_in == None:
			missingFieldsForFairness.append(req)
		else:
			# A required field was found, now check its value
			field_found_in[fieldName] = isValidiFDOField(fieldName,field_found_in[fieldName],fieldDefinition=reqFields)

			# check sub fields:
			if 'subFields' in reqFields[req]:
				subitem = copy.deepcopy(field_found_in[fieldName])
				# list
				if reqFields[req]['dataType'] == miqtv.dataTypes.list:
					if not isinstance(subitem,list):
						raise miqtc.IfdoException(fieldName + " must be a list")
					subitems = subitem
				# dict
				else:
					subitems = [subitem]
				for subitem in subitems:
					if not isinstance(subitem,dict):
						subitem = {}
					subMissing = isValidiFDOItem(subitem,{},reqFields[req]['subFields'])
					if len(subMissing) != 0:
						missingFieldsForFairness.append(req + ":" + str(subMissing))

	return missingFieldsForFairness


def isValidiFDOCoreHeader(header:dict):
	""" Returns list of fields which are missing to achieve FAIRness for the header and throws Exception if any field is filled invalidly. """
	missingFieldsForFairness = []
	for req in [ k for k,v in miqtv.ifdo_header_core_fields.items() if v['fairnessReq']]:

		field_found = False
		alt_field_found = False

		if req in header and header[req] != "":
			field_found = True
		elif 'alt-fields' in miqtv.ifdo_header_core_fields[req] and len(miqtv.ifdo_header_core_fields[req]['alt-fields']) > 0:
			for alt in miqtv.ifdo_header_core_fields[req]['alt-fields']:
				if alt in header and header[alt] != "":
					alt_field_found = True

		# A required field was not found
		if not field_found:
			if not alt_field_found:
				missingFieldsForFairness.append(req)
		else:
			# Validata values
			header[req] = isValidiFDOField(req,header[req])

	return missingFieldsForFairness


def isValidiFDOCapture(iFDO:dict):
	""" Returns fields of variables.ifdo_capture_fields which are missing in iFDO and throws exception if a field contains an invalid value"""
	return isValidiFDO(iFDO,miqtv.ifdo_capture_fields)
def isValidiFDOContent(iFDO:dict):
	""" Returns fields of variables.ifdo_content_fields which are missing in iFDO and throws exception if a field contains an invalid value"""
	return isValidiFDO(iFDO,miqtv.ifdo_content_fields)


def isValidiFDO(iFDO:dict,ref:dict):
	""" Returns fields of ref which are missing in iFDO and throws exception if a field contains an invalid value"""
	vals_missing = []

	if 'image-set-header' not in iFDO or 'image-set-items' not in iFDO:
		raise Exception("iFOD does not contain 'image-set-header' or 'image-set-items'")

	prog = miqtc.PrintKnownProgressMsg("Checking fields", len(ref), modulo=10)
	for req in ref:
		prog.progress()
		# check if in header
		inHeader = False
		if req in iFDO['image-set-header']:
			iFDO['image-set-header'][req] = isValidiFDOField(req,iFDO['image-set-header'][req])
			inHeader = True

		# if not in header and a 'set' field, its missing
		if req[:9] == 'image-set' and not inHeader:
			vals_missing.append(req)
		# check if in items
		else:
			num = 0
			for item in iFDO['image-set-items']:
				if req not in iFDO['image-set-items'][item]:
					num += 1
				else:
					iFDO['image-set-items'][item][req] = isValidiFDOField(req,iFDO['image-set-items'][item][req])

			if num == len(iFDO['image-set-items']) and not inHeader:
				vals_missing.append(req+": neither the set's header nor any image item contain this field")
			elif num > 0 and not inHeader:
				vals_missing.append(req+": neither the set's header nor "+str(num)+" of "+str(len(iFDO['image-set-items']))+" contain this field")
	prog.clear()
	return vals_missing

	"""
	for req in ref:
		if req[:9] == 'image-set':
			# It is a header field
			if req not in iFDO['image-set-header']:
				vals_missing.append(req)
			else:
				iFDO['image-set-header'][req] = isValidiFDOField(req,iFDO['image-set-header'][req])
		else:
			# It is an item field:
			num = 0
			for item in iFDO['image-set-items']:
				if req not in iFDO['image-set-items'][item]:
					num += 1
				else:
					iFDO['image-set-items'][item][req] = isValidiFDOField(req,iFDO['image-set-items'][item][req])
				
			if num == len(iFDO['image-set-items']):
				vals_missing.append(req+": no image item contains this field")
			elif num > 0:
				vals_missing.append(req+": "+str(num)+" of "+str(len(iFDO['image-set-items']))+" do not contain this field")
	return vals_missing
	"""


def filesHaveUniqueName(files:list):
	""" checks if all files (with or without path) have unique file names. Returns True/False and list of duplicates"""
	fileNames_noPath = []
	duplicates = []
	prog = miqtc.PrintKnownProgressMsg("Checking files have unique name", len(files), modulo=10)
	for file in files:
		prog.progress()
		fileName_noPath = os.path.basename(file)
		if fileName_noPath in fileNames_noPath:
			duplicates.append(fileName_noPath)
		else:
			fileNames_noPath.append(fileName_noPath)
	
	prog.clear()
	if len(duplicates) == 0:
		return True, duplicates
	else:
		return False, duplicates


def isValidOrcid(orcid:str):
	""" returns whether  oricd is valid my using the MOD 11-2 check digit standard """
	# # e.g. "https://orcid.org/0000-0002-9079-593X"
	try:
		orcid = orcid[orcid.rindex("/")+1::]
	except ValueError:
		pass
	if len(orcid) != 19 or orcid[4] != "-" or orcid[9] != "-" or orcid[14] != "-":
		return False

	digits = []
	for char in orcid:
		if char.isdigit():
			digits.append(int(char))
		if char == "X" or char == "x":
			digits.append(10)

	if len(digits) != 16:
		return False

	# MOD 11-2 (see https://www.sis.se/api/document/preview/605987/)
	M = 11
	r = 2

	p = 0
	for digit in digits:
		s = p + digit
		p = s * r
	if s%M == 1:
		return True

	return False


def isValidEmail(mail:str):
	if mail.count("@") == 1:
		return True
	return False


def allImageNamesValidIn(path:miqtd.Dir,sub:str = "raw"):
	""" Validates that all image file names are valid in the given folder."""

	img_paths = miqti.browseForImageFiles(path.tosensor()+"/"+sub+"/")
	return allImageNamesValid(img_paths)

def allImageNamesValid(img_paths:dict):
	invalidImageNames = []
	prog = miqtc.PrintKnownProgressMsg("Checking files have valid name", len(img_paths), modulo=10)
	for file in img_paths:
		prog.progress()
		file_name = os.path.basename(file)
		if not isValidImageName(file_name)[0]:
			invalidImageNames.append(file)
	prog.clear()
	if len(invalidImageNames) != 0:
		return False,"Not all files have valid image names! Rename following files before continuing:\n-" + "\n- ".join(invalidImageNames)
	return True,"All filenames valid"