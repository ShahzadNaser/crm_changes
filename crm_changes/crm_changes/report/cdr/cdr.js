// Copyright (c) 2016, Shahzad Naser and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["CDR"] = {
	"filters": [
		{
			"fieldname":"date",
			"label": __("Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		}
	],
	after_datatable_render: function(datatable_obj) {
		$('.dt-cell').css("height","40px !important");
		$('.dt-row').css("height","40px !important");
	}
};


function play_audio(filepath){
	
	var d = new frappe.ui.Dialog({
		title: "Please wait audio is downloading..........",
		fields: [
			{fieldname: "field_html", fieldtype: "HTML", options:'<audio controls class="audio" src=""></audio>'}
		]
	});
	d.show();
	frappe.call({
		method: "crm_changes.crm_changes.report.cdr.cdr.get_file",
		args: {
			"file_name": filepath
		},
		callback: function(r){
			if(r.message){
				setTimeout(function(){ $('.audio').attr("src",r.message)},100);
			}else{
				frappe.msgprint(__("No File Found."));
			}
		}
	});
}