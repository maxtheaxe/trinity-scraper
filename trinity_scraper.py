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

def post_req(url, data):
	'''performs a post request given a url and data, returns response'''
	# ref: https://community.dataquest.io/t/web-scraping-without-selenium/456297
	headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
			'content-type': 'application/json; charset=UTF-8'}
	cookies = browser_cookie3.chrome(domain_name='internet3.trincoll.edu')
	print("cookies:\n", cookies)
	for _ in range(5):
		try:
			response = requests.post(url, data=data.encode('utf-8'), headers=headers, timeout=20, cookies=cookies)
			if response.status_code == 200:
				return response
		except Exception as e:
			print(e)
			continue
	print('Error status code', response.status_code, response.text)

def grab_email(student_name = ["Kendall", "H.", "Brown"]):
	'''given the name of student, returns their email'''
	lookup_url = 'https://internet3.trincoll.edu/pTools/Directory_wp.aspx'
	# student_name is list in format [first, middle, last]
	# insert student name into request body in appropriate format
	data = "__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPDwUJMzE4NTY4MDE2D2QWAgIDD2QWAgIRDxYCHgdWaXNpYmxlaGRkWlkFIfH3xPbt%2FpRMEVF28H5zAnfKteS0JVPrAfWDOAo%3D&__VIEWSTATEGENERATOR=6845247C&__EVENTVALIDATION=%2FwEdAAmxNz0EFftFcHbAGp4e0t7hcbPKx50kq3egClC2RlspeC2xiRVTqzGkI4MPBO6VPO3lEzO1ijM9q%2FQSZVzorA1gWWj0ciZIBshSehh2B6iuhwivHF9mc03OEeiXOsVdAx7LHM5qi2WaC%2Bu8uRejijG9E5WL%2FselN996AS2BLk%2FPTu6S23tvdLgY%2F67OcsepzKxJl6hSxqFoU3SiileJcWRut%2BFbcKdqAa6RWkXZ5WmFMg%3D%3D&txtLastname="
	data += student_name[2] + "&rblSearchType=Student&txtFirstname=" + student_name[0] + "&txtMiddlename=" + student_name[1] + "H.&btnSubmitSearch=Search"
	response = post_req(lookup_url, data)
	print("type: ", type(response.content.decode()))
	# print(str(response.content.decode()))
	# response_data = json.loads(response)
	# soup = BeautifulSoup(response.content, 'html.parser')
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