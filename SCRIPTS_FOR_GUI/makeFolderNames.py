from os.path import join
import os
from datetime import datetime
import shutil
import sys

TIME_FORMAT =  "%Y-%m-%d_%H-%M-%S"

"""
SelectedMGFSpectra_Min(Field1)(Field2)ions_MinIntensity(Field3)_MassError(Field4)ppm
SelectedReporters_Min(Field1)(Field2)ions_MinIntensity(Field3)_MassError(Field4)ppm
SelectedReporters_Min(Field1)(Field2)ions_MinIntensity(Field3)_InitialMassError(Field4)ppm_RecalMassError(Field5)

Field1=minimum reporters with said intensity
Field2= value from reporter type field
Field3=Minimum Intensity per reporter
Field4=m/z error for initial runthrough
Field5=m/z error for initial runthrough

"""


def construct_selected_mgf_path(form):

	if form['performRecalibration'] == "0":
		a = "MGFSpectraSelected_Min" + str(form['minReporters']) + str(form['reporterIonType']) + "ions" + \
			"_MinIntensity" + str(form['minIntensity']) + "_MassError" + str(form['mzError']) + "ppm"
		a = a.replace('.','-')

		full_path = join(form['mgfReadDirPath'], a, '')
		return full_path

	elif form['performRecalibration'] == "1":
		a = "MGFSpectraSelected_Min" + str(form['minReporters']) + str(form['reporterIonType']) + "ions" + \
			"_MinIntensity" + str(form['minIntensity']) + "_InitialMassError" + str(form['mzErrorInitialRun']) + \
			"ppm_RecalMassError" + str(form['mzErrorRecalibration']) + "ppm"
		a = a.replace('.','-')

		full_path = join(form['mgfReadDirPath'], a, '')
		return full_path

	else:
		raise Exception("Did not catch anything, must be a bad input")


def construct_reporter_folder_path(form):
	if form['performRecalibration'] == "0":
		a = "ReportersSelected_Min" + str(form['minReporters']) + str(form['reporterIonType']) + "ions" + \
			"_MinIntensity" + str(form['minIntensity']) + "_MassError" + str(form['mzError']) + "ppm"
		a = a.replace('.','-')

		full_path = join(form['mgfReadDirPath'], a, '')

		return full_path

	elif form['performRecalibration'] == "1":
		a = "ReportersSelected_Min" + str(form['minReporters']) + str(form['reporterIonType']) + "ions" + \
			"_MinIntensity" + str(form['minIntensity']) + "_InitialMassError" + str(form['mzErrorInitialRun']) + \
			"ppm_RecalMassError" + str(form['mzErrorRecalibration']) + "ppm"
		a = a.replace('.','-')
		
		full_path = join(form['mgfReadDirPath'], a, '')

		return full_path

	else:
		raise Exception("Did not catch anything, must be a bad input")


def construct_short_reporter_folder_path(form):
	timestamp = datetime.now().strftime(TIME_FORMAT)
	fullpath = join(form['mgfReadDirPath'], "ReporterSelect_"+timestamp , "")
	return fullpath


def construct_plain_parse_reporter_folder_path(form):
	a = os.path.splitext(os.path.basename(str(form['xmlReadPath'])))[0]+'_plain_parse'
	full_path = join(form['mgfReadDirPath'], a, '')
	return full_path


def construct_merged_gpm_reporter_filename(form):
	reporter_path = None
	if form['mgfOperationToPerform'] == '1':
		reporter_path = construct_reporter_folder_path(form)
	reporter_path = form['mgfTxtReadDirPath']
	parent_xml_basename = os.path.basename(os.path.normpath(form["xmlReadPath"]))
	parent_xml_filename = parent_xml_basename.rsplit('.', 1)[0]
	outfile_name = join(reporter_path, parent_xml_filename + '-pep-reporter-merged.txt')
	return outfile_name


def rename_folders(form, timestamp):
	print "in rename"
	if form['mgfOperationToPerform'] == '0':
		print "in first if"
		#tab 1 - select reporters
		if 'xmlReadPath' not in form:
			mgf_folder_name = construct_reporter_folder_path(form)
			new_mgf_folder_name = join(form['mgfReadDirPath'], "rep_sel_"+timestamp, '')
			os.rename(mgf_folder_name, new_mgf_folder_name)
			return
		#tab 2 - use pre extracted reporters
		else:
			# don't rename
			return
	else:
		#tab 1 - select reporters and make mgf
		if 'xmlReadPath' not in form:
			mgf_folder_name = construct_selected_mgf_path(form)
			new_mgf_folder_name = join(form['mgfReadDirPath'], "mgf_sel_"+timestamp, '')
			os.rename(mgf_folder_name, new_mgf_folder_name)
			reporter_folder_name = construct_reporter_folder_path(form)
			new_reporter_folder_name = join(form['mgfReadDirPath'], "rep_sel_"+timestamp, '')
			os.rename(reporter_folder_name, new_reporter_folder_name)
			return

		#tab 4 - plain parse & tab 2 - use raw MGF files
		reporter_folder_name = ''
		new_reporter_folder_name = ''
		mgf_folder_name = ''
		new_mgf_folder_name  = ''
		output_suffix = ''

		if 'plain_parse' in form:
			output_suffix = "plain_parse_"
			reporter_folder_name = construct_plain_parse_reporter_folder_path(form)
		else:
			mgf_folder_name = construct_selected_mgf_path(form)
			reporter_folder_name = construct_reporter_folder_path(form)
			output_suffix = "rep_sel_"

			if form['outDirPath'] == '':
				new_mgf_folder_name = join(sys.path[0], "Archive", "mgf_sel_"+timestamp, '')
			else:
				new_mgf_folder_name = join(form['outDirPath'], "mgf_sel_"+timestamp, '')

			if form['removeMGF'] == '0':
				shutil.rmtree(mgf_folder_name)
			else:
				shutil.copytree(mgf_folder_name, new_mgf_folder_name)
				shutil.rmtree(mgf_folder_name)

		if form['removeReporters'] == '0':
			reporter_folder_files=os.listdir(reporter_folder_name)
			for filename in reporter_folder_files:
				if filename.endswith(".reporter"):
					os.remove(join(reporter_folder_name, filename))
		
		#write to output directory if one given, else write to IDEAA/Archive/
		if form['outDirPath'] == '':
			new_reporter_folder_name = join(sys.path[0], "Archive", output_suffix+timestamp, '')
		else:
			new_reporter_folder_name = join(form['outDirPath'], output_suffix+timestamp, '')

		shutil.copytree(reporter_folder_name, new_reporter_folder_name)
		shutil.rmtree(reporter_folder_name)
		return