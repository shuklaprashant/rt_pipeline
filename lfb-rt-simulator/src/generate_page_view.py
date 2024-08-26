import random
import datetime
import calendar

def generate_pv(number_of_events = 1000):

    # sample_data = [{'user_id': 1234, 'postcode': 'SW19', 'webpage': 'www.website.com/index.html', 'timestamp': 1611662684}]
    POSTCODES = ['NG1', 'SE10', 'SE9', 'SW19']
    URLs = ['www.website.com/index.html', 'www.google.com/index.html']
    
    for i in range(number_of_events):
        event = {
            'user_id': random.randint(1001, 9999),
            'postcode': random.choice(POSTCODES),
            'webpage': random.choice(URLs),
            'at_time': calendar.timegm(datetime.datetime.now().timetuple())
            }
        
        yield event