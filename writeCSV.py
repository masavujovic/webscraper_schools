import csv
from harringey import Harringey


class WriteCSV:

	def __init__(self, school_list):
		self.school_list = school_list

	def write_to_csv(self, school_list):
		with open("school_database.csv", 'w') as csvfile:
			fieldnames = ["name", "head", "address", "email", "telephone"]
			writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
			writer.writeheader()
			for school in school_list:
				writer.writerow(school)
		return csvfile

h = Harringey()
urls = h.get_school_urls()
school_data = h.process_all_schools(urls)

csv_writer = WriteCSV(school_data)
school_database = csv_writer.write_to_csv(school_data) 

