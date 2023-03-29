# SOE Parser
This is a parser for the SOE live tracker data. I exported the live tracker to an excel sheet. From there I mapped each tab of the spreadsheet to a worksheet object for each category of points. Using those objects I was able to parse the data into a JSON object. I then used the JSON object to create send the data to the notion database.

## Getting started
- Create an integration in notion and get the secret key.
- Add the integration to the database you want to add the data to.
  - Instructions for integrations can be found [here](https://www.notion.so/help/create-integrations-with-the-notion-api).
- Be sure to add the live tracker excel file (2023 currently in this repo) to the root directory of the project.
- Update the excel file name on line 14.
- Update the worksheet references, responsibility mappings, and database ID as needed.
- Create a `.env` file in the root directory and add `NOTION_SECRET=your_secret` to the file.
- Create a virtual environment and activate it.
  - `mkdir venv && python3 -m venv venv && . venv/bin/activate`
    - Instructions are probably slightly different for windows.
- In the root directory run `pip3 install -r requirements.txt` to install the dependencies.
- You should now be able to run `python3 soeParser.py` and the data should be added to the notion database.
- See `whatToSubmit.py` for an example of how to update the notion pages with what to submit after obtaining the inital SOE data.