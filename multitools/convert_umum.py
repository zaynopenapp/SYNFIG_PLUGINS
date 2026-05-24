# Copyright (c) 2028 by ZAINAL AB <robert.mailcat@gmail.com>


import uuid
import xml.etree.ElementTree as ET
import copy
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import pkgutil

import numpy as np
import math

import varglo
from pathlib import Path
import zipfile	

gtk_ready = False

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    gtk_ready = True
except ModuleNotFoundError:
    print("GTK modul not found. please install GTK.")

if gtk_ready:
	settings = Gtk.Settings.get_default()
	settings.set_property("gtk-application-prefer-dark-theme", True) 

def cari_file():

	class MainWindow(Gtk.Window):
		Gtk.filepath = None

		def __init__(self):
			Gtk.Window.__init__(self, title="Pilih File")

			self.set_default_size(300, 50)
			button = Gtk.Button(label="Cari folder")
			button.connect("clicked", self.on_open_file)
			self.add(button)

		def on_open_file(self, widget):

			dialog = Gtk.FileChooserDialog(
			title="Pilih File",
			parent=self,
			action=Gtk.FileChooserAction.OPEN
			)

			dialog.add_buttons(
			Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OPEN, Gtk.ResponseType.OK
			)

			response = dialog.run()

			if response == Gtk.ResponseType.OK:
				Gtk.filepath = dialog.get_filename()
				Gtk.main_quit()

			dialog.destroy()


	win = MainWindow()
	win.connect("destroy", Gtk.main_quit)
	win.show_all()
	Gtk.main()

	return Gtk.filepath


def menu_plugin(pilihan_list):

	Gtk.pilihan = 0
	class RadioListBoxWindow(Gtk.Window):
		def __init__(self):
			Gtk.Window.__init__(self, title="Tools plugin")
			self.set_border_width(10)
			self.set_default_size(500, 150)

			main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
			self.add(main_vbox)

			main_bbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
			#self.add(main_bbox)

			# List untuk menyimpan RadioButton
			page1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
			page1.set_border_width(10)
			page1.pack_start(Gtk.Label(label="Select plugin"), False, False, 0)

			self.radio_buttons = []	

			scrolled_window = Gtk.ScrolledWindow()
			scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
			scrolled_window.set_min_content_height(200)
			# Buat ListBox
			self.listbox = Gtk.ListBox()
			self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
			#
			scrolled_window.add(self.listbox)
			page1.pack_start(scrolled_window, False, False, 0)
			main_vbox.pack_start(page1, False, False, 0)

			# Daftar pilihan radio
			#choices = ["Pilihan 1", "Pilihan 2", "Pilihan 3", "Pilihan 4", "Pilihan 4", "Pilihan 4", "Pilihan 4"]
			radio_group = None
			idx=0
			for choice in pilihan_list:
				row = Gtk.ListBoxRow()
				hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
				row.add(hbox)

				if radio_group is None:
				    radio_button = Gtk.RadioButton.new_with_label_from_widget(None, choice)
				    radio_group = radio_button
				else:
				    radio_button = Gtk.RadioButton.new_with_label_from_widget(radio_group, choice)

				radio_button.connect("toggled", self.on_radio_toggled)
				radio_button.idx = idx

				self.radio_buttons.append(radio_button)

				hbox.pack_start(radio_button, True, True, 0)
				self.listbox.add(row)

				idx +=1

			self.button = Gtk.Button(label="select Plugin")
			self.button.info = 0
			self.listbox.add(Gtk.ListBoxRow())
			self.button.connect("clicked", self.on_button_plih)
			main_bbox.pack_start(self.button , True, True, 2)
			
			self.buttonc = Gtk.Button(label="Cancel")
			
			self.buttonc.connect("clicked", self.on_button_cancel)
			main_bbox.pack_end(self.buttonc , False, False, 0)

			main_vbox.pack_start(main_bbox , False, False, 0)
			self.show_all()

		def on_button_cancel(self, button):
			Gtk.pilihan = -1
			Gtk.main_quit()

		def on_button_plih(self, button):
			#global pilihan
			#ilihan = button.info
			Gtk.pilihan = button.info
			Gtk.main_quit()

		def on_radio_toggled(self, radio_button):
			if radio_button.get_active():
				label = radio_button.get_label()
				self.button.set_label(f"Run plugin {label}")
				self.button.info = radio_button.idx

	win = RadioListBoxWindow()
	win.connect("destroy", Gtk.main_quit)
	Gtk.main()

	return Gtk.pilihan
	
def get_position(r, angle_deg):

    angle_rad = math.radians(angle_deg)  # konversi derajat ke radian
    x = r * math.cos(angle_rad)
    y = r * math.sin(angle_rad)
    return x, y

def caripos(el_bone_p):

	el_r = el_bone_p.find(".//scalelx/")
	r = float(el_r.get('value'))
	el_angle = el_bone_p.find(".//angle/")
	angle = float(el_angle.get('value'))

	return get_position(r,angle)


def rotate_point_np(point, angle_deg, center=(0, 0)):
    angle_rad = np.radians(angle_deg)
    rot_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad),  np.cos(angle_rad)]
    ])
    shifted_point = np.array(point) - np.array(center)
    rotated_point = rot_matrix @ shifted_point + np.array(center)
    return rotated_point


def save_print_log(list_text):
	with open("log.dat", "w") as file:
		file.write("info !\n")
		for text in list_text:
			file.write(text+"\n")

		file.write("\n")
		#file.write("please close this info first !"+"\n")

def replace(parent, el_new):
	parent.remove(parent[0])
	parent.append(el_new)

def hapus_kode(el_kode):
	el_string = el_kode[0][0][0] # hapus grey code
	replace(el_kode,el_string)

def load_template(kunci_tag,main_template):

	el_temp = main_template.find(kunci_tag)
	return copy.deepcopy(el_temp)

def timemap(main_template): # timemap new param

	el_jump = load_template(".//*[@kunci='CU_jump']",main_template)
	el_imp = load_template(".//*[@kunci='CU_influence']",main_template)

	for el_timemap in  varglo.root_file.findall(".//timemap"):
		el_c = copy.deepcopy(el_jump)
		el_timemap.append(el_c[0])
		el_imp = copy.deepcopy(el_imp)
		el_timemap.append(el_imp[0])

def set_bone_with():

	def convert_file(root_file,main_template,template_filename):
		el_bones = root_file.find(".//bones")

		el_shape = load_template(".//*[@kunci='BONE_shape']",main_template)
		if el_bones != None:
			for el_bonelist in el_bones.findall(".//bone"):
				el_width = el_bonelist.find(".//width/")

				if el_width.tag == 'real':
					el_width.set('value','0.066666666666667')
				el_twidth = el_bonelist.find(".//tipwidth/")

				if el_twidth.tag == 'real':
					el_twidth.set('value','0.066666666666667')

		hasil = template_filename			

		if template_filename == None:
			hasil = sys.argv[1]

		el_tree = ET.ElementTree(root_file)
		with open(hasil, "wb") as filesnew:
			el_tree.write(filesnew)

		print(" set width, tipwidth done")

	template_file = os.path.join(os.path.dirname(sys.argv[0]), 'template.xml')
	tree_convert = ET.parse(template_file)
	main_template = tree_convert.getroot()

	onsynfig = len(sys.argv)

	if onsynfig == 1:
		template_filename = cari_file()
		if template_filename !=None:
			namafile = Path(template_filename).name
			p = len(namafile)
			nama = namafile[:p-4]
			folder = os.path.dirname(template_filename)
			tree_convert = ET.parse(template_filename)
			root_file = tree_convert.getroot()

			convert_file(root_file,main_template,template_filename)
		else: 
			print("cancel")

	else:
		print("internal synfig")

		root_file = ET.parse(sys.argv[1]).getroot()

		convert_file(root_file,main_template,None)

def bone_ikangleconvertdata(main_template):

	el_bones = varglo.root_file.find(".//bones")

	el_shape = load_template(".//*[@kunci='BONE_shape']",main_template)
	if el_bones != None:
		for el_bonelist in el_bones.findall(".//joint_bone/"):
			el_bonelist.tag='integer'
			el_bonelist.set('value','1')
		
		for el_bonelist in el_bones.findall(".//t_bone/"):
			el_bonelist.tag='integer'
			el_bonelist.set('value','1')

def convert_tobonedeformation(main_template):

	list_parent = {}
	list_bone = []
	el_bones = varglo.root_file.find(".//bones")
	el_rootbone = el_bones.find(".//bone_root")
	guid_root = el_rootbone.get('guid')

	el_skeleton = varglo.root_file.find(".//*[@group='convert']")
	#print(el_skeleton.attrib)

	if el_skeleton != None:
		#ganti attributnya
		el_skeleton.set('type','skeleton_deformation')
		el_skeleton.set('version','0.2')
		el_skeleton.attrib.pop('group')
		el_name = el_skeleton.find(".//*[@name='name']")
		el_skeleton.remove(el_name)

		el_param = load_template(".//*[@kunci='BONE_deformation_param']",main_template)

		for el_this in el_param.findall(".//param"):
			el_skeleton.append(el_this)

		el_entrybaru = load_template(".//*[@kunci='BONE_deformation']",main_template)

		el_static_list = el_skeleton.find(".//static_list")
		el_static_list.set('type','pair_bone_object_bone_object')

		for el_entry in el_static_list.findall(".//entry"):
			el_entry_awal = copy.deepcopy(el_entry[0])
			guid_awal = el_entry_awal.get('guid')
			el_entry_def = copy.deepcopy(el_entrybaru)
			el_second = el_entry_def.find(".//second")
			replace(el_second,el_entry_awal)

			guid_baru = str(uuid.uuid4())
			if guid_awal in list_parent: # jika ada di kamus gunakan guid parent baru dari kamus
				guid_baru = list_parent[guid_awal]

			else:# jika tidak ada gunakan guid baru dan masukan ke kamus guid baru
				list_parent[guid_awal]=guid_baru

			el_first = el_entry_def.find(".//first")
			el_first[0].set('guid',guid_baru)

			replace(el_entry,el_entry_def[0]) #ganti entry menjadi enry deformasi

			for elbone in el_bones.findall(".//bone"):
				if guid_awal == elbone.get('guid'):
					bone_copy = copy.deepcopy(elbone)
					bone_copy.set('guid',guid_baru)

					nama_el = bone_copy.find(".//name/")
					el_nn = nama_el.text
					nama_el.text = el_nn+" #"

					el_parent =bone_copy.find(".//bone_valuenode")
					el_parent_guid = el_parent.get('guid')

					if guid_root == el_parent_guid: #sementara semua ke root/ tanpa parent
						
						el_bone_depth = bone_copy.find(".//bone_depth")
						if el_bone_depth[0].tag == 'vectorlength':# jika ada kode khusus maka artinya dia memiliki prent khusus
							el_p = el_bone_depth.find(".//bone_valuenode")
							guid_p = el_p.get('guid')
							if guid_p in list_parent:
								el_parent.set('guid',list_parent[guid_p])
							else:
								guid_baru = str(uuid.uuid4())
								list_parent[guid_p]=guid_baru
								el_parent.set('guid',guid_baru)
						

					else: # jika parent ke bone lain/ memiliki parent
						if el_parent_guid in list_parent: # jika ada di kamus
							el_parent.set('guid',list_parent[el_parent_guid])

						else:
							guid_baru = str(uuid.uuid4())
							list_parent[el_parent_guid]=guid_baru
							el_parent.set('guid',guid_baru)

					for el_berguid in bone_copy.findall(".//*[@guid]/.."):

						if el_berguid[0].tag != 'bone_valuenode':
							if el_berguid.tag != 'scalelx':
								el_berguid[0].attrib.pop('guid',None)

						#else:
							#if el_berguid.get('guid')!=guid_root:
								#el_berguid.attrib.pop('guid')

					#el_bones.append(bone_copy)
					list_bone.append(bone_copy)

	list_bone.reverse()
	for bone in list_bone:
		el_bones.append(bone)

def masukan_bone_baru(list_new_el_bone_baru):

	bones = varglo.root_file.find(".//bones")
	for new_bone in list_new_el_bone_baru:
		bones.append(list_new_el_bone_baru[new_bone])

def cari_bone(guid_this):

	bones = varglo.root_file.find(".//bones")
	root_bone = varglo.root_file.find(".//bone_root")
	guit_rootbone = root_bone.get('guid')

	for bone in bones.findall(".//bone"):
		guid_bone = bone.get('guid')
		if guid_this == guid_bone:
			return bone

	return None

def ganti_guidnya(el):

	def umum(el_berguid):
		print(">>> tag umum : ",el_berguid.tag)
		guid_apa = el_berguid.get('guid')

		if guid_apa in varglo.list_guid_umum:
			guid_b = varglo.list_guid_umum[guid_apa]
			el_berguid.set('guid',guid_b)

		else:
			guid_baru = str(uuid.uuid4())
			varglo.list_guid_umum[guid_apa]=guid_baru
			el_berguid.set('guid',guid_baru)


	for el_berguid in el.findall(".//*[@guid]"):

		if 'type' in el_berguid.attrib:
			if el_berguid.get('type')=='bone_object':# +++
			#if el_berguid.tag == 'bone_valuenode':# khusus berguid bone
				print(">>> tag bone : ",el_berguid.tag)
				guid_apa = el_berguid.get('guid')
				if guid_apa != varglo.root_bone_guid : # abaikan jika guid itu sebuah root guid
					if guid_apa in varglo.list_new_bone:
						bone_cari = varglo.list_new_bone[guid_apa]
						guidnya = bone_cari.get('guid')
						el_berguid.set('guid',guidnya)

			else:
				umum(el_berguid)
			
		else:
			umum(el_berguid)
			
def buat_bone_baru(copy_group):

	bones = varglo.root_file.find(".//bones")
	root_bone = varglo.root_file.find(".//bone_root")
	guit_rootbone = root_bone.get('guid')
	varglo.root_bone_guid = guit_rootbone

	for sk in copy_group.findall(".//*[@type='skeleton']"):
		for bone in sk.findall(".//bone"):
			guid_bone = bone.get('guid')
			bone_asli = bones.find(".//*/[@guid='{no}']".format(no= guid_bone))

			bone_copy = copy.deepcopy(bone_asli)
			guid_asli = bone_copy.get('guid')

			if not guid_asli in varglo.list_new_bone:
				guid_baru = str(uuid.uuid4())
				bone_copy.set('guid',guid_baru)
				varglo.list_new_bone[guid_asli]=bone_copy
	#ganti semua guid masing2 bone dan simpan guid barunya
	for newbone in varglo.list_new_bone:
		bone = varglo.list_new_bone[newbone]
		ganti_guidnya(bone)
		
def masukan_bonebaru():

	print('++ masukan bone done')
	bones = varglo.root_file.find(".//bones")

	list_bone = []
	for newbone in varglo.list_new_bone:
		bone = varglo.list_new_bone[newbone]
		list_bone.append(bone)

	list_bone.reverse()
	for bone in list_bone:
		bones.append(bone)

def duplicate_shapekey():

	print('[.] searching group')

	list_new_el_bone = []
	ditemukan = False
	copy_group = None
	list_new_el_bone_baru = {}
	for group in varglo.root_file.findall(".//*[@type='group']"):
		if 'desc' in group.attrib:
			if '>copy' in group.get('desc'):
				ditemukan = True
				group.set('desc','group')
				copy_group = copy.deepcopy(group)
				copy_group.set('desc','group_copy')

				#create bone baru
				buat_bone_baru(copy_group)
				ganti_guidnya(copy_group)
				

	if ditemukan:
		masukan_bonebaru()
		varglo.root_file.append(copy_group)

	else:
		print('!!! mising code >copy in group your data shapekey')
		print('!!! please make group shapekey for temporary and set new description with add code ">copy"')

	# tree_copy = ET.ElementTree(copy_group)
	# tree_copy.write('/home/mint/Documents/'+'duplicate_shapekey.sif')

def convert_key_tolinear():

	for wp in varglo.root_file.findall(".//waypoint"):
		if wp.get('before') !='linear':
			wp.set('before','linear')

		if wp.get('after') !='linear':
			wp.set('after','linear')

def repeat_convert(main_template):

	print('[.] cari id')

	el_defs = varglo.root_file.find('.//defs')

	for el_id in el_defs.findall(".//*[@id]"):
		nama_id = el_id.get('id')
		guidnya = None
		if 'repeat' in nama_id:
			tipenya = el_id.get('type')

			if 'guid' in el_id.attrib:
				guidnya = el_id.get('guid')

			el_id.attrib.pop('guid')
			el_id.attrib.pop('id')

			el_TIMELOOP = load_template(".//*[@kunci='GANTI_TIMELOOP']",main_template)
			for el_tipe in el_TIMELOOP.findall(".//*[@type='TIPE']"):
				el_tipe.set('type',tipenya)
				if guidnya != None:
					el_tipe.set('guid',guidnya)
				
			time_akhir='none'
			for wp in el_id.findall('.//waypoint'):
				time_akhir = wp.get('time')

			if time_akhir !='none':
				el_waktu = el_TIMELOOP.find(".//*[@value='WAKTU']")
				el_waktu.set('value',time_akhir)

			el_link = el_TIMELOOP.find(".//link")
			el_id_copy = copy.deepcopy(el_id)

			replace(el_link,el_id_copy)
			el_defs.remove(el_id)

			for el_berid in varglo.root_file.findall(".//*[@use]"):
				if nama_id == el_berid.get('use'):
					el_berid.attrib.pop('use')
					el_berid.append(el_TIMELOOP[0])

def del_erasepointsamepos(el_bline):

	last_point_x = 0
	last_point_y = 0
	first = True
	entrys =  el_bline.findall(".//entry")
	last_entry = None

	for entry in entrys:
		point = entry.find('.//point/')

		if point.tag != 'vector':
			continue

		if first:
			last_point_x = round(float(point[0].text),3)
			last_point_y = round(float(point[1].text),3)
			last_entry = entry
			first = False
			continue
		
		last_point_x_cur = round(float(point[0].text),3)
		last_point_y_cur = round(float(point[1].text),3)

		if last_point_x_cur == last_point_x:
			if last_point_y_cur == last_point_y:
				el_bline[0].remove(last_entry)
				print("found double point")

		last_point_x = last_point_x_cur
		last_point_y = last_point_y_cur
		last_entry = entry

def double_point():

	print('>>> del double_point')

	root_file,template_filename = find_file()

	if not root_file == None:

		for el_bline in root_file.findall(".//*[@name='bline']"):
			del_erasepointsamepos(el_bline)

		save_file(template_filename,root_file)
		print('Done')

	else:
		print(" cancel")


def non_sharpline(root_file):

	for el_outline in root_file.findall(".//*[@type='outline']"):
		el_round1 = el_outline.find(".//*[@name='round_tip[0]']/")
		el_round1.set('value', 'true')

		el_round2 = el_outline.find(".//*[@name='round_tip[1]']/")
		el_round2.set('value', 'true')

	print(" >>> round_tip outline set true")


def split_bline():

	print('>>> convert split bline process')

	root_file,template_filename = find_file()

	non_sharpline(root_file)

	if not root_file == None:

		for el_bline in root_file.findall(".//*[@name='bline']"):
			del_erasepointsamepos(el_bline)

			for el_this in el_bline.findall('.//split/'):
				if el_this.tag == 'bool':
					el_this.set('value','false')

			for el_this in el_bline.findall('.//split_radius/'):
				if el_this.tag == 'bool':
					el_this.set('value','true')

			for el_this in el_bline.findall('.//split_angle/'):
				if el_this.tag == 'bool':
					el_this.set('value','false')

		save_file(template_filename,root_file)
		print('Done')

	else:
		print(" cancel")

def add_display(root_file):

	total_add = 0
	for el_sk in root_file.findall(".//bones/bone") :
		el_display = el_sk.find(".//display")

		if el_display == None:
			a = ET.Element('display')
			b = ET.SubElement(a, 'integer')
			b.set('value','2')
			el_sk.append(a)

			total_add +=1
		else:
			print(" Element display sudah ada")

	if total_add >0:
		print("ditemukan [ "+str(total_add)+"] bones, add el_display done")

	else:
		print("tidak ada layers bone")

def find_file():

	onsynfig = len(sys.argv)
	root_file = None
	
	if onsynfig >= 1:
		root_file = None
		template_filename = None

		if onsynfig == 1:
			template_filename = cari_file()
			if template_filename !=None:
				namafile = Path(template_filename).name
				p = len(namafile)
				nama = namafile[:p-4]
				folder = os.path.dirname(template_filename)
					#with zip_ref.open("content.sif") as file_xml:
				tree_convert = ET.parse(template_filename)
				root_file = tree_convert.getroot()
				return root_file,template_filename

			else:
				return None, None

		else:
			root_file = ET.parse(sys.argv[1]).getroot()
			return root_file,template_filename
	else:
		return None, None

def cari_center_allbline(blines):

	xs = []
	ys = []

	for bline in blines:
	    el_vec = bline.find('.//vector')

	    xs.append(float(el_vec.find('x').text))
	    ys.append(float(el_vec.find('y').text))

	mid_pos_x = (max(xs) + min(xs)) / 2
	mid_pos_y = (max(ys) + min(ys)) / 2

	return mid_pos_x,mid_pos_y

def scale_bline():

	root_file,template_filename = find_file()

	if not root_file == None:

		faktor_x = None
		faktor_y = 0
		done = False
		el_kode = root_file.find('.//greyed/link/vector/../../..')

		if el_kode != None:
			el_vec = el_kode.find('.//vector')

			if el_vec[0].tag == 'x':
				faktor_x = float(el_vec[0].text)
				faktor_y = float(el_vec[1].text)

			el_vec_new = copy.deepcopy(el_vec)
			replace(el_kode,el_vec)

		onlygroup = root_file.find(".//*[@group='greyed']")

		if onlygroup != None:
			print("... found set layer")
			onlygroup.attrib.pop('group')
			
			blines = onlygroup.findall(".//*[@name='bline']")

			faktor_x,faktor_y = cari_center_allbline(blines)

			for bline in blines:
				if faktor_x == None:
					el_vec = bline.find('.//vector')
					if el_vec[0].tag == 'x':
						faktor_x = float(el_vec[0].text)
						faktor_y = float(el_vec[1].text)

				for vectors in bline.findall(".//vector"):
					
					if vectors[0].tag == 'x':
						vec_x = float(vectors[0].text)
						vec_y = float(vectors[1].text)

						vec_x_new = ((vec_x - faktor_x)*2)+faktor_x
						vec_y_new = ((vec_y - faktor_y)*2)+faktor_y

						vectors[0].text = str(vec_x_new)
						vectors[1].text = str(vec_y_new)

				for radius in bline.findall(".//radius"):
					if radius[0].tag == 'real':
						val = radius[0].get('value')
						val_new = float(val)*2
						radius[0].set('value', str(val_new))

			save_file(template_filename,root_file)

			print("...done")

		else:
			print("!!! code [greyed] not found")
			print("[help] please set layer with name 'greyed'")

	else:
		print("...cancel")


def mirror_bline():

	root_file ,template_filename = find_file()

	if not root_file == None:
		layers = root_file.findall(".//*[@group='mirror']") # set layer with name 'mirror'
		
		if len(layers)== 0:
			print(" !!! set layer with name 'mirror' not found")

		for bl in layers:
			bline = bl.find(".//*[@name='bline']")

			if bline is None:
				print("no bline")
				continue

			mirrored_entries = []

			for entry in bline.findall(".//entry"):
				entry_c = copy.deepcopy(entry) # copy element

		        # mirror vector x
				vec = entry_c.find(".//point/vector")
				if vec != None:
					vec[0].text = str(float(vec[0].text) * -1)

		        # mirror theta angle
				angle = entry_c.find(".//theta/angle")
				if angle != None:
					angle.set("value", str(float(angle.get("value")) * -1))

				mirrored_entries.append(entry_c)

			for entry in reversed(mirrored_entries): # reverse list entry
				entry[0].attrib.pop("guid", None)
				bline[0].append(entry)

		save_file(template_filename,root_file)

		print(" mirror bline done")

	else:
		print(" cancel")

def blend_onto():

	root_file ,template_filename = find_file()

	if not root_file == None:
		layers = root_file.findall(".//*[@desc='clip']")

		if len(layers)== 0:
			print(" !!! not found layer name code 'clip'")

		for layer_this in layers:
			layer_this.attrib.set('desc','cl')
			param = layer_this.find(".//*[@name='blend_method']/")
			param.set('value','13')

		save_file(template_filename,root_file)

		print(" make clip blende done")

	else:
		print(" cancel")

def save_file(template_filename,root_file):

	if template_filename == None:
		hasil = sys.argv[1]

	else:
		hasil = template_filename	

	el_tree = ET.ElementTree(root_file)
	with open(hasil, "wb") as filesnew:
		el_tree.write(filesnew)

def set_center_bline():

	print(" please set layer with name code 'greyed'")

	root_file ,template_filename = find_file()

	if not root_file == None:
		faktor_x = None
		faktor_y = 0
		done = False
		el_kode = root_file.find('.//greyed/link/vector/../../..')

		if el_kode != None:
			el_vec = el_kode.find('.//vector')

			if el_vec[0].tag == 'x':
				faktor_x = float(el_vec[0].text)
				faktor_y = float(el_vec[1].text)

			el_vec_new = copy.deepcopy(el_vec)
			replace(el_kode,el_vec)

		onlygroup = root_file.find(".//*[@group='greyed']")

		if onlygroup != None:

			print("... found set layer")
			onlygroup.attrib.pop('group')

			blines = onlygroup.findall(".//*[@name='bline']")
			faktor_x,faktor_y = cari_center_allbline(blines)

			for bline in blines:
				if faktor_x == None:
					el_vec = bline.find('.//vector')
					if el_vec[0].tag == 'x':
						faktor_x = float(el_vec[0].text)
						faktor_y = float(el_vec[1].text)

				for vectors in bline.findall(".//vector"):
					if vectors[0].tag == 'x':
						vec_x = float(vectors[0].text)
						vec_y = float(vectors[1].text)

						vec_x_new = vec_x - faktor_x
						vec_y_new = vec_y - faktor_y

						vectors[0].text = str(vec_x_new)
						vectors[1].text = str(vec_y_new)

			save_file(template_filename,root_file)
			
			print("... done")

		else:
			print(" not set layer code [greyed]")
			print(" help: please select layer and set to name is 'greyed'")
	else:
		print(" cancel")

def buka_file():

	template_filename = cari_file()
	if template_filename !=None:
		namafile = Path(template_filename).name
		p = len(namafile)
		nama = namafile[:p-4]
		folder = os.path.dirname(template_filename)
		print(folder)
			#with zip_ref.open("content.sif") as file_xml:
		tree_convert = ET.parse(template_filename)
		varglo.root_file = tree_convert.getroot()

		add_display(varglo.root_file)

		ET.indent(varglo.root_file)
		tree_copy = ET.ElementTree(varglo.root_file)
		tree_copy.write(folder+'/'+nama+'_converted'+'.sif')

	else:
		print("   >>> convert to add display param cancel")

def create_list():

	plugin_namelist = []
	plugin_namelist.append('add_display_param')
	plugin_namelist.append('split_bline')
	plugin_namelist.append('set_bone_with')
	plugin_namelist.append('center_bline')
	plugin_namelist.append('scale_bline_2x')
	plugin_namelist.append('clip_bline')
	plugin_namelist.append('mirror_bline')
	plugin_namelist.append('del_double_pointbline')


	return plugin_namelist

def process():
	print("")
	print(">>>>>>>> processing <<<<<<<<")

	list_plugin = create_list()
	choice = menu_plugin(list_plugin)

	if choice >= 0:
		match list_plugin[choice]:
			case 'add_display_param':
				buka_file()

			case 'split_bline':
				split_bline()

			case 'set_bone_with':
				set_bone_with()

			case 'center_bline':
				set_center_bline()

			case 'scale_bline_2x':
				scale_bline()

			case 'clip_bline':
				blend_onto()

			case 'mirror_bline':
				mirror_bline()

			case 'del_double_pointbline':
				double_point()

	else:
		print(" cancel multi plugins")


	
	
	#ada = timemap(root_file,main_template) # timemap new param

	
	#bone_ikangleconvertdata(root_file,main_template)
	#convert_tobonedeformation(root_file,main_template)
	#duplicate_shapekey()
	#convert_key_tolinear()
	#repeat_convert(main_template)
	#split_bline(main_template)
	#add_display(varglo.root_file)

	#tree_copy = ET.ElementTree(varglo.root_file)
	#tree_copy.write(path+namafile+'_converted.sif')
	#tree_copy.write('/home/mint/.config/synfig/plugins/convertumum/'+namafile+'_new.sif')

	print(">>>>>>>> processing Done <<<<<<<<")
	
def main():

	onsynfig = len(sys.argv)
	if onsynfig >= 1:
		process()

		#namafile = "uji.sif"
		#template_filename = os.path.join(os.path.dirname(sys.argv[0]), namafile)
		

	# else:
	# 	namafile =""
	# 	if len(sys.argv) < 2:
	# 		pass
	# 	else:
	# 		namafile = os.path.basename(sys.argv[1])

	# 	folder = os.path.dirname(template_filename)
	# 	varglo.root_file = ET.parse(sys.argv[1]).getroot()
	# 	jalankan(namafile,folder+'/')

	# 	writeTo = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
	# 	with open(writeTo, "wb") as files:
	# 		files.write(ET.tostring(varglo.root_file, encoding="utf-8", xml_declaration=True))

if __name__ == "__main__":
	main()