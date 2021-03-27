# trinity-scraper by max
import requests
import re
from string import ascii_lowercase as alpha
import csv
from tqdm import tqdm
from bs4 import BeautifulSoup
import time

def query_dir(student_name):
	'''performs a post request given a url and data, returns response'''
	# student_name is list in format [last, first, class year]
	# request built using postman and browser testing
	url = "https://internet3.trincoll.edu/pTools/Directory_wp.aspx"
	payload={
		'txtLastname': student_name[0],
		'rblSearchType': 'Student',
		'txtFirstname': student_name[1],
		'txtMiddlename': '', # may need to be more specific later if this causes issues
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

def grab_email(student_name, slept = 1):
	'''given the name of student, returns their email'''
	# student_name is list in format [last, first, class year]
	try:
		response = query_dir(student_name)
	except: # if request times out
		if (slept == 5):
			tqdm.write("\n\trequest timed out too many times; exiting...")
			return False
		time.sleep(slept*120) # wait two minutes, probably got timed out
		tqdm.write("\n\trequest timed out; sleeping {} minutes...").format(slept*2)
		return grab_email(student_name, (slept + 1)) # try again
	emails = []
	# parse response with bs4
	soup = BeautifulSoup(response.content, features='html.parser')
	# find all links
	all_links = soup.find_all(href=True)
	# remove non emails
	for i in range(len(all_links)):
		if ('mailto:' in all_links[i].get('href')):
			emails.append(all_links[i].get('href'))
	# emails.append("no email found") # add error string to end in case no email found
	return emails # returns list len 0 if none found

def collect_emails(student_list):
	'''returns student list with added email column'''
	cleaned_student_list = [] # student list including only those who have an email
	for i in tqdm(range(len(student_list))):
		email = grab_email(student_list[i]) # grab email for given student
		if len(email) != 0: # assuming an email was actually found...
			student_list[i].append(email[0][7:]) # append email to sublist (w/o prefix)
			cleaned_student_list.append( student_list[i] ) # append to new student list
		# not sure why some students don't have a school email, maybe handle later
		# print(student_list[i]) # print current student info
	return cleaned_student_list

def brute_emails():
	'''returns a list of emails gathered by trying different last name prefixes'''
	student_emails = []
	# loop over whole alphabet of last name combos
	for first in tqdm(alpha, desc='Overall'): # label overall progress bar
		name_fragment = first # build fragment of last name
		for second in tqdm(alpha, desc=(first.upper()) + ' Names'): # label w curr letter
			name_fragment = first + second # build fragment of last name
			# collect emails for each combo and slice off "mailto:"
			results = grab_email(["", "", name_fragment])
			# in case errored out
			if results == False:
				return student_emails
			# print(name_fragment)
			if len(results) == 0:
				# then further break down the alphabet
				for third in alpha:
					name_fragment = first + second + third # build fragment of last name
					# collect emails for each combo and slice off "mailto:"
					results = grab_email(["", "", name_fragment])
					# in case errored out
					if results == False:
						return student_emails
					results.extend(results)
				# add all results to master list
			for i in range(len(results)):
				# if not an alumni email (alumni emails also have years in them)
				if not any(x.isdigit() for x in results[i]):
					student_emails.append(results[i][7:])
					# print("found: ", results[i][7:]) # print each email found
	return student_emails

def scrape_students():
	'''collects student names from student directory list'''
	student_list = [] # each entry contains [first, middle, last name, class year]
	# grab cached version of webpage (google converts pdf to html w alignment data)
	directory = requests.get('https://webcache.googleusercontent.com/search?q=cache:https://internet3.trincoll.edu/pTools/docs/studph.pdf')
	# parse response with bs4
	directory_soup = BeautifulSoup(directory.content, features='html.parser')
	# grab left-hand column of names (divs w style = 'left:59')
	student_elements = directory_soup.find_all('div', attrs={'style':re.compile(r'left:59')})
	# grab right-hand column of names (divs w style = 'left:479')
	student_elements.extend( directory_soup.find_all('div', attrs={'style':re.compile(r'left:479')}) )
	# sort out student names and class years
	name_pattern = '.*, [0-9]{2}' # pattern for finding names in elements
	# not sure what it means if they don't have a class listed
	weird_syntax_students = [] # maybe do something with them later?
	for i in range(len(student_elements)):
		# searches for [last, first, class] pattern and splits it on ', '
		try:
			student_info = re.search(name_pattern, student_elements[i].text).group().split(', ')
			# strip middle initial, if they have one
			middle_initial = ' [A-Z]\\.' # space, one capital letter, period
			# split returns list of split parts, just list of og string if no match found
			student_info[1] = re.split(middle_initial, student_info[1])[0]
			student_list.append(student_info) # record student info
		except AttributeError:
			# track students w/o class, in case want to handle later
			weird_syntax_students.append(student_elements[i].text)
		# print('student: ', student_info)
	# print(f'there were {len(weird_syntax_students)} students without a class year listed')
	# print(f'num students collected: {len(student_list)}')
	return student_list

def export_results(student_emails):
	'''exports the scraped directory as a csv'''
	with open('results/student_emails.csv', mode='w', newline='') as file:
		email_writer = csv.writer(file, delimiter=',')
		email_writer.writerow(['first', 'last', 'class', 'email']) # column label(s)
		for i in range(len(student_emails)):
			# student_name is list in format [last, first, class year, email]
			first = student_emails[i][1]
			last = student_emails[i][0]
			class_year = student_emails[i][2]
			email = student_emails[i][3]
			email_writer.writerow([first, last, class_year, email]) # write name, email
	return

def main():
	print("\n\t---- Trinity Email Scraper by Max ----")
	student_list = scrape_students()
	student_emails = collect_emails(student_list)
	export_results(student_emails)
	print(f"\n\t  {len(student_emails)} emails successfully scraped\n")

if __name__ == '__main__':
	main()
