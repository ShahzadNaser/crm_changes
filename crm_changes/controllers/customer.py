import frappe
from frappe.desk.doctype.tag.tag import add_tag

def before_save(doc, method):
    if doc.get("tags"):
        tags = doc.get("tags").split(",")
        print(doc.get("tags"))
        print(tags)
        for tag in tags:
            add_tag(tag.strip(), "Customer", doc.get("name"))
    doc.tags = ""