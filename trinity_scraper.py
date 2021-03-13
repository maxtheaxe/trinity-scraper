# trinity-scraper by max
import requests

def get_dir():
	'''grabs the latest directory pdf from trinity website'''
	r = requests.get('https://internet3.trincoll.edu/pTools/docs/studph.pdf')
	with open('results/directory.pdf', 'wb') as f:
		f.write(r.content)
	return

def ingest_pdf():
	'''parses the pdf content into student names and class years'''
	return

def grab_email():
	'''given the name of student, returns their email'''
	return

def collect_emails():
	'''given a list of names, returns a list of emails'''
	return

def export_results():
	'''exports the scraped directory as a csv'''
	return

def main():
	# get_dir() # download the latest directory as a pdf

if __name__ == '__main__':
	main()