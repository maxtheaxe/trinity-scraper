# trinity-scraper by max
import requests
import pdfminer.high_level as pdf
import re
from string import ascii_lowercase as alpha
import csv
from tqdm import tqdm
# import browser_cookie3

def get_dir():
	'''grabs the latest directory pdf from trinity website'''
	response = requests.get('https://internet3.trincoll.edu/pTools/docs/studph.pdf')
	with open('results/directory.pdf', 'wb') as file:
		file.write(response.content) # save the file we just grabbed
	return

def ingest_pdf(pdf_location = 'results/directory.pdf'):
	'''parses the pdf content into student names and class years'''
	pdf_blob = pdf.extract_text(pdf_location) # extract all text from dir pdf
	# print("pdf blob:\n", str(pdf_blob))
	with open('results/directory_content.txt', 'w', encoding='utf-8') as file:
		file.write(pdf_blob)
	# do *some* regex to identify names
	# current attempt: "(?:\n)[a-zA-Z, ]{1,}(?:\. ){10,}"
	return

def query_dir(student_name):
	'''performs a post request given a url and data, returns response'''
	# request built using postman and browser testing
	url = "https://internet3.trincoll.edu/pTools/Directory_wp.aspx"
	payload={
		'txtLastname': student_name[2],
		'rblSearchType': 'Student',
		'txtFirstname': student_name[0],
		'txtMiddlename': student_name[1],
		'btnSubmitSearch': 'Search',
		'__EVENTTARGET': '',
		'__EVENTARGUMENT': '',
		'__VIEWSTATE': '/wEPDwUJMzE4NTY4MDE2D2QWAgIDD2QWAgIRDxYCHgdWaXNpYmxlaGRkWlkFIfH3xPbt/pRMEVF28H5zAnfKteS0JVPrAfWDOAo=',
		'__VIEWSTATEGENERATOR': '6845247C',
		'__EVENTVALIDATION': '/wEdAAmxNz0EFftFcHbAGp4e0t7hcbPKx50kq3egClC2RlspeC2xiRVTqzGkI4MPBO6VPO3lEzO1ijM9q/QSZVzorA1gWWj0ciZIBshSehh2B6iuhwivHF9mc03OEeiXOsVdAx7LHM5qi2WaC+u8uRejijG9E5WL/selN996AS2BLk/PTu6S23tvdLgY/67OcsepzKxJl6hSxqFoU3SiileJcWRut+FbcKdqAa6RWkXZ5WmFMg=='
	}
	files=[]
	headers = {'Cookie': 'ASP.NET_SessionId=iwryzakfcnnbgtoakmayjs4f'}
	response = requests.request("POST", url, headers=headers, data=payload, files=files)
	return response

def grab_email(student_name):
	'''given the name of student, returns their email'''
	# student_name is list in format [first, middle, last]
	response = query_dir(student_name)
	# could use bs4 to parse response, but honestly not even necessary
	# email_pattern = '(?:mailto:)[a-z.@]+'
	# findall isn't working with non-capturing groups for some reason; can just slice
	email_pattern = 'mailto:[a-z.@]+'
	# search for email that comes after "mailto:"
	# match = re.search(email_pattern, response.content.decode())
	match = re.findall(email_pattern, response.content.decode()) # find *all* results
	try: # try to return names (will fail if too many)
		return match
	except:
		return [] # handle no results lazily

def collect_emails():
	'''given a list of names, returns a list of emails'''
	student_emails = []
	# loop over whole alphabet of last name combos
	for first in tqdm(alpha):
		name_fragment = first # build fragment of last name
		for second in tqdm(alpha):
			name_fragment += second # build fragment of last name
			# collect emails for each combo and slice off "mailto:"
			results = grab_email(["", "", name_fragment])
			if len(results) == 0:
				# then further break down the alphabet
				for third in alpha:
					name_fragment += third # build fragment of last name
					# collect emails for each combo and slice off "mailto:"
					results.extend(grab_email(["", "", name_fragment]))
				# add all results to master list
			for i in range(len(results)):
				# if not an alumni email (alumni emails also have years in them)
				if not any(x.isdigit() for x in results[i]):
					student_emails.append(results[i][7:])
					# print("found: ", results[i][7:]) # print each email found
	return student_emails

def export_results(student_emails):
	'''exports the scraped directory as a csv'''
	with open('results/student_emails.csv', mode='w') as file:
		email_writer = csv.writer(file)
		for i in range(len(student_emails)):
			employee_writer.writerow([student_emails[i]])
	return

def main():
	print("\n\t---- Trinity Email Scraper by Max ----")
	student_emails = collect_emails()
	export_results(student_emails)
	# print(len(student_emails), " emails successfully exported.")
	print("\n\t  ", len(student_emails), "emails successfully scraped\n")

if __name__ == '__main__':
	main()