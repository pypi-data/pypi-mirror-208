#lexisnexisapi

##About lexisnexisapi:
lexisnexisapi is a module designed to work with certain LexisNexis DAAS APIs.  
Currently, this module only works with the Metabase API, and requires a Metabase API key.
the Metabase module within lexisnexisapi creates an instance of the MbSearch class based on a query 
provided by the end user.  It takes the JSON response from the Metabase API and places it within a 
Python class.  
It is also possible to create an instance of a class for a specific article, to simplify further analysis.
This class can retrieve dataframes, index terms, or any other
attributes retrieved from the API HTTP response.
The lexisnexisapi is a work in progress... and may not be regularly maintained. 

##Requirements
Beyond system requirements, lexisnexisapi requires an active Metabase API key.
#Required modules
##Configuration
##Troubleshooting & FAQ 
lexisnexisapi has limited built-in error handling and should be considered a beta module.  There
is no guarantee that lexisnexisapi will work in all environments.
##Maintainers
This module is not regularly maintained.  It was written and is updated by the
customer service integration specialist within the DAAS customer success team at 
LexisNexis.  It is not, however, a regularly maintained product, and LexisNexis makes 
no representation as to its safety or effectiveness.
