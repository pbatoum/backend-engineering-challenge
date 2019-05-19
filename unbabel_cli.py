#!/bin/python

import json
import datetime
import os
import sys, getopt

class UnbabelError(Exception):
    pass

def ValidateEventIntegrity(event):
    """
        Make sure event have at least thhe following keys:
            - duration
            - event_name and is set to translation_delivered
            - timestamp
        params:
            event : dict
        return True/False
    """
    required = ['event_name', 'duration', 'timestamp']
    for elt in required:
        if elt not in event.keys():
            return False
        if event['event_name'] != 'translation_delivered':
            return False
    
    return True

def JsonfileToListofdict(file_path):
    """
        Extract events from input file.
        params :
            file_path : string ==> path to the input json file

        return list of events as list of dict
    """
    if not os.path.isfile(file_path):
        raise UnbabelError('File Does not exist')
    data = [json.loads(line) for line in open(file_path, 'r')]

    return data

def SortEvents(events):
    """
        sort list of events, make sure we have them from the oldest
        to the newest (timestamp)
        params:
            events : list ==> list of dictionaries (events)
        return list of events as list of dict 
    """
    sorted_events = sorted(events, key = lambda k:datetime.datetime.strptime(k['timestamp'], '%Y-%m-%d %H:%M:%S.%f'))
    
    return sorted_events
    
def CheckDeltabetweenTimes(date, event_date, window_size=10):
    """
        return True/False
        True if difference between date and event_date is <= window_size
        False if not

    """
    window_size_delta = datetime.timedelta(minutes=window_size)
    if (date - event_date).days < 0:
        return False
    return (date - event_date) <= window_size_delta

def ComputeAverageDeliveryTime(events, frequency=1, window_size=10):
    """
        Count for each 'frequency' the average delivery time of 'events' for
        the past 'window_size' minutes
        params :
            events : list ==> sorted list of events
            frequency : int ==> minutes
            window_size : int ==> minutes

        return list of dict
    """
    frequency_delta = datetime.timedelta(minutes=frequency)
    window_size_delta = datetime.timedelta(minutes=int(window_size))
    start_time = datetime.datetime.strptime(events[0]['timestamp'], '%Y-%m-%d %H:%M:%S.%f').replace(second=0, microsecond=0) 
    end_time = datetime.datetime.strptime(events[len(events)-1]['timestamp'], '%Y-%m-%d %H:%M:%S.%f').replace(second=0, microsecond=0) + frequency_delta
    date = start_time
    data = []
    while date <= end_time:
        N = 0
        cumsum = 0
        for idx, event in enumerate(events, 1):
            if not ValidateEventIntegrity(event):
                raise UnbabelError('%s is not a valid event entry'%event)
            event_date = datetime.datetime.strptime(event['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
            if CheckDeltabetweenTimes(date, event_date):
                cumsum += event['duration']
                N += 1
        if N: 
            data.append({'date' : str(date), 'average_delivery_time':cumsum / float(N)})
        else:
            data.append({'date' : str(date), 'average_delivery_time':0})
        date += frequency_delta

    with open('data.json', 'w') as outfile:  
        json.dump(data, outfile)

def UsageExit():
    usage = """Usage : 
               must be run on python 2.7
               unbabel_cli --input_file filename --window_size timeframe
               filename and timeframe are required
               timeframe must be an integer
               use --help to print this message
    """
    print(usage)
    sys.exit(2)

if __name__ == '__main__':
    json_file = None
    ws = None
    try:
        options, args = getopt.getopt(sys.argv[1:],'iwh', ["input_file=", 'window_size=', 'help'])
        for opt, value in options:
            if opt in ('-h', '--help'):
                UsageExit()
            if opt in ('-i', '--input_file'):
                json_file = value
            if opt in ('-w', '--window_size'):
                ws = value
    except getopt.GetoptError as e:
        UsageExit()
    try:
        int(ws)
    except:
        UsageExit()
    if not os.path.isfile(json_file):
        UsageExit()
    if json_file and ws:
        events = JsonfileToListofdict(json_file)
        events = SortEvents(events)
        ComputeAverageDeliveryTime(events, window_size=ws)
    else:
        UsageExit()
