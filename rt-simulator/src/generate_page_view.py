import random
import datetime
import calendar
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_page_view_event(number_of_events=1000):
    """
    Generates a stream of page view events.

    Args:
        number_of_events (int): The number of events to generate.

    Yields:
        dict: A dictionary representing a page view event with fields:
              'user_id', 'postcode', 'webpage', and 'at_time'.
    """
    POSTCODES = ['NG1', 'SE10', 'SE9', 'SW19']
    URLs = ['www.website.com/index.html', 'www.google.com/index.html']

    logger.info(f"Starting to generate {number_of_events} page view events.")

    for i in range(number_of_events):
        event = {
            'user_id': random.randint(1001, 9999),
            'postcode': random.choice(POSTCODES),
            'webpage': random.choice(URLs),
            'at_time': calendar.timegm(datetime.datetime.now().timetuple())
        }

        logger.debug(f"Generated event {i+1}: {event}")
        yield event

    logger.info(f"Finished generating {number_of_events} page view events.")

if __name__ == "__main__":
    try:
        # Example of generating 10 page view events for testing
        for event in generate_page_view_event(10):
            print(event)
    except Exception as e:
        logger.error(f"Error during event generation: {e}")
