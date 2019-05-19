import unittest
import unbabel_cli
import datetime
import os

class UnbabelCliTest(unittest.TestCase):
    """
        Unit tests for the unbabel_cli client
    """
    
    def test_ValidateEventIntegrity(self):
        """
            Test the ValidateEventIntegrity function
        """
        #Test a good event
        event = {"timestamp": "2018-12-26 18:11:08.509654","translation_id": "5aa5b2f39f7254a75aa5","source_language": "en","target_language": "fr","client_name": "easyjet","event_name": "translation_delivered","nr_words": 30, "duration": 20}
        self.assertTrue(unbabel_cli.ValidateEventIntegrity(event))
        #event_name missing
        event = {"timestamp": "2018-12-26 18:11:08.509654","translation_id": "5aa5b2f39f7254a75aa5","source_language": "en","target_language": "fr","client_name": "easyjet","nr_words": 30, "duration": 20}
        self.assertFalse(unbabel_cli.ValidateEventIntegrity(event))
        #duration missing
        event = {"timestamp": "2018-12-26 18:11:08.509654","translation_id": "5aa5b2f39f7254a75aa5","source_language": "en","target_language": "fr","client_name": "easyjet","nr_words": 30, "event_name": "translation_delivered"}
        self.assertFalse(unbabel_cli.ValidateEventIntegrity(event))
        #timestamp missing
        event = {"translation_id": "5aa5b2f39f7254a75aa5","source_language": "en","target_language": "fr","client_name": "easyjet","event_name": "translation_delivered","nr_words": 30, "duration": 20}
        self.assertFalse(unbabel_cli.ValidateEventIntegrity(event))
        #event_name not translation_delivered
        event = {"timestamp": "2018-12-26 18:11:08.509654","translation_id": "5aa5b2f39f7254a75aa5","source_language": "en","target_language": "fr","client_name": "easyjet","event_name": "translation_failed","nr_words": 30, "duration": 20}
        self.assertFalse(unbabel_cli.ValidateEventIntegrity(event))
        #source_language missing but should pass
        event = {"timestamp": "2018-12-26 18:11:08.509654","translation_id": "5aa5b2f39f7254a75aa5","target_language": "fr","client_name": "easyjet","event_name": "translation_delivered","nr_words": 30, "duration": 20}
        self.assertTrue(unbabel_cli.ValidateEventIntegrity(event))
        
    def test_JsonfileToListofdict(self):
        """
            Make sure we get a list of dict after parsing the file
        """
        #File does not exist exception raised
        with self.assertRaises(Exception) as context:
            unbabel_cli.JsonfileToListofdict('i/dont/exists')
        self.assertTrue('File Does not exist' in context.exception)
        #Good File
        data =  unbabel_cli.JsonfileToListofdict('events.json')
        self.assertIsInstance(data, type([]))
        self.assertEqual(len(data), 3)
        self.assertEqual(data[1]['client_name'], 'booking')

    def test_SortEvents(self):
        """
            test SortEvents function
        """
        data =  unbabel_cli.JsonfileToListofdict('events.json')
        self.assertEqual(data[0]['timestamp'], '2018-12-26 18:11:08.509654')
        self.assertEqual(data[1]['timestamp'], '2018-12-26 18:23:19.903159')
        self.assertEqual(data[2]['timestamp'], '2018-12-26 18:15:19.903159')
        data = unbabel_cli.SortEvents(data)
        self.assertEqual(data[0]['timestamp'], '2018-12-26 18:11:08.509654')
        self.assertEqual(data[1]['timestamp'], '2018-12-26 18:15:19.903159')
        self.assertEqual(data[2]['timestamp'], '2018-12-26 18:23:19.903159')
        
    def test_CheckDeltabetweenTimes(self):
        """
            test CheckDeltabetweenTimes function
        """
        date = datetime.datetime.strptime('2018-12-26 18:11:00', '%Y-%m-%d %H:%M:%S')
        event_date = datetime.datetime.strptime('2018-12-26 18:23:19.903159', '%Y-%m-%d %H:%M:%S.%f')
        self.assertFalse(unbabel_cli.CheckDeltabetweenTimes(date, event_date))
        date = datetime.datetime.strptime('2018-12-26 18:15:00', '%Y-%m-%d %H:%M:%S')
        self.assertFalse(unbabel_cli.CheckDeltabetweenTimes(date, event_date))
        date = datetime.datetime.strptime('2018-12-26 18:44:00', '%Y-%m-%d %H:%M:%S')
        self.assertFalse(unbabel_cli.CheckDeltabetweenTimes(date, event_date))
        date = datetime.datetime.strptime('2018-12-26 18:32:00', '%Y-%m-%d %H:%M:%S')
        self.assertTrue(unbabel_cli.CheckDeltabetweenTimes(date, event_date))

    def test_ComputeAverageDeliveryTime(self):
        """
            test ComputeAverageDeliveryTime function
        """
        events = unbabel_cli.JsonfileToListofdict('events.json')
        events = unbabel_cli.SortEvents(events)
        unbabel_cli.ComputeAverageDeliveryTime(events, window_size=10)
        #Make sure resulting file exists
        self.assertTrue(os.path.isfile('data.json'))
        data = unbabel_cli.JsonfileToListofdict('data.json')[0]
        #Make sure we have the number of entry corresponding to minutes between the highest time and the lowest one (18:11 to 18:24)
        self.assertEqual(len(data), 14)
        #verify average values
        for elt in data:
            if elt['date'] == '2018-12-26 18:11:00':
                self.assertEqual(float(elt['average_delivery_time']), float(0))
            if elt['date'] == '2018-12-26 18:15:00':
                self.assertEqual(float(elt['average_delivery_time']), float(20))
            if elt['date'] == '2018-12-26 18:23:00':
                self.assertEqual(float(elt['average_delivery_time']), float(31))
            if elt['date'] == '2018-12-26 18:24:00':
                self.assertEqual(float(elt['average_delivery_time']), float('42.5'))

if __name__ == '__main__':
    unittest.main()
    
