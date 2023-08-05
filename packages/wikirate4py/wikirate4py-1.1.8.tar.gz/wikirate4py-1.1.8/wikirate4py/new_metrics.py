import pandas as pd
import wikirate4py
from pymongo import MongoClient

client = MongoClient("localhost:27017",
                     username='admin',
                     password='w00d4th3s0u1',
                     authSource='admin')

db = client.get_database("sec_filings")

df = pd.read_excel('D:/WikiRate/data/sec/Selected SEC metrics.xlsx',
                   sheet_name='metrics', engine='openpyxl')

api = wikirate4py.API('ThessaloWikiRate')

for index, row in df.iterrows():
    designer = row['metric_designer']
    name = row['metric_name']
    tag = row['tag']
    about = row['about']
    value_type = row['value_type']
    unit = row['unit']
    question = row['question']

    print(index)
    print(name)
    try:

        metric = api.add_metric(designer=designer,
                                name=name,
                                question=question,
                                topics=['Annual Reporting', 'Corporate Accountability', 'Financial'],
                                metric_type='Researched',
                                value_type=value_type,
                                unit='USD',
                                research_policy='Community Assessed',
                                report_type='Form 10-K',
                                about=about,
                                methodology='<p>Companies should report their financial performance in their annual financial reports, and these are the best places to find this information.</p><p>For companies that file with the SEC, this information can be found within their \"Form 10-K\" filings. You can often find these documents by searching for \"Company 10-k\", or they can be found through the <a href=\"http://www.sec.gov/edgar/searchedgar/companysearch.html\">SEC\'s EDGAR search</a>.</p>')

        json = metric.json()
        json['_id'] = json['id']
        del json['about']
        del json['methodology']

        del json['id']
        json['tag'] = row['tag']
        db.metrics.insert_one(json)

        print(json)
    except Exception as e:
        print(e.__str__())
