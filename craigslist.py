import feedparser
import urllib
import sys
import sqlite3
import time
import datetime
from lxml.html.clean import Cleaner

import pdb



# Generate the RSS links

def rss_link_generator(locations, search_terms, listings, price, year, makes, title_status, has_pic):
    rss_links = []
    rss_generic_link = "http://%s.craigslist.org/search/%s?query=%s" \
        "&minAsk=%s&maxAsk=%s&autoMinYear=%s&autoMaxYear=%s&autoMakeModel=%s" \
        "&auto_title_status=%s&hasPic=%s"

    for location in locations:
        for listing in listings:
            for make in makes:
                if len(search_terms) != 0:
                    for term in search_terms:
                        term = urllib.quote(term)
                        rss_link = rss_generic_link % (location, listing, 
                                                    term, price[0], price[1], year[0], 
                                                    year[1], make, title_status, has_pic)
                        rss_link = rss_link + "&format=rss"
                        rss_links.append(rss_link)
                else:
                    rss_link = rss_generic_link % (location, listing, "", price[0], 
                                                    price[1], year[0], year[1], make, 
                                                    title_status, has_pic)
                    rss_link = rss_link + "&format=rss"
                    rss_links.append(rss_link)

    return rss_links


def retrieve_and_enter_data(db_cursor, update_time, rss_links):
    cleaner = Cleaner(remove_unknown_tags=False, allow_tags=['img', 'p', 'a', 'b', 'em', 'div']);

    for rss_link in rss_links:
        listings = feedparser.parse(rss_link)
        
        for listing in listings.entries:
            
            title = listing["title"]
            url = listing["link"]
            text = cleaner.clean_html(listing["description"])
            
            db_cursor.execute("""SELECT last_update FROM listings WHERE title = ?""", (title,))

            if db_cursor.fetchone() == None:
                db_cursor.execute("""
                    INSERT INTO listings 
                    (url, title, text, last_update, new, found) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (url, title, text, update_time, 1, update_time,)
                )
            else:
                db_cursor.execute("""
                    UPDATE listings
                    SET last_update = ?
                    WHERE title = ?
                    """,
                    (update_time, title,)
                )

def clean_expired_entries(db_cursor, update_time):
    db_cursor.execute("""
    DELETE FROM listings
    WHERE last_update != ?
    """,
    (update_time,)
    )    


def main():
    ### Search Parameters ###
    locations = ["washingtondc", "richmond"]
    search_terms = []
    listings = ["cta"] # cta is the listing for cars and trucks
    price = [3000, 5000] # min and max price
    year = [2004, 2010] # min and max year
    makes = ["honda", "hyundai"]
    title_status = 1 # Clean title
    has_pic = 1 # has pic

    ### Database Information ###
    db_file = "var/db/craigslist.db"
    update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Initialization
    db = sqlite3.connect(db_file)
    db_cursor = db.cursor()

    # Retrieve and parse rss

    rss_links = rss_link_generator(locations, search_terms, listings, \
                                price, year, makes, title_status, has_pic)

    retrieve_and_enter_data(db_cursor, update_time, rss_links)


    # Uncomment this line to clean existing entries from the database
    # clean_expired_entries(db_cursor, update_time)

    
    db.commit()
    db.close()


if __name__ == '__main__':
    main()