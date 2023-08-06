# airportfinder

airportfinder is a Python library that provides a simple interface for looking up airport information by IATA code or airport name. It uses a JSON dataset of airports worldwide to provide accurate and up-to-date information.

## Installation

You can install airportfinder using pip:

```python
pip install airportfinder


Usage

from airportfinder.airportfinder import Airports

# Create an instance of the Airports class
airports = Airports()

# Look up an airport by IATA code
airport = airports.airport_iata('LGA')
print(airport) # {'code': 'LGA', 'lat': '40.7731', 'lon': '-73.8756', 'name': 'LaGuardia Airport', 'city': 'Flushing', 'state': 'New York', 'country': 'United States', 'woeid': '12520509', 'tz': 'America/New_York', 'phone': '', 'type': 'Airports', 'email': '', 'url': '', 'runway_length': '7000', 'elev': '22', 'icao': 'KLGA', 'direct_flights': '82', 'carriers': '30'}

# Look up an airport by name
airport = airports.airport_name('LaGuardia Airport')
print(airport) # {'code': 'LGA', 'lat': '40.7731', 'lon': '-73.8756', 'name': 'LaGuardia Airport', 'city': 'Flushing', 'state': 'New York', 'country': 'United States', 'woeid': '12520509', 'tz': 'America/New_York', 'phone': '', 'type': 'Airports', 'email': '', 'url': '', 'runway_length': '7000', 'elev': '22', 'icao': 'KLGA', 'direct_flights': '82', 'carriers': '30'}
```

The airport_iata and airport_name methods return the airport object corresponding to the provided IATA code or name. If the airport is not found, it returns None.

Contributing
Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue on the GitHub repository.

License
This project is licensed under the BSD 3-Clause License. See the LICENSE.txt file for details.

Acknowledgments
This project uses airport data provided by Thomas Reynolds's "Airports" gist on GitHub: 
https://gist.github.com/tdreyno/4278655

We would like to thank Thomas for his contributions to the open-source community and for making this data available to us.