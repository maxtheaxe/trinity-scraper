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

def grab_email(student_name, slept = 1):
	'''given the name of student, returns their email'''
	# student_name is list in format [first, middle, last]
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
	return emails # will return list of len 0 if too many or none found

def collect_emails():
	'''given a list of names, returns a list of emails'''
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

def export_results(student_emails):
	'''exports the scraped directory as a csv'''
	with open('results/student_emails.csv', mode='w', newline='') as file:
		email_writer = csv.writer(file, delimiter=',')
		email_writer.writerow(['student email addresses']) # column label(s)
		for i in range(len(student_emails)):
			# emails aren't consistent enough to it this way, would need to
			# grab email in initial request (which is trivial, but don't have time)
			# first_name = student_emails[i].split('.')[0]
			email_writer.writerow([student_emails[i]]) # write name, email
	return

def main():
	print("\n\t---- Trinity Email Scraper by Max ----")
	# starting_point = launcher() # maybe handle progress thus far in case of crashes
	student_emails = collect_emails()
	export_results(student_emails)
	print("\n\t  ", len(student_emails), "emails successfully scraped\n")

if __name__ == '__main__':
	main()
