import feedparser
import urllib
import sys
import sqlite3
import time
import datetime
from lxml.html.clean import Cleaner

import unicode_csv as ucsv

import pdb

def rss_link_generator(locations, sublocations, search_terms, listings, price, \
    year, makes, title_status, has_pic):
    rss_links = []
    rss_generic_link = "http://%s.craigslist.org/search/%s/%s?query=%s" \
        "&minAsk=%s&maxAsk=%s&autoMinYear=%s&autoMaxYear=%s&autoMakeModel=%s" \
        "&auto_title_status=%s&hasPic=%s"

    for location in locations:
        for sublocation in sublocations:
            for listing in listings:
                for make in makes:
                    if len(search_terms) != 0:
                        for term in search_terms:
                            term = urllib.quote(term)
                            rss_link = rss_generic_link % (location, sublocation, listing, 
                                                        term, price[0], price[1], year[0], 
                                                        year[1], make, title_status, has_pic)
                    else:
                        rss_link = rss_generic_link % (location, sublocation, listing, "", price[0], 
                                                        price[1], year[0], year[1], make, 
                                                        title_status, has_pic)
                    rss_link = rss_link + "&format=rss"
                    rss_links.append(rss_link)

    return rss_links

def enter_data(db_cursor, url, sublocation, title, text, update_time):
    db_cursor.execute("SELECT last_update FROM listings WHERE title = ?", (title,))

    if db_cursor.fetchone() == None: # Meaning that this tile does not exist yet
        db_cursor.execute('''
            INSERT INTO listings
            (url, sublocation, title, text, last_update, new, found)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (url, sublocation, title, text, update_time, 1, update_time) 
            )
    else: # If this title exists then update the update_time
        db_cursor.execute('''
            UPDATE listings
            SET last_update = ?
            WHERE title = ?''',
            (update_time, title)
            )

def retrieve_and_enter_data(db_cursor, rss_links, update_time):
    cleaner = Cleaner(remove_unknown_tags=False, allow_tags=['img', 'p', 'a', 'b', 'em', 'div']);

    for rss_link in rss_links:
        listings = feedparser.parse(rss_link)
        
        for listing in listings.entries:
            # pdb.set_trace()
            title = listing["title"]
            url = listing["link"]
            sublocation = listing["link"].split("/")[3] # This is code like doc, nva
            text = cleaner.clean_html(listing["description"])
            
        enter_data(db_cursor, url, sublocation, title, text, update_time)

def clean_expired_entries(db_cursor, update_time):
    db_cursor.execute("""
    DELETE FROM listings
    WHERE last_update != ?
    """,
    (update_time,)
    )

def main():
    # When this operation starts
    update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    ### Search Parameters ###
    locations = ["washingtondc"]
    sublocations = ["doc", "nva", "mld"]
    search_terms = []
    listings = ["cta"] # cta is the listing for cars and trucks
    price = [3000, 5000] # min and max price
    year = [2004, 2010] # min and max year
    makes = ["honda", "toyota", "hyundai"]
    title_status = 1 # Clean title
    has_pic = 1 # has pic

    ### Database Information ###
    csv_file = "search_result.csv"
    db_file = "search_result.db"
    
    # Database connection
    db = sqlite3.connect(db_file)
    db_cursor = db.cursor()

    # Retrieve and parse rss
    rss_links = rss_link_generator(locations, sublocations, search_terms, listings, \
                                price, year, makes, title_status, has_pic)
    retrieve_and_enter_data(db_cursor, rss_links, update_time)

    # Uncomment this line to clean existing entries from the database
    # clean_expired_entries(db_cursor, update_time)

    # Commit the change to sqlite database
    db.commit()
    
    # pdb.set_trace()
    # Convert the sqlite3 database to csv
    db_cursor.execute('SELECT * FROM listings')
    with open("search_result.csv", "wb") as f:
        csv_writer = ucsv.UnicodeWriter(f)
        csv_writer.writerow([i[0] for i in db_cursor.description]) # Write the header
        csv_writer.writerows(db_cursor)

    # Close the database
    db.close()

if __name__ == '__main__':
    main()