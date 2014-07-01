### How to use

1. Run `sqlite3 search_result.db < craigslist.sql` to initialize a SQLite3 database
2. Run `python craigslist.py` to populate the database with Craig's List RSS feed item. The code also copy `search_result.db` into `search_result.csv`
    * Modify parameters in `main()` in `craigslist.py` to fine tune your search
    * Options include multiple search terms, locations, type of listings, min/max price, etc.

### To do
1. Write to .csv instead of sqlite3 database (DONE)

### Credits

Modified from [Mike Roddewig](http://www.dietfig.org/craigslist.html)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License v3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>
