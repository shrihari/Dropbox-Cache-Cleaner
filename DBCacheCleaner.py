import wx
import thread
import time
import base64
import os.path
import platform


### DROPBOX CODE ###
if platform.system() == 'Windows':
	HOST_DB_PATH = os.path.expandvars(r'%APPDATA%\Dropbox\host.db')
else:
	HOST_DB_PATH = os.path.expanduser(r'~/.dropbox/host.db')

def read_dropbox_location():
	f = open(HOST_DB_PATH, "r")
	  
	try:
		ignore = f.readline()
		location_line = f.readline().strip()
		return base64.decodestring(location_line).decode('utf8')
	finally:
		f.close()
  
	raise Exception("Dropbox location not found")
### END DROPBOX CODE ###


CACHE_LIMIT = int()

def cache_clear():
	global CACHE_LIMIT

	db_cache_folder = os.path.join(read_dropbox_location(), ".dropbox.cache")
	
	while True:
		print CACHE_LIMIT
		time.sleep(60)
		total_size = 0
		for dirpath, dirnames, filenames in os.walk(db_cache_folder):
			for f in filenames:
				fp = os.path.join(dirpath, f)
				total_size += os.path.getsize(fp)

		if total_size > (CACHE_LIMIT * 1073741824):
			for the_file in os.listdir(db_cache_folder):
				file_path = os.path.join(db_cache_folder, the_file)
				try:
					os.unlink(file_path)
				except Exception, e:
					print e
		else:
			print "Not exceeded"

class MyTaskBarIcon(wx.TaskBarIcon):
	def __init__(self, frame):
		wx.TaskBarIcon.__init__(self)

		self.frame = frame
		self.SetIcon(wx.Icon('dbcc.png', wx.BITMAP_TYPE_PNG), 'Dropbox Cache Cleaner')
		self.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=1)
		self.Bind(wx.EVT_MENU, self.OnTaskBarDeactivate, id=2)
		self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=3)
		self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.OnTaskBarActivate)

	def CreatePopupMenu(self):
		menu = wx.Menu()
		menu.Append(1, 'Show')
		menu.Append(2, 'Hide')
		menu.Append(3, 'Close')
		return menu

	def OnTaskBarClose(self, event):
		self.frame.Close()

	def OnTaskBarActivate(self, event):
		if not self.frame.IsShown():
			self.frame.Show()
			self.frame.SetFocus()

	def OnTaskBarDeactivate(self, event):
		if self.frame.IsShown():
			self.frame.Hide()


class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(300, 130), style = wx.DEFAULT_FRAME_STYLE )#^ wx.RESIZE_BORDER )

		global CACHE_LIMIT
		
		self.tskic = MyTaskBarIcon(self)
		self.Centre()
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_ICONIZE, self.OnIconize)

		self.SetAutoLayout(1)
		self.SetBackgroundColour(wx.NullColour)
		
		if not os.path.exists('settings.ini'):
			print True
			f = open('settings.ini', 'w')
			f.write('10')
			f.close()

		f = open('settings.ini', 'r')
		CACHE_LIMIT = limit = int(f.read())
		print "--"+str(limit)
		print "---"+str(CACHE_LIMIT)
		f.close()

		box = wx.BoxSizer(wx.VERTICAL)
		box1 = wx.BoxSizer(wx.HORIZONTAL)
		box2 = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "Set cache limit (in GB): ")
		label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT,  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, ))
		box1.Add(label)
		
		self.sc = wx.SpinCtrl(self, -1)
		self.sc.SetRange(1, 10000)
		self.sc.SetValue(limit)
		box1.Add(self.sc)
		
		self.save = wx.Button(self, -1, 'Save')
		self.Bind(wx.EVT_BUTTON, self.OnSave, self.save)
		box2.Add(self.save, 1, wx.ALIGN_CENTER)

		box.Add(box1, 0, wx.ALIGN_CENTER | wx.ALL, 14)
		box.Add(box2, 0, wx.ALIGN_CENTER | wx.ALL, 8)
	
		self.SetSizer(box)
		self.Show()

		thread.start_new_thread(cache_clear, ())

	def OnSave(self, e):
		global CACHE_LIMIT
		CACHE_LIMIT = self.sc.GetValue()
		print CACHE_LIMIT
		f = open('settings.ini', 'w')
		f.write(str(CACHE_LIMIT))
		f.close()
		
	def OnExit(self, e):
		os._exit(1)
		
	def OnClose(self, event):
		self.tskic.Destroy()
		self.Destroy()
		
	def OnIconize(self, event):
		self.Iconize(False)
		self.Hide()
		
print read_dropbox_location()


class MyApp(wx.App):
	def OnInit(self):
		frame = MainWindow(None, 'Dropbox Cache Cleaner')
		frame.Show(True)
		self.SetTopWindow(frame)
		return True

app = MyApp(0)
try:
	app.MainLoop()
finally:
	del app

#app = wx.App(False)
#frame = MainWindow(None, "Dropbox Cache Cleaner")
#try:
#	app.MainLoop()
#finally:
#	del app
