# Make the necessary imports
from __future__ import print_function
import argparse
import json
import pprint
import requests
import sys
import csv                                     # For persisting the ReST API results into a CSV file

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

# Scraping Strategy: 
# To fetch data from the Yelp Website, we use their Yelp Fusion API [https://www.yelp.com/developers/documentation/v3]
# which offers us plethora of business endpoints 

# Credentials - Yelp doesnt use OAuth
# We therefore do not have to provide ClientID to fetch data. 
# Yelp uses private keys (API Keys) to authenticate requests. 
# Reference: https://www.yelp.com/developers/v3/manage_app
#            https://www.yelp.com/developers/documentation/v3/get_started
# To get an API_KEY and the ClientID, you need to register and log into the Yelp Website and 'Create an App'. 
# Yelp offers myriad of open source resources for developers [Refer: https://www.yelp.com/developers]

API_KEY= 'YOUR_API_KEY'
API_HOST = 'https://api.yelp.com'
SEARCH_BIZ_URI = '/v3/businesses/search'
SPECIFIC_BIZ_CONTENT_URI = '/v3/businesses/'    # Business ID of specific business will come after the slash


# Example 1
DEFAULT_SEARCH_TERM = 'Restaurant'
DEFAULT_SEARCH_LOC = "1111 NE LOOP 410, SAN ANTONIO, TX 78209"
#"350 5th Ave, New York, NY 10118"
#2613 S LAMAR BLVD, Austin, TX 78681
SEARCH_LIMIT = 50                               # Upper limit. An increase beyond this limit, renders the API non-functional [Default = 20] and results into
                                                # VALIDATION ERROR. Limit + Offset <= 1000.
                                                
def request(host, path, api_key, url_params=None):
    '''
        Obj: Make the actual ReST API Call
    '''
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
                  'Authorization': 'Bearer %s' % api_key,
              }
    response = requests.request('GET', url, headers = headers, params = url_params)
    return response.json()


def search(api_key, search_term, search_location):
    '''
        Obj: Search specific biz at specific location
    '''
    # Stitch the URL params
   
    url_params = {'term': search_term.replace(' ', '+'),
                  'location': search_location.replace(' ','+'),
                  'limit': SEARCH_LIMIT,
                  'offset': 950}
   
    print("url_params:--->", url_params)
    return request(API_HOST, SEARCH_BIZ_URI, api_key, url_params=url_params)


def query_api(term, location):
    '''
        Obj: Call appropriate REST API's and supply them with user inputs.
    '''
    response = search(API_KEY, term, location)
    #print("response:----->", response)
    #print("type(response):----->", type(response))      # Its a <dict>

    # For printing along with indentation
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(response)
                        
    biz = response.get('businesses')        
    #print("biz:------>", biz)
    #print('type(biz):------>', type(biz))     # Returns a <list>
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")
    

    if not(biz):
        print("No businesses found for {0} in {1}.".format(term, location))
        return
    return biz


def persistResult(result):
    '''
        Obj: To persist the ReST API response, into a CSV file
    '''
    print("Total # of search results:---->", len(result))    # Total list of 50 restaurants returned [Limitation of the Yelp Fusion API]
    # Print a single record from within the search result
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(result[0])

    # Open a CSV file to persist the search results
    with open('Yelp_Search_Businesses.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(['Business_Alias', 'Business_ID', 'Business_Name', 'Category_Alias', 'Category_Title', 'Latitude', 'Longitude', 'Display_Phone', 'Phone',\
                        'Distance','Image_URL', 'Is_Closed', 'Address_Line1', 'Address_Line2', 'Address_Line3', 'City', 'State', 'Country', 'ZipCode', 'Rating',\
                        'Review_Count', 'Transactions', 'Business_URL'])
        
        # Iterate through the search results and fetch the desired data.
        for i in range(len(result)):
            tAlias = result[i]['alias'].encode('utf-8').strip()
            tCategoryAlias = result[i]['categories'][0]['alias'].encode('utf-8').strip()
            tCategoryTitle = result[i]['categories'][0]['title'].encode('utf-8').strip()
            tLatitude = result[i]['coordinates']['latitude']
            tLongitude = result[i]['coordinates']['longitude']
            tDisplayPhone = result[i]['display_phone'].encode('utf-8').strip()
            tDistance = result[i]['distance']
            tBizID = result[i]['id'].encode('utf-8').strip()
            tImageURL = result[i]['image_url'].encode('utf-8').strip()
            tIsClosed = result[i]['is_closed']
            tLocationAddrLin1 = result[i]['location']['address1']
            tLocationAddrLin2 = result[i]['location']['address2']
            tLocationAddrLin3 = result[i]['location']['address3']
            tCity = result[i]['location']['city'].encode('utf-8').strip()
            tState = result[i]['location']['state'].encode('utf-8').strip()
            tCountry = result[i]['location']['country'].encode('utf-8').strip()
            tZipCode = result[i]['location']['zip_code'].encode('utf-8').strip()
            tName = result[i]['name'].encode('utf-8').strip()
            tPhone = result[i]['phone'].encode('utf-8').strip()
            tRating = result[i]['rating']
            tReviewCount = result[i]['review_count']
            tTransactions = result[i]['transactions']
            tURL = result[i]['url'].encode('utf-8').strip()
            #print(tAlias, tCategoryAlias, tCategoryTitle, tLatitude, tLongitude, tDisplayPhone, tDistance, tBizID, tImageURL, tIsClosed,\
            #      tLocationAddrLin1, tLocationAddrLin2, tLocationAddrLin3, tCity, tState, tCountry, tZipCode, tName, tPhone, tRating, tReviewCount,\
            #      tTransactions, tURL)
            writer.writerow([tAlias, tBizID, tName, tCategoryAlias, tCategoryTitle, tLatitude, tLongitude, tDisplayPhone, tPhone, tDistance, tImageURL,\
                             tIsClosed, tLocationAddrLin1, tLocationAddrLin2, tLocationAddrLin3, tCity, tState, tCountry, tZipCode, tRating, tReviewCount,\
                             tTransactions, tURL])

def main():
    '''
        Using Argparse: 
        ---------------
        add_argument() is used to specify which command-line options the program is willing to accept.
        argparse treats the options we give it as strings, unless we tell it otherwise.To tell argparse to treat that 
        input as an integer, specifically use the 'type=int' argument.
        
        Sample usage of the program:
        ---------------------------
        C:\> python 1_YelpScrape.py --term="bars" --location="San Francisco, CA"`
    '''
    # Read the command line arguments
    parser = argparse.ArgumentParser(description = "Calling Yelp Fusion APIs")

    parser.add_argument('-t',                                 # Short version of the switch                  
                        '--term',                             # Long version of the switch
                        dest = 'term',                        # The way you would access this value in the program 
                        default = DEFAULT_SEARCH_TERM,        # The default value provided 
                        type = str,
                        help = 'Enter Search Term (default: %(default)s)')
    
    parser.add_argument('-l', 
                        '--location', 
                        dest = 'location', 
                        default = DEFAULT_SEARCH_LOC, 
                        type  = str, 
                        help = 'Enter Search Location (default: %(default)s)')

    input_values = parser.parse_args()
    print("input_values:-------------->", input_values)
    print("input_values.term:-------------->", input_values.term)
    print("input_values.location:-------------->", input_values.location)
    
    try:
        # Supply the user inputs and call appropriate REST API handles.
        result = query_api(input_values.term, input_values.location)
        persistResult(result)
    except HTTPError as error:
        sys.exit(
                'Encountered HTTP Error {0} on {1}:\n {2}\n Abort program...'. format(
                    error.code, error.url, error.read()))
    
if __name__ == '__main__':
    main()
