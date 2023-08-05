import pandas as pd
from pymongo.errors import DuplicateKeyError

import wikirate4py
from pymongo import MongoClient

from wikirate4py import Cursor

client = MongoClient("localhost:27017",
                     username='admin',
                     password='w00d4th3s0u1',
                     authSource='admin')

db = client.get_database("msa_assessed")

api = wikirate4py.API('ThessaloWikiRate')

assessed_metrics = ["Business & Human Rights Resource Centre+Modern Slavery Statement",
                    "Business & Human Rights Resource Centre+MSA statement signed",
                    "Business & Human Rights Resource Centre+MSA Statement Approval",
                    "Walk Free+MSA Organizational structure and operations",
                    "Walk Free+MSA supply chain disclosure",
                    "Walk Free+MSA policy (revised)",
                    "Walk Free+MSA risk assessment",
                    "Walk Free+MSA Identification of risks",
                    "Walk Free+MSA risk management (revised)",
                    "Walk Free+MSA whistleblowing mechanism (revised)",
                    "Walk Free+MSA incidents identified",
                    "Walk Free+MSA incidents remediation (revised)",
                    "Walk Free+MSA training (revised)",
                    "Walk Free+MSA Performance Indicators",
                    "Walk Free+MSA Business Performance Indicators"]


def get_uk_assessed_statements():
    cursor = Cursor(api.get_answers_by_metric_id, metric_id=12602618, value='Yes', per_page=100)

    while cursor.has_next():
        answers = cursor.next()

        for answer in answers:
            print(answer)
            db.uk_assessed_0523.insert_one(answer.json())


def get_answers_on_assessed_metrics():
    assessed_statements = db.uk_assessed_0523.find()

    for statement in assessed_statements:
        # print(statement)
        for metric in assessed_metrics:
            metric_designer = metric.split('+')[0]
            metric_name = metric.split('+')[1]
            answer = api.get_answer_by(metric_designer,
                                       metric_name,
                                       statement['company'],
                                       statement['year'])

            json = answer.raw_json()
            json['_id'] = json['id']
            del json['id']
            try:
                db.uk_assessed_statements.insert_one(json)
            except DuplicateKeyError as e:
                print('duplicate')


def verify_statements():
    assessed_statements = db.uk_assessed_0523.find()

    for statement in assessed_statements:
        verified = True
        number_of_verified_answers = 0

        verified_answers = []
        verified_answers_ids = []
        unverified_answers = []
        unverified_answers_ids = []
        for metric in assessed_metrics:
            answer = db.uk_assessed_statements.find_one(
                {'metric': metric, 'company': statement['company'], 'year': statement['year']})
            print(answer)
            if len(answer['checked_by']) == 0:
                verified = False
                unverified_answers.append(answer['metric'])
                unverified_answers_ids.append(answer['_id'])
            else:
                number_of_verified_answers += 1
                verified_answers.append(answer['metric'])
                verified_answers_ids.append(answer['_id'])
        if verified:
            db.uk_assessed_0523.update_one({'_id': statement['_id']},
                                           {'$set': {'verified': True,
                                                     'verified_answers': verified_answers,
                                                     'unverified_answers': unverified_answers,
                                                     'verified_answers_ids': verified_answers_ids,
                                                     'unverified_answers_ids': unverified_answers_ids
                                                     }})
        else:
            db.uk_assessed_0523.update_one({'_id': statement['_id']},
                                           {'$set': {'number_of_verified_answers': number_of_verified_answers,
                                                     'verified_answers': verified_answers,
                                                     'unverified_answers': unverified_answers,
                                                     'verified_answers_ids': verified_answers_ids,
                                                     'unverified_answers_ids': unverified_answers_ids
                                                     }})


assessed_statements = db.uk_assessed_0523.find({'verified': {'$exists': False}})

f = open("D:\\Assessed Stats.csv", "a")

for statement in assessed_statements:
    f.write("{0};{1};{2};{3};{4};{5};{6}\n".format(
        statement['company'],
        statement['year'],
        statement['number_of_verified_answers'],
        statement['unverified_answers'],
        statement['verified_answers'],
        statement['unverified_answers_ids'],
        statement['verified_answers_ids']
    ))

f.close()

# get_uk_assessed_statements()
# get_answers_on_assessed_metrics()
