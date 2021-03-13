# trinity-scraper by max
import requests
import browser_cookie3
import json
import re

def get_dir():
	'''grabs the latest directory pdf from trinity website'''
	response = requests.get('https://internet3.trincoll.edu/pTools/docs/studph.pdf')
	with open('results/directory.pdf', 'wb') as file:
		file.write(response.content) # save the file we just grabbed
	return

def ingest_pdf():
	'''parses the pdf content into student names and class years'''
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

def grab_email(student_name = ["Kendall", "H.", "Brown"]):
	'''given the name of student, returns their email'''
	# student_name is list in format [first, middle, last]
	response = query_dir(student_name)
	# could use bs4 to parse response, but honestly not even necessary
	email_pattern = '(?:mailto:)[a-z.@]+'
	# search for email that comes after "mailto:"
	match = re.search(email_pattern, response.content.decode())
	return match.group()

def collect_emails():
	'''given a list of names, returns a list of emails'''
	return

def export_results():
	'''exports the scraped directory as a csv'''
	return

def main():
	# get_dir() # download the latest directory as a pdf
	email = grab_email()
	print("email grabbed: ", email)

if __name__ == '__main__':
	main()