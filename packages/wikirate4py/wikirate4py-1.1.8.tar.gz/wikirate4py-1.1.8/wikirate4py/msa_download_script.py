import time
import csv
from datetime import datetime

import wikirate4py
from wikirate4py import Cursor

api = wikirate4py.API('ThessaloWikiRate')

company_groups = ['MSA_Garment', 'MSA_Food_Beverage', 'MSA_Hospitality', 'MSA_Financial', '']
for company_group in company_groups:
    cursor = Cursor(api.get_answers_by_id, identifier=12641428, per_page=1000, company_group=company_group,
                    view="detailed")

    answers = []

    start_time = time.time()
    while cursor.has_next():
        answers.extend(cursor.next())
        end_time = time.time()
        start_time = time.time()

    # end_time = time.time()
    # exec_time = end_time - start_time
    # print('Retrieving Dataset for {0} sector completed'.format(company_group))
    # print(exec_time)
    # print('------------------------------------------------------------------------------------')

    header = ["Answer Page", "Metric", "Company", "Year", "Value", "Source Page"]
    now = datetime.utcnow()
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    rows = []

    for answer in answers:
        sources = ""
        for source in answer.sources:
            sources += 'https://wikirate.org/' + source + ", "
        if len(sources) > 0:
            sources = sources[:-2]
        row = [answer.url.replace('\.json', ''), answer.metric, answer.company, answer.year, answer.value, sources]
        rows.append(row)

    with open("/srv/msa-beyond-compliance/src/assets/downloads/Wikirate_MSA_Beyond_Compliance_Dashboard_Dataset_{0}.csv".format(
            'full' if company_group == '' else company_group), 'w',
            encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "# https://wikirate.org/MSA_Beyond_Compliance_Dashboard?filter[company_group]={0}".format(
                company_group)])
        writer.writerow(["# Creative Commons Attribution-ShareAlike 4.0 International License"])
        writer.writerow(["# Last updated at: {0} UTC".format(date_time)])
        writer.writerow(["# "])
        writer.writerow(header)
        # write the data
        writer.writerows(rows)

    f.close()
