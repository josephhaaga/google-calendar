# Google Calendar
Simple CLI for Google Calendar

## Get Summary of next event
`python3 quickstart.py | head -1 | cut -d ' ' -f 2-`

## Generate a status message
Pipe the following into your Slack client 

`echo "Joseph Haaga is currently $(~/anaconda3/bin/python3 quickstart.py | head -1 | cut -d ' ' -f 2-)"`
