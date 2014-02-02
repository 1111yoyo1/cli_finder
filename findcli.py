import re,sys,time,datetime,os,shutil

def detect_time_format(str_time):
	try:
		t_time=time.strptime(str_time, '%Y-%m-%d_%H:%M:%S')
	except ValueError:
		t_time=time.strptime(str_time, '%Y-%m-%d %H:%M:%S')
	time_time=datetime.datetime(t_time.tm_year,t_time.tm_mon,t_time.tm_mday,t_time.tm_hour,t_time.tm_min,t_time.tm_sec)
	return time_time

def getdevicenumber(filename):
	f=open(filename,'r')
	for line in f:
		pattern1=re.compile(r'.*<DeviceNumber>(\d{1})</DeviceNumber>')
		match1=pattern1.match(line)
		if match1:
			test_result=match1.group(1)
			f.close() 
			return test_result

def convert_str_to_time(str_time):
	t_str_time=time.strptime(str_time,'%y%m%d %H:%M:%S')
	time_str_time=datetime.datetime(t_str_time.tm_year,t_str_time.tm_mon,\
		t_str_time.tm_mday,t_str_time.tm_hour,t_str_time.tm_min,\
		t_str_time.tm_sec)
	return time_str_time

def get_log_start_end_time(filename,pattern):
	f=open(filename,'r')
	for line in f:
		pattern1=re.compile(r'.*<%s>(.*)</%s>' %(pattern,pattern))
		match1=pattern1.match(line)
		if match1:
			f.close()
			return detect_time_format(match1.group(1))
	 
def closetostarttime(time_current_line_time):
	if (time_start-time_current_line_time).seconds <=120 :  
		return time_current_line_time
	else:
		return None

def closetoendtime(time_current_line_time):
	if (time_current_line_time-time_end-datetime.timedelta(seconds=120)).seconds <=120 \
	and (time_current_line_time-time_end).days ==0:
		return time_current_line_time
	else:
		return None

def getmatchfile(filename, pattern):#match script log and cli log with same machine no
	match_pattern = 'eclid_' + pattern + '.log'
	print "pattern %s" %match_pattern
	print filename
	if filename == match_pattern:
		return filename

# def getmatchfile(filename,pattern):#match script log and cli log with same machine no
# 	temp_machinename=((filename.split('_')[1])).split('-')[0]
# 	if temp_machinename[0:2] =='SH' or temp_machinename[0:2] =='sh':
# 		real_machinename='-'.join((filename.split('_')[1]).split('-')[0:-1])
# 	else:
# 		real_machinename=temp_machinename
# 	if real_machinename==pattern or real_machinename+'-ssdt' ==pattern:
# 		return real_machinename

def getmachineno(log_filename):
	machineno=log_filename.split('_')
	return (machineno[1].split('.')[0]).rstrip('.lsi.com')

def extractcli(filename):
	list_target_cli=[]
	f=open(filename,'r')
	line_count=1
	list_close_end_time=[]
	for line in f:
		pattern1=re.compile(r'.*(\d{6} \d{2}:\d{2}:\d{2}).\d{3}.*')
		match1=pattern1.match(line)
		if match1:
			time_current_line_time=convert_str_to_time(match1.group(1))
			if closetoendtime(time_current_line_time) is not None:
				list_close_end_time.append(line_count) 
		line_count=line_count+1
	f.close() 

	if len(list_close_end_time) != 0:
		print filename
		for f in open(filename,'r').readlines()[0:list_close_end_time[0]]:
			list_target_cli.append(f)
	else:
		pass
	return list_target_cli

def getlogtime(log_filename): #get cli log start time
	log_end_time=(log_filename.split('_')[-2])+' '+(log_filename.split('_')[-1]).rstrip('.log')
	t_log_time=time.strptime(log_end_time,'%Y-%m-%d %H.%M.%S')
	time_log_time=datetime.datetime(t_log_time.tm_year,t_log_time.tm_mon,\
		t_log_time.tm_mday,t_log_time.tm_hour,t_log_time.tm_min,\
		t_log_time.tm_sec)
	return time_log_time

def get_log_modify_endtime(filename): #get last modification time of the script log
	t_str_time=time.localtime(os.path.getmtime(filename))
	time_str_time=datetime.datetime(t_str_time.tm_year,t_str_time.tm_mon,\
	t_str_time.tm_mday,t_str_time.tm_hour,t_str_time.tm_min,\
	t_str_time.tm_sec)
	return time_str_time

def comparelog_start_end_time(time_logfile_start,time_logfile_end,time_cli_start,time_cli_end):
	if time_cli_end is not None or time_cli_end is not None:
		if (time_cli_end-time_logfile_end).days >= 0 and (time_logfile_start-time_cli_start).days >= 0:
			return True
		else:
			return False
	else:
		return False

def find_cli():
	result=None
	list_target_cli=[]
	for filename in os.listdir(ecli_location):
		st1=getmatchfile(filename,machinename)
		if st1 is not None: # firstly we need to find the log matches the exactly same machine
			full_dir_ecli=ecli_location+'/'+filename
			if comparelog_start_end_time(time_start,time_end,getlogtime(full_dir_ecli),get_log_modify_endtime(full_dir_ecli)):
				result=filename
				break
	if result is None:
		print "no fould exactly match, looking for close one"
		for filename in os.listdir(ecli_location):
			st1=getmatchfile(filename,machinename)
			if st1 is not None:
				full_dir_ecli=ecli_location+'\\'+filename
				list_target_cli=extractcli(full_dir_ecli)
				if len(list_target_cli) !=0:
					result=filename
					#print " %s" %list_target_cli 
				else:
					pass
	return list_target_cli, result
	raise Exception("no found close one" )

def cli_exist_infolder(scan_path):
	for files in os.listdir(scan_path):
		full_dir=scan_path+'/'+files
		if files.startswith('eclid_') is True and os.path.isfile(full_dir) is True and os.path.getsize(full_dir) >0:
			return True
	return False

def scan_folder(scan_path):
	for element in os.listdir(scan_path): 
		if element.startswith('eclid') is False:
			return element 
		else:
			pass

def getdir(file_log):
	path='/'.join(file_log.split('/')[0:-1])
	return path

if __name__ == "__main__":
	totalstarttime=time.time()
	
	# #ecli_location=r'\\cn-samba1.sandforce.com\\sqa-logfiles\\eclid'
	# ecli_location=r'/home/yoxu/ecli/'
	# list_need_cli=[]
	# dir1=os.getcwd()
	# if cli_exist_infolder(dir1): #detect if there's a cli file exist
	# 	raise Exception(" already have cli")
	# else:
	# 	pass
	# filename=scan_folder(dir1)        #get the log name which need cli
	# file_log=dir1+'\\'+filename
	# print "script log :" 
	# print "%s" %file_log
	# if file_log	is not None:
	# 	time_start=get_log_start_end_time(file_log,'StartTime')
	# 	time_end=get_log_start_end_time(file_log,'EndTime')
	# 	#time_end=get_log_modify_endtime(file_log)
	# else:
	# 	raw_input("no found log need to get cli")

	# print '\nstart time for script log:%s' %time_start
	# print 'end time for script log:%s' %time_end

	# if time_start is not None and time_end is not None:
	# 	output_dir=dir1+'\\'
	# 	machinename=getmachineno(file_log)    #get the machine name for the script log
	# 	str_target_cli,cli_log=find_cli()
	# 	if len(str_target_cli) == 0:
	# 		if cli_log is not None:
	# 			full_ecli_location=ecli_location+'\\'+cli_log
	# 			full_dir_output=output_dir+'\\'+cli_log
	# 			if os.path.exists(full_dir_output) is False or os.path.getsize(full_dir_output) == 0:  #if the exactly match cli log exist , copy it directly
	# 				print "found cli log, copying"
	# 				print "source file %s" %full_ecli_location
	# 				print "target file %s" %full_dir_output
	# 				print "copying file"
	# 				shutil.copyfile(full_ecli_location,full_dir_output)
	# 				print "copying done"
	# 			elif os.path.getsize(full_dir_output) >209715200: #file size more than 20MB, extract usefull content from the existed cli log
	# 				list_target_cli=extractcli(full_dir_output)
	# 				print "clipping cli file to %s" %full_dir_output
	# 				file_output=open(full_dir_output,'a')
	# 				file_output.writelines(list_target_cli)
	# 				file_output.close()
	# 		else:
	# 			full_dir_output=output_dir+'\\'+cli_log
	# 			print "dumping cli file to %s" %full_dir_output  #didn't find the match cli log, dump the closest one
	# 			file_output=open(full_dir_output,'a')
	# 			file_output.writelines(str_target_cli)
	# 			file_output.close()
	# 	else:
	#  			raw_input("no found cli log")
				#raise Exception("")

	ecli_location ='/home/yoxu/ecli/'
	log_location = '/home/yoxu/log1/ea4_25190/TestDeviceStatisticsLog/'
	if cli_exist_infolder(log_location):  #detect if there's a cli file exist
		raise Exception(" already have cli")

	file_log = scan_folder(log_location)   #get log name that need cli
	
	machinename=getmachineno(file_log)

	for filename in os.listdir(ecli_location):
		target_cli=getmatchfile(filename, machinename) #get match cli file
		if target_cli is not None:
			break
	shutil.copyfile(ecli_location+target_cli, log_location+target_cli)
	#if os.path.getsize(full_dir_output) >209715200: #file size more than 20MB, extract usefull content from the existed cli log




	totalendtime=time.time()
	print totalendtime-totalstarttime
	