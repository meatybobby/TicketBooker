import requests
import lxml.html
import random
import datetime
import PIL.Image
import PIL.ImageTk
import urllib.parse
import json
import os
import captcha
import threading
from tkinter import *
from tkinter import messagebox
class TicketBooker(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.grid()
		self.createOption()
		self.createWidgets()
		self.cls = captcha.CaptchaDecoder()
		self.bAuto = False
		self.sAuto = False
		if not os.path.exists("record"):
			os.mkdir("record")

	def createWidgets(self):
		self.pidText = Label(self)
		self.pidText["text"] = "Person id:"
		self.pidText.grid(row=0, column=0)
		self.pidField = Entry(self)
		self.pidField["width"] = 15
		self.pidField.grid(row=0, column=1, columnspan=1)
		
		self.fromText = Label(self)
		self.fromText["text"] = "From station:"
		self.fromText.grid(row=1, column=0)
		self.fromField = Entry(self)
		self.fromField["width"] = 10
		self.fromField.grid(row=1, column=1, columnspan=1)
		
		self.toText = Label(self)
		self.toText["text"] = "To station:"
		self.toText.grid(row=2, column=0)
		self.toField = Entry(self)
		self.toField["width"] = 10
		self.toField.grid(row=2, column=1, columnspan=1)
		
		self.dateText = Label(self)
		self.dateText["text"] = "Date(YYYY/MM/DD):"
		self.dateText.grid(row=0, column=2)
		self.dateField = Entry(self)
		self.dateField["width"] = 15
		self.dateField.grid(row=0, column=3, columnspan=1)
		
		self.sTimeText = Label(self)
		self.sTimeText["text"] = "Start time:"
		self.sTimeText.grid(row=1, column=2)
		self.sVar = StringVar(self)
		self.sVar.set(self.option[9])
		self.sTimeMenu = OptionMenu(self,self.sVar,*self.option)
		self.sTimeMenu.grid(row=1, column=3, columnspan=1)
		
		self.eTimeText = Label(self)
		self.eTimeText["text"] = "End time:"
		self.eTimeText.grid(row=2, column=2)
		self.eVar = StringVar(self)
		self.eVar.set(self.option[17])
		self.eTimeMenu = OptionMenu(self,self.eVar,*self.option)
		self.eTimeMenu.grid(row=2, column=3, columnspan=1)
		
		self.typeText = Label(self)
		self.typeText["text"] = "Type:"
		self.typeText.grid(row=3, column=0)
		self.tVar = StringVar(self)
		self.tVar.set(self.typeOption[0])
		self.typeMenu = OptionMenu(self,self.tVar,*self.typeOption)
		self.typeMenu.grid(row=3, column=1, columnspan=1)
		
		self.numText = Label(self)
		self.numText["text"] = "Number(1~6):"
		self.numText.grid(row=3, column=2)
		self.numField = Entry(self)
		self.numField["width"] = 10
		self.numField.grid(row=3, column=3, columnspan=1)
		
		self.autoVar = IntVar()
		autoBox = Checkbutton(self, text='Auto', variable=self.autoVar)
		autoBox.grid(row=4, column=0)
		
		self.search = Button(self)
		self.search["text"] = "Search"
		self.search.grid(row=4, column=1)
		self.search["command"] = self.searchTicket
		
		self.book = Button(self)
		self.book["text"] = "BookFromType"
		self.book.grid(row=4, column=2)
		self.book["command"] = self.bookFromType
		
		self.save = Button(self)
		self.save["text"] = "SaveInfo"
		self.save.grid(row=5, column=2)
		self.save["command"] = self.saveInfo
		
		self.load = Button(self)
		self.load["text"] = "LoadInfo"
		self.load.grid(row=5, column=3)
		self.load["command"] = self.loadInfo
		
	def createOption(self):
		self.option=[]
		for i in range(0,24,1):
			if i < 10:
				self.option.append('0'+str(i)+':00')
			else:
				self.option.append(str(i)+':00')
		self.option.append('23:59')
		self.typeOption=['*1','*2','*3','*4']
		
		now = datetime.datetime.now()

		
	def searchTicket(self):
		if self.bAuto:
			messagebox.showinfo('Error',"Another job is running")
		elif self.sAuto:
			self.sAuto = False
			self.search['text'] = 'Search'
		elif self.autoVar.get():
			self.sAuto = True
			self.search['text'] = 'Stop search'
			self.searchThread = threading.Thread(target=self.autoSearch)
			self.searchThread.start()
		else:
			self.bookType = 'search'
			self.actionTicket()
		
	def bookFromType(self):
		if self.sAuto:
			messagebox.showinfo('Error',"Another job is running")
		elif self.bAuto:
			self.bAuto = False
			self.book['text'] = 'BookFromType'
		elif self.autoVar.get():
			self.bAuto = True
			self.book['text'] = 'Stop book'
			self.bookThread = threading.Thread(target=self.autoBookFromType)
			self.bookThread.start()
		else:
			self.bookType = 'from'
			self.actionTicket()
		
	def saveInfo(self):
		if os.path.exists("./info.sav"):
			var = messagebox.askyesno("Warning","Save file exist, override it?")
		if var:
			self.setData()
			dataStr = json.dumps(self.data)
			with open('info.sav','w') as f:
				f.write(dataStr)
			messagebox.showinfo("Success", "Save information!")
		
	def loadInfo(self):
		if os.path.exists("./info.sav"):
			with open('info.sav','r') as f:
				dataStr = f.read()
			self.data = json.loads(dataStr)
			self.pidField.delete(0,END)
			self.pidField.insert(0,self.data['person_id'])
			self.fromField.delete(0,END)
			self.fromField.insert(0,self.data['from_station'])
			self.toField.delete(0,END)
			self.toField.insert(0,self.data['to_station'])
			self.dateField.delete(0,END)
			self.dateField.insert(0,self.data["getin_date"])
			self.tVar.set(self.data["train_type"])
			self.sVar.set(self.data["getin_start_dtime"])
			self.eVar.set(self.data["getin_end_dtime"])
			self.numField.delete(0,END)
			self.numField.insert(0,self.data["order_qty_str"])
		else:
			messagebox.showinfo("Error", "Not find save file")
			
	def autoSearch(self):
		self.setData()
		url = "http://railway1.hinet.net/check_csearch.jsp"
		url2 = "http://railway1.hinet.net/wait_order_search.jsp"
		self.sess = requests.Session()
		headers1 = {"Origin":"http://railway1.hinet.net","Referer":"http://railway1.hinet.net/csearch.htm"}
		headers2 = {"Referer":url}
		while self.sAuto:
			num = random.random()
			image_url = "http://railway1.hinet.net/ImageOut.jsp?pageRandom="+str(num)
			self.sess.post(url,data=self.data,headers=headers1)
			cookie = requests.utils.dict_from_cookiejar(self.sess.cookies)
			image = self.sess.get(image_url,cookies=cookie,headers=headers2)
			now = datetime.datetime.now()
			imgPath = "IMG" + now.strftime('%Y%m%d%H%M%S') + ".jpg"
			with open(imgPath,"wb") as f:
				f.write(image.content)
			self.data['randInput'] = self.cls.identify(imgPath)
			os.remove(imgPath)
			cookie = requests.utils.dict_from_cookiejar(self.sess.cookies)
			res = self.sess.get(url2,cookies=cookie, headers=headers2,params=self.data)
			binary = res.content
			document = lxml.html.document_fromstring(binary)
			numTag = document.xpath('/html/body/table[2]/tr/td/a')
			del self.data['randInput']
			if numTag:
				self.sAuto = False
				self.search['text'] = 'Search'
		self.referUrl = res.url
		self.disPlaySearch(document)
		
	def autoBookFromType(self):
		url = "http://railway.hinet.net/check_ctkind1.jsp"
		url2 = "http://railway.hinet.net/order_kind1.jsp"
		self.sess = requests.Session()
		headers1 = {"Origin":"http://railway.hinet.net","Referer":"http://railway.hinet.net/ctkind1.htm"}
		headers2 = {"Referer":url}
		while self.bAuto:
			num = random.random()
			image_url = "http://railway.hinet.net/ImageOut.jsp?pageRandom="+str(num)
			self.sess.post(url,data=self.data,headers=headers1)
			cookie = requests.utils.dict_from_cookiejar(self.sess.cookies)
			image = self.sess.get(image_url,cookies=cookie,headers=headers2)
			now = datetime.datetime.now()
			imgPath = "IMG" + now.strftime('%Y%m%d%H%M%S') + ".jpg"
			with open(imgPath,"wb") as f:
				f.write(image.content)
			self.data['randInput'] = self.cls.identify(imgPath)
			os.remove(imgPath)
			cookie = requests.utils.dict_from_cookiejar(self.sess.cookies)
			res = self.sess.get(url2,cookies=cookie, headers=headers2,params=self.data)
			binary = res.content
			document = lxml.html.document_fromstring(binary)
			del self.data['randInput']
			timeTag = document.xpath('/html/body/p[5]/span[2]')
			if timeTag:
				self.bAuto = False
				self.book["text"] = "BookFromType"
		codeTag = document.xpath('//*[@id="spanOrderCode"]')
		now = datetime.datetime.now()
		filePath = "record/success" + now.strftime('%Y%m%d%H%M%S') + ".html"
		with open(filePath,"wb") as f:
			f.write(res.content)
		messagebox.showinfo("Success", "Success\nLeave time is\n"+timeTag[0].text
			+"\nCode: "+codeTag[0].text)
	
	def actionTicket(self):
		num = random.random()
		if self.bookType == 'search':
			url = "http://railway1.hinet.net/check_csearch.jsp"
			self.headers = {"Origin":"http://railway1.hinet.net","Referer":"http://railway1.hinet.net/csearch.htm"}
			image_url = "http://railway1.hinet.net/ImageOut.jsp?pageRandom="+str(num)
		else:
			url = "http://railway.hinet.net/check_ctkind1.jsp"
			self.headers = {"Origin":"http://railway.hinet.net","Referer":"http://railway.hinet.net/ctkind1.htm"}
			image_url = "http://railway.hinet.net/ImageOut.jsp?pageRandom="+str(num)
		self.setData()
		self.sess = requests.Session()
		self.sess.post(url,data=self.data,headers=self.headers)
		self.headers={"Referer":url}
		cookie = requests.utils.dict_from_cookiejar(self.sess.cookies)
		image = self.sess.get(image_url,cookies=cookie,headers=self.headers)
		now = datetime.datetime.now()
		imgPath = "IMG" + now.strftime('%Y%m%d%H%M%S') + ".jpg"
		with open(imgPath,"wb") as f:
			f.write(image.content)
		self.createCaptchaWindow(imgPath)

	def setData(self):
		self.data = {"returnTicket":"0"}
		self.data["person_id"] = self.pidField.get()
		self.data["from_station"] = self.fromField.get()
		self.data["to_station"] = self.toField.get()
		self.data["getin_date"] = self.dateField.get()
		self.data["train_type"] = self.tVar.get()
		self.data["getin_start_dtime"] = self.sVar.get()
		self.data["getin_end_dtime"] = self.eVar.get()
		self.data["order_qty_str"] = self.numField.get()
		
	def createCaptchaWindow(self,imgpath):
		self.captWin = Toplevel()
		self.captWin.title('Input captcha')
		img = PIL.ImageTk.PhotoImage(PIL.Image.open(imgpath))
		captchaLabel = Label(self.captWin, image=img)
		captchaLabel.grid(row=0,column=0)
		self.captchaField = Entry(self.captWin)
		self.captchaField["width"] = 10
		self.captchaField.grid(row=1, column=0, columnspan=1)
		captchaButton = Button(self.captWin)
		captchaButton["text"] = "Ok"
		captchaButton.grid(row=2,column=0)
		captchaButton["command"] = self.checkSearch
		os.remove(imgpath)
		self.captWin.mainloop()
		
	def checkSearch(self):
		if self.bookType == 'search':
			url = "http://railway1.hinet.net/wait_order_search.jsp"
		else:
			url = "http://railway.hinet.net/order_kind1.jsp"
		self.data['randInput']=self.captchaField.get()
		cookie = requests.utils.dict_from_cookiejar(self.sess.cookies)
		res = self.sess.get(url,cookies=cookie,
			headers=self.headers,params=self.data)
		if self.bookType == 'search':
			with open('result.html',"wb") as f:
				f.write(res.content)
			binary = res.content
			document = lxml.html.document_fromstring(binary)
			self.captWin.destroy()
			self.referUrl = res.url;
			self.disPlaySearch(document)
		else:
			with open('result.html',"wb") as f:
				f.write(res.content)
			binary = res.content
			document = lxml.html.document_fromstring(binary)
			timeTag = document.xpath('/html/body/p[5]/span[2]')
			codeTag = document.xpath('//*[@id="spanOrderCode"]')
			if not timeTag:
				errorTag = document.xpath('/html/body/form/p[1]/strong')
				if errorTag:
					messagebox.showinfo("Error", "Captcha Error!")
					return
				errorTag = document.xpath('/html/body/p[1]/font/strong/span/strong')
				if errorTag:
					messagebox.showinfo("Error", "No ticket!")
					return
				errorTag = document.xpath('/html/frameset')
				if errorTag:
					messagebox.showinfo("Error", "Input error!")
					return
				errorTag = document.xpath('/html/body/font')
				if errorTag:
					messagebox.showinfo("Error","ID error!")
					return
				messagebox.showinfo("Error","QQ error")
				return
			now = datetime.datetime.now()
			filePath = "record/success" + now.strftime('%Y%m%d%H%M%S') + ".html"
			with open(filePath,"wb") as f:
				f.write(res.content)
			messagebox.showinfo("Success", "Success\nLeave time is\n"+timeTag[0].text
				+"\nCode: "+codeTag[0].text)
		
	
	def disPlaySearch(self,document):
		numTag = document.xpath('/html/body/table[2]/tr/td/a')
		typeTag = document.xpath('/html/body/table[2]/tr/td[2]')
		sTimeTag = document.xpath('/html/body/table[2]/tr/td[3]')
		eTimeTag = document.xpath('/html/body/table[2]/tr/td[6]')
		otherTag = document.xpath('/html/body/table[2]/tr/td[7]')
		if not numTag:
			errorTag = document.xpath('/html/body/form/p[1]/strong')
			if errorTag:
				messagebox.showinfo("Error", "Captcha Error!")
				return
			errorTag = document.xpath('/html/body/p[1]/font/strong/span/strong')
			if errorTag:
				messagebox.showinfo("Error", "No ticket!")
				return
			errorTag = document.xpath('/html/frameset')
			if errorTag:
				messagebox.showinfo("Error", "Input error!")
				return
			errorTag = document.xpath('/html/body/font')
			if errorTag:
				messagebox.showinfo("Error","ID error!")
				return
			messagebox.showinfo("Error", "Input Error!")
			return
		self.searchWin = Toplevel()
		self.searchWin.title('Search result')
		self.setSearchText(self.searchWin)
		self.bookOption = {}
		for i in range(len(numTag)):
			num = Label(self.searchWin)
			num["text"] = numTag[i].text.strip()
			num.grid(row=i+1,column=0)
			self.bookOption[num['text']] = numTag[i].attrib['href']
			type = Label(self.searchWin)
			type["text"] = typeTag[i+1].text.strip()
			type.grid(row=i+1,column=1)
			sTime = Label(self.searchWin)
			sTime["text"] = sTimeTag[i+1].text.strip()
			sTime.grid(row=i+1,column=2)
			eTime = Label(self.searchWin)
			eTime["text"] = eTimeTag[i+1].text.strip()
			eTime.grid(row=i+1,column=3)
			if otherTag[i+1].text:
				other = Label(self.searchWin)
				other["text"] = otherTag[i+1].text.strip()
				other.grid(row=i+1,column=4)
				
		self.bVar = StringVar(self.searchWin)
		self.bVar.set(numTag[0].text.strip())
		bookMenu = OptionMenu(self.searchWin,self.bVar,*list(self.bookOption.keys()))
		bookMenu.grid(row=len(numTag)+1, column=0)
		
		bookButton = Button(self.searchWin)
		bookButton['text'] = 'Book'
		bookButton['command'] = self.bookTicket
		bookButton.grid(row=len(numTag)+1, column=1)
		
	def setSearchText(self,win):
		numLabel = Label(win)
		numLabel["text"] = "Train num"
		numLabel.grid(row=0,column=0)
		typeLabel = Label(win)
		typeLabel["text"] = "Type"
		typeLabel.grid(row=0,column=1)
		sTimeLabel = Label(win)
		sTimeLabel["text"] = "Leave time"
		sTimeLabel.grid(row=0,column=2)
		eTimeLabel = Label(win)
		eTimeLabel["text"] = "Arrive time"
		eTimeLabel.grid(row=0,column=3)
		otherLabel = Label(win)
		otherLabel["text"] = "Other"
		otherLabel.grid(row=0,column=4)
		
	def bookTicket(self):
		cookie = requests.utils.dict_from_cookiejar(self.sess.cookies)
		self.headers={"Referer":self.referUrl}
		url = self.bookOption[self.bVar.get()]
		res = self.sess.get("http://railway1.hinet.net/"+url,cookies=cookie,headers=self.headers)
		binary = res.content
		with open('bookResult.html',"wb") as f:
			f.write(res.content)
		document = lxml.html.document_fromstring(binary)
		timeTag = document.xpath('/html/body/p[5]/span[2]')
		codeTag = document.xpath('//*[@id="spanOrderCode"]')
		if not timeTag:
			errorTag = document.xpath('/html/body/form/p[1]/strong')
			if errorTag:
				messagebox.showinfo("Error", "Captcha Error!")
				return
			errorTag = document.xpath('/html/body/p[1]/font/strong/span/strong')
			if errorTag:
				messagebox.showinfo("Error", "No ticket!")
				return
			errorTag = document.xpath('/html/frameset')
			if errorTag:
				messagebox.showinfo("Error", "Input error!")
				return
			errorTag = document.xpath('/html/body/font')
			if errorTag:
				messagebox.showinfo("Error","ID error!")
				return
			messagebox.showinfo("Error","QQ error")
			return
		now = datetime.datetime.now()
		filePath = "record/success" + now.strftime('%Y%m%d%H%M%S') + ".html"
		with open(filePath,"wb") as f:
			f.write(res.content)
		messagebox.showinfo("Success", "Success\nLeave time is\n"+timeTag[0].text
			+"\nCode: "+codeTag[0].text)

if __name__ == '__main__':
	root = Tk()
	root.title('TicketBooker')
	app = TicketBooker(master=root)
	app.mainloop()
