#!/bin/env python3

import sys
import re
import datetime
import csv

import private

class Message(object):
    def __init__(self):
        self.date = ''
        self.sender = ''
        self.content = ''

    def day(self):
        return self.date.date()


def parse_whatsapp_file(filename):
    pattern_date_line = re.compile('^([0-9]{2}/[0-9]{2}/[0-9]{4}) à ([0-9]{2}:[0-9]{2}) - (.*)$')
    pattern_discussion= re.compile('^([^:]*): (.*)$')

    messages = []

    with open(filename) as f:
        for line in f:
            match = pattern_date_line.match(line)

            if match is None:
                # That means it's the last message continuation
                if len(messages) > 0:
                    messages[-1].content = messages[-1].content + '\n' + line

            else:
                msg = Message()

                # That means it's the start of a new message
                day  = match.group(1)
                hour = match.group(2)
                text = match.group(3)

                msg.date = datetime.datetime.strptime(day + ' ' + hour, "%d/%m/%Y %H:%M" )

                match = pattern_discussion.match(text)
                if match is not None:
                    msg.sender = match.group(1)
                    msg.content= match.group(2)

                    messages.append(msg)

                else:
                    # That means it's a system message, drop
                    pass

    return messages


def count_per_day(messages):
    dates = []

    for m in messages:
        day = m.day()
        sender = m.sender

        if len(dates) > 0 and dates[-1]['date'] == day:
            if sender in dates[-1]:
                dates[-1][sender] += 1
            else:
                dates[-1][sender] = 1
        else:
            dates.append({ 'date': day, sender: 1 })

    return dates


def count_per_day_to_csv(counts):
    f = csv.writer(open('counts.csv', 'w'))

    # Write CSV Header, If you dont need that, remove this line
    f.writerow(['date'] + private.recipients)

    for c in counts:
        row = [ c['date'].strftime('%d/%m/%Y') ]
        for id in private.recipients_ids:
            if id in c:
                row += [ c[id] ]
            else:
                row += [ 0 ]
        f.writerow(row)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = 'Discussion.txt'

    messages = parse_whatsapp_file(filename)

    counts = count_per_day(messages)
    count_per_day_to_csv(counts)
