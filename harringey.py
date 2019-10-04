import pprint
import requests
from lxml import html
import re

class Harringey:

	def __init__(self,):
		self.base_url = "http://www.haringey.gov.uk"
		self.landing_url = "/children-and-families/schools-and-education/primary-schools/school-locations"

	def scrape_whole_council(self):
		'''
		Return a list of dictionnaires containing contact details
		for all schools from the council page

		get_school_urls: gets school urls from main page
		process_all_schools: for each url, scrapes all contact details
		and returns a dictionnary
		'''
		school_urls = self.get_school_urls()
		school_info = self.process_all_schools(school_urls)
		return school_info

	def get_school_urls(self):
		'''
		Scrape home page to identify all urls
		Search all urls to identify primary schools only based on title attribute
		Return a list containing urls for all primary schools
		'''
		base_page_html = self.get_page_html(self.landing_url)

		def is_school_link(a):
			'''
			Check if an entry on the page is a primary school
			'''
			try:
				if 'primary' in a.attrib['title']:
					return True
				else:
					return False
			except:
				return False

		all_page_links = base_page_html.findall('.//a')

		school_urls = []
		for a in all_page_links:
			if is_school_link(a):
				school_urls.append(a.attrib['href'])
		return school_urls

	def get_page_html(self, page_url):
		'''
		Get all HTML from a page
		Page url is combined with the base url 

		page_url = landing url for a single page (string)
		'''
		page_raw_html = requests.get(self.base_url + page_url).content
		page_html = html.fromstring(page_raw_html)
		return page_html

	def process_all_schools(self, school_urls):
		'''
		Return a list of dictionnaries containing
		contact details for every school url page

		school_urls: all primary school urls from
		main council page (list)
		'''
		schools = []
		for school in school_urls:
			school_obj = self.process_school(school)
			vals = school_obj.values()
			# if any entry in school disctionnary has multiple schools 
			if any([type(v) == list for v in vals]):
				school_obj_0, school_obj_1 = Harringey.process_multiple_schools(school_obj)
				schools.append(school_obj_0)
				schools.append(school_obj_1)
			else:
				schools.append(school_obj)
		return schools

	def process_school(self, school_url):
		'''
		Return a dictionnary of contact details for one school
		School name, Head Teacher, address, telephone, email

		school_url: url of a school page (string)
		'''
		school = {}
		page_html = self.get_page_html(school_url)
		school["name"] = self.get_school_name(page_html)
		school["head"] = self.get_school_head(page_html)
		school["address"] = self.get_school_address(page_html)
		school["telephone"] = self.get_school_phone(page_html)
		school["email"] = self.get_school_email(page_html)
		return school

	def duplicate_school(self, school):
		'''
		Create two separate school items when there are two schools on one page

		school: 
		'''
		for value in school.values():
			if len(school[value] == 2):
				school_zero[value] = school[value][0]
				school_one[value] = school[value][1]
			else:
				school_zero[value] = school[value][0]
				school_one[value] = school[value][0]
		return school_zero, school_one

	@staticmethod
	def process_multiple_schools(school_obj):
		school_obj_0 = {}
		school_obj_1 = {}
		for k in school_obj:
			if type(school_obj[k]) == list:
				v_0 = school_obj[k][0]
				v_1 = school_obj[k][1]
			else:
				v_0 = school_obj[k]
				v_1 = school_obj[k]
			school_obj_0[k] = v_0
			school_obj_1[k] = v_1
		return school_obj_0, school_obj_1

	#######################################################
	######### GET SCHOOL CONTACT DETAIL ENTRIES ###########
	######### AS STRINGS TO POPULATE SCHOOL DICTS #########
	#######################################################

	def get_school_name(self, page_html):
		school_name = page_html.find('.//*[@id="content-content"]/div[3]/div/div/div/div[2]/div/div[5]/div/div/h1')
		school_name = school_name.text_content()
		return school_name

	def get_school_head(self, page_html):
		head_texts = [
			'Head Teacher',
			'Headteacher',
			'Head of School',
			'Executive Principal',
			'Principal'
		]
		head = self.search_strong(head_texts, page_html)
		head = self.process_head(head)
		return Harringey.process_return(head)

	def get_school_address(self, page_html):
		address_text = [
			'Address'
		]
		address = self.search_strong(address_text, page_html)
		address = self.process_address(address)
		return Harringey.process_return(address)


	def get_school_phone(self, page_html):
		tel_text = [
			'Tel'
		]
		phone = self.search_strong(tel_text, page_html)
		phone = self.process_phone(phone)
		return Harringey.process_return(phone)

	def get_school_email(self, page_html):
		email_text = [
			'Email'
		]
		email = self.search_strong(email_text, page_html)
		email = self.process_email(email)
		return Harringey.process_return(email)


	##########################################################
	############# SCRAPE CONTACT DETAIL ENTRIES ##############
	##########################################################

	def search_strong(self, texts, page_html):
		'''
		Return text content embedded under HTML strong heading

		texts: relevant text to search for (list of strings)
		page_html: HTML of page to search 
		'''
		for text in texts:
			strong = page_html.xpath('.//strong[contains(text(), "' + text + '")]')
			content = Harringey.process_strong(strong)
			if content is not None:
				return content
		for text in texts:
			headings = page_html.xpath('.//h2')
			for head in headings:
				if text in head.text_content():
					content = head.getnext().text_content()
					return content

		if content is not None:
			return content

		for text in texts:
			headings = page_html.xpath('.//strong')
			for head in headings:
				if text in head.text_content():
					content = head.getparent().getnext().text_content()
					break
			else:
				break
		return content

	def split_by_capital_letter(self, address, address_searched):
		'''
		Split a string containing school address by capital letter
		'''
		a = address.split(address_searched.group(0))
		lower_case = address_searched.group(0)[0]
		upper_case = address_searched.group(0)[1]
		address_zero = a[0] + lower_case
		address_one = upper_case + a[1]
		return address_zero + "," + address_one

	def split_by_word(self, address, split_word):
		'''
		Split a string containing school address by a word

		address: school address (string)
		split word: word to split by (string)
		'''
		street, postcode = address.split(split_word)
		address = street + "," + split_word + "," + postcode
		return address

	def split_address(self, address):
		'''
		Split a string containing school address by 
		a particular word (London, Crouch End) 
		or by capital letter

		address: school addres (string)
		'''
		try:
			address = self.split_by_word(address, "London")
		except ValueError:
			try:
				address = self.split_by_word(address, "Crouch End")
			except ValueError:
				address = "Crouch End Hill, Crouch End, N8 8DN"
		address_searched = re.search("[a-z][A-Z]", address) 
		if address_searched is None:
			return address
		else:
			address = self.split_by_capital_letter(address, address_searched)
			return address

	def process_address(self, address):
		if len(address) == 2:
			address = [self.split_address(one_address) for one_address in address]
		else:
			address = self.split_address(address)
		return address

	def process_phone(self, phone):
		if len(phone) == 2:
			phone = [p for p in phone]
		return phone

	def process_email(self, email):
		try:
			if len(email) == 2:
				email = [e for e in email]
			else:
				email = email.split("mailto:")[1]
		except IndexError:
			pass
		return email

	def process_head(self, head):
		if len(head) == 2:
			head = [h for h in head]
		return head


	##########################################################
	########### STATIC METHODS FOR STRING PROCESSING #########
	##########################################################

	@staticmethod
	def process_string(s):
		'''
		Encode string in UTF-8 and remove Unicode

		s: string
		'''
		s = s.replace(u'\xa0', u' ')
		return s.encode('utf-8', 'ignore')

	@staticmethod
	def process_return(r):
		'''
		Call process_string method differently depending on 
		whether the string is embedded in a list or not

		r: any object
		'''
		if type(r) == list:
			return [Harringey.process_string(x) for x in r]
		else:
			return Harringey.process_string(r)

	@staticmethod
	def process_strong(strong_head):
		'''
		Process text embedded within the HTML strong tag
		(Once the search_strong function identifies relevant text)
		'''
		# there were no strong tags
		if len(strong_head) == 0:
			return None

		name = strong_head[0].tail
		if name is None:
			pass
		# if contains some text return it
		elif len(name.strip()) > 0:
			return name

		# otherwise we might be in a table, so return that
		tr = strong_head[0].getparent().getparent()
		tds = tr.xpath('.//td')
		if len(tds) > 0:
			try:
				head_1, head_2 = tds[1:]
			except ValueError:
				return None
			return head_1.text_content(), head_2.text_content()
		else:
			a = strong_head[0].getparent().xpath('.//a')
			if len(a) > 0:
				return a[0].attrib['href']
			else:
				return None

