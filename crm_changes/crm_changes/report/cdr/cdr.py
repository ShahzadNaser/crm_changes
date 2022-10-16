# Copyright (c) 2013, Shahzad Naser and contributors
# For license information, please see license.txt

from multiprocessing import Condition
import frappe
from frappe import _
import pymysql.cursors

def execute(filters=None):
	columns = [
		_("calldate") + "::120",
		_("src") + "::120",
		_("dst") + "::120",
		_("dcontext") + "::120",
		_("channel") + "::120",
		_("dstchannel") + "::120",
		_("lastapp") + "::120",
		_("lastdata") + "::120",
		_("duration") + "::120",
		_("billsec") + "::120",
		_("disposition") + "::120",
		_("amaflags") + "::120",
		_("accountcode") + "::120",
		_("uniqueid") + "::120",
		_("userfield") + "::120",
		_("recordingfile") + "::100",
		_("cnam") + "::120",
		_("cnam") + "::120",
		_("outbound_cnum") + "::120",
		_("outbound_cnam") + "::120",
		_("dst_cnam") + "::120",
		_("linkedid") + "::120",
		_("sequence") + "::120",
		_("peeraccount") + "::120"
	]

	data = get_data(filters)
	
	return columns, data

def get_data(filters):
	try:
		cn_settings = frappe.get_single("Remote Server Details")
		if not cn_settings.get("hostname") or not cn_settings.get("db_user") or not cn_settings.get("hostname"):
			frappe.throw("Remote Server Details credentials required")

		conn = pymysql.connect(
			host=cn_settings.get("hostname"),
			user=cn_settings.get("db_user"), 
			password = cn_settings.get("password"),
			db=cn_settings.get("database_name"),
		)
		cond = get_condition(filters)
		query = """SELECT 
				calldate,
				src,
				dst,
				dcontext,
				channel,
				dstchannel,
				lastapp,
				lastdata,
				duration,
				billsec,
				disposition,
				amaflags,
				accountcode,
				uniqueid,
				userfield,
				IF(disposition = 'ANSWERED' and recordingfile > 1 ,CONCAT("<button type='button' style='height: 26px;margin-top: -4px;padding: 4px;' class='btn btn-primary ellipsis' onClick='play_audio(",CONCAT('"',recordingfile,'"'),")'>Play Audio</button>"),'') as recordingfile ,
				cnam,
				cnam,
				outbound_cnum,
				outbound_cnam,
				dst_cnam,
				linkedid,
				peeraccount,
				sequence
			FROM
				cdr
			WHERE {0}
			ORDER BY calldate desc
			LIMIT 100
   				""".format(cond)
    
		cur = conn.cursor()
		cur.execute(query)
		output = cur.fetchall()
		result = []
		for row in output:
			result.append(list(row))
		# To close the connection
		conn.close()
		return result
	except Exception as e:
		traceback = frappe.get_traceback()
		frappe.log_error(title="CDR",message=traceback)

def get_condition(filters):
	cond = " 1=1 "
	cs_default = frappe.get_single("Call Settings")
	for row in cs_default.get("settings"):
		cond += " and (outbound_cnam like %{0}% or dst like %{0}% or clid like %{0}% )".format(row.get("value"))
     
	if filters.get("did"):
		cond += " and (outbound_cnam like %{0}% or outbound_cnam like %{0}% or outbound_cnam like %{0}% )".format(filters.get("did"))

	print(cond)
	return " 1=1 "

@frappe.whitelist()
def get_file(file_name=""):
	import os
	import os.path
	if not file_name:
		return ""

	dyn_str = ""
	for sstr in file_name.split("-",):
		if sstr.startswith("202") and len(sstr) == 8:
			dt = frappe.utils.getdate(sstr)
			if dt:
				dyn_str = "{}/{}/{}/".format("{:02d}".format(dt.year,),"{:02d}".format(dt.month,),"{:02d}".format(dt.day,))

	print(file_name)
	print(dyn_str)
	print("==========================")
	cn_settings = frappe.get_single("Remote Server Details")
	filepath = "{}{}".format(cn_settings.get("current_server_file_path"),file_name)
	print('sshpass -p "{}" scp {}@{}:{} {}'.format(cn_settings.get("ssh_password"),cn_settings.get("ssh_username"),cn_settings.get("ssh_hostname"),cn_settings.get("server_file_path")+dyn_str+file_name,cn_settings.get("current_server_file_path")))
	if not os.path.isfile(filepath):
		try:
			os.system('sshpass -p "{}" scp {}@{}:{} {}'.format(cn_settings.get("ssh_password"),cn_settings.get("ssh_username"),cn_settings.get("ssh_hostname"),cn_settings.get("server_file_path")+dyn_str+file_name,cn_settings.get("current_server_file_path")))
			filepath = "/files/{}".format(file_name)
		except Exception as e:
			frappe.log_error(str(e))
			filepath = False;
	else:
		filepath = "/files/{}".format(file_name)

	return filepath