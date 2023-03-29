import requests
import concurrent.futures
import pprint
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from notion_client import Client
import json

env_values = dotenv_values(".env")

notion = Client(auth=env_values['NOTION_SECRET'])
database_id = 'c6443abd824a403ba2d5398d67c3a76b'


pp = pprint.PrettyPrinter(indent=2)

def updateNotionPage(page_id, properties):
	notion.pages.update(page_id=page_id, properties=properties)

def getNotionID(title):
	response = notion.databases.query(database_id=database_id, filter= {'property': 'Name', 'title': { 'equals': title } })
	try:
		notion_title = response['results'][0]['properties']['Name']['title'][0]['plain_text']
		if notion_title != title:
			print(f'Notion title: {notion_title} != {title}')
		return response['results'][0]['id']
	except:
		print(f'No Notion page found for {title}')
		return ''

def updatePageUsingUrlInformation(url):
	req = requests.get(url)
	soup = BeautifulSoup(req.text, 'html.parser')
	titles = soup.find_all('title')
	title = ''
	if len(titles) >= 1:
		title = titles[0].text.strip().replace('23 SOE: ', '')
		if title == 'Brotherly Love 16':
			title = 'Brotherly Love Point 16'
	lis = soup.select('form ul li')
	required = []
	optional = []
	for li in lis:
		label = li.find('label')
		fieldset = li.find('fieldset')
		if fieldset is not None:
			legend = fieldset.find('legend')
			if legend is not None:
				legend = legend.text.strip()
				legend = " ".join(legend.split())
				if '*' in legend:
					required.append(legend.replace('*', ''))
				else:
					optional.append(legend)
		if label is not None and label.parent.name == 'li':
			text = label.text.replace('\n', '').replace('\t', '').strip()
			if text not in ['Name*', 'Email*', 'College/University*', 'Additional Comments', 'Do Not Fill This Out', 'Yes', 'No']:
				if '*' in text:
					required.append(text.replace('*', ''))
				else:
					optional.append(text)
	rtn = {}
	rtn['title'] = title
	
	whatToSubmit = ""
	if len(required) > 0:
		whatToSubmit += 'Required:\n'
		whatToSubmit += '\n'.join(f'\t{i+1}. {item}' for i, item in enumerate(required))
	if len(optional) > 0:
		whatToSubmit += '\nOptional:\n'
		whatToSubmit += '\n'.join(f'\t{i+1}. {item}' for i, item in enumerate(optional))
	rtn['whatToSubmit'] = whatToSubmit
	pageID = getNotionID(title)
	rtn['pageID'] = pageID

	properties = {
		'What to Submit': {
				'type': 'rich_text',
				'rich_text': [
					{
						'text': {
							'content': whatToSubmit,
							'link': None
						},
						'annotations': {
							'bold': False,
							'italic': False,
							'strikethrough': False,
							'underline': False,
							'code': False,
							'color': 'default'
						},
						'type': 'text'
					}
				]
			}
		}
	rtn['properties'] = properties
	updateNotionPage(pageID, properties)
	return rtn



urls = []
with open('checklist.html', 'r') as f:
	data = f.read()
	soup = BeautifulSoup(data, 'html.parser')
	for link in soup.find_all('a'):
		href = link.get('href')
		if href != None and href.startswith('https://zetabetatau.wufoo.com/'):
			urls.append(href)
			
res = []
with concurrent.futures.ThreadPoolExecutor(max_workers=len(urls)) as pool:
	futures = [pool.submit(updatePageUsingUrlInformation, url) for url in urls]
	for future in concurrent.futures.as_completed(futures):
		result = future.result()
		res.append(result)

json_object = json.dumps({ 'info': res }, indent=4)
with open("info.json", "w") as outfile:
    outfile.write(json_object)