import jpype
jpype.startJVM()
import asposecells
from asposecells.api import Workbook
from dotenv import dotenv_values
import json
from notion_client import Client

env_values = dotenv_values(".env")

notion = Client(auth=env_values['NOTION_SECRET'])
database_id = 'c6443abd824a403ba2d5398d67c3a76b'

workbook = Workbook("2023StandardsofExcellenceLiveTracker.xlsx")

# map responsibilities to points
responsibilities = {
    'Intellectual Awareness': {
		'Point 1': ['Programming'],
		'Point 2': ['Risk'],
		'Point 3': ['Academics', 'Operations'],
		'Point 4': ['President'],
		'Point 5': ['Academics'],
		'Point 6': ['Communications'],
		'Point 7': ['Communications'],
		'Point 8': ['Communications', 'Recruitment'],
		'Point 9': ['Programming'],
	},
	'Social Responsibility': {
		'Point 1': ['BDD', 'Programming'],
		'Point 2': ['Risk', 'Programming'],
		'Point 3': ['Risk', 'Programming'],
		'Point 4': ['Risk', 'Social'],
		'Point 5': ['Risk', 'Social'],
		'Point 6': ['Risk', 'Social'],
		'Point 7': ['Standards'],
		'Point 8': ['Operations'],
		'Point 9': ['President', 'Operations'],
		'Point 10': ['President', 'Operations'],
		'Point 11': ['President', 'Operations'],
		'Point 12': ['President'],
		'Point 13': ['President'],
		'Point 14': ['Heritage'],
		'Point 15': ['Community Service'],
		'Point 16': ['Philanthropy'],
		'Point 17': ['Community Service', 'Programming'],
		'Point 18': ['Philanthropy', 'Programming'],
		'Point 19': ['Programming'],
		'Point 20': ['Philanthropy', 'Programming'],
	},
	'Integrity': {
		'Point 1': ['Risk'],
		'Point 2': ['Programming', 'BDD'],
		'Point 3': ['Finance'],
		'Point 4': ['Finance'],
		'Point 5': ['Finance'],
		'Point 6': ['Finance'],
		'Point 7': ['Finance'],
	},
	'Brotherly Love': {
		'Point 1': ['Operations'],
		'Point 2': ['President', 'Standards', 'BDD', 'Operations'],
		'Point 3': ['BDD'],
		'Point 4': ['Operations', 'Communications', 'Programming', 'BDD', 'Standards', 'Recruitment'],
		'Point 5': ['BDD'],
		'Point 6': ['BDD'],
		'Point 7': ['BDD'],
		'Point 8': ['BDD'],
		'Point 9': ['Parent/Alum', 'Communications'],
		'Point 10': ['Parent/Alum'],
		'Point 11': ['Parent/Alum'],
		'Point 12': ['Communications'],
		'Point 13': ['Athletics'],
		'Point 14': ['President', 'BDD'],
		'Point 15': ['Recruitment'],
		'Point 16': ['Recruitment'],
		'Point 17': ['Recruitment'],
		'Point 18': ['Recruitment'],
		'Point 19': ['President', 'BDD'],
		'Point 20': ['BDD', 'Provost'],
		'Point 21': ['BDD', 'Provost'],
		'Point 22': ['BDD'],
		'Point 23': ['BDD'],
		'Point 24': ['BDD'],
		'Point 25': ['BDD', 'Parent/Alum', 'Programming']
	}
}

# map worksheets to their names and references, and init points list
worksheets = {
	'intellectual_awareness_worksheet': {
		'name': 'Intellectual Awareness',
		'worksheet_ref': workbook.getWorksheets().get(1),
		'points': []
	},
	'social_responsibilty_worksheet': {
		'name': 'Social Responsibility',
		'worksheet_ref': workbook.getWorksheets().get(2),
		'points': []
	},
	'integrity_worksheet': {
		'name': 'Integrity',
		'worksheet_ref': workbook.getWorksheets().get(3),
		'points': []
	},
	'brotherly_love_worksheet': {
		'name': 'Brotherly Love',
		'worksheet_ref': workbook.getWorksheets().get(4),
		'points': []
	}
}

# get all points from worksheets, create dict, and then use that to create the notion pages. 
# I also dumped to a json obj because that's how I started this code and then I just left it in
for worksheet_tab_name, dict in worksheets.items():
	worksheet = dict['worksheet_ref']
	worksheet_name = dict['name']
	cells = worksheet.getCells()
	col = 'D'
	while cells.get(f'{col}1').getValue() != None:
		name = f'{worksheet_name} {cells.get(f"{col}1").getValue()}'
		description = worksheet.getComments().get(f'{col}1').getNote()
		if col == 'Z':
			col = 'AA'
		elif len(col) != 1:
			col = f'{col[0]}{chr(ord(col[1]) + 1)}'
		else:
			col = chr(ord(col) + 1)
		# create the notion page
		page = { 
			'Completed': {
				'type': 'checkbox',
				'checkbox': False
			},
			'Name': {
				'type': 'title',
				'title': [
					{
						'text': {
							'content': str(name),
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
			},
			'Description': {
				'type': 'rich_text',
				'rich_text': [
					{
						'text': {
							'content': str(description),
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
			},
			'Who': { 
				'type': 'multi_select',
				'multi_select': [{'name': name} for name in responsibilities[worksheet_name][f'Point {str(name).strip().split()[-1]}']]
			}
		}
		# append to the dictionary I'm making for the json dump
		worksheets[worksheet_tab_name]['points'].append(page)
		# make the call to the notion api
		notion.pages.create(parent={'database_id': database_id}, properties=page)

# dump to json
json_dict = { 'points': [] }
for worksheet_tab_name in worksheets.keys():
	json_dict['points'].extend(worksheets[worksheet_tab_name]['points'])
with open("points.json", "w") as outfile:
    json.dump(json_dict, outfile)

jpype.shutdownJVM()