# rfin_scraper
a scraper for basic property info on the MLS

This can be installed into a project using pip install finny_scrapper in a Python project

A new instance of a property class must be created and a redfin url must be passed as the only argument.

The accessible methods are:

get_property_image() - returns the first image in the property listing as a string
get_listing_price() - returns an integer of the current listed property price
get_property_type() - returns a string that will be something like "Single Family" or "Multifamily (2-4)" or "C, (2-4)," etc.
get_number_of_units() - returns an integer of units on the property. Single Family = 1, Duplex = 2. There are some bugs with condos
get_property_info() - return an object with all of the above info in a dictionary
