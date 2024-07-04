# anobii2goodreads

Another script to convert a CSV export from the Anobii website
to a CSV similar to Goodreads export, which could be imported on Goodreads via
, or on [The StoryGraph](https://www.thestorygraph.com/) .

> [!WARNING]
> The script has been updated to have valid data structure as of **July 2024**.


_This is an updated and slightly modified version of [shaform/anobii2goodreads](https://github.com/shaform/anobii2goodreads),
which was in turn inspired by [tijs/Anobii2Goodreads](https://github.com/tijs/Anobii2Goodreads)._


## Usage

### 1. Get your Anobii data

Go on your Anobii profile and export your data as CSV. 

> [!NOTE]
> Sometimes Anobii seemingly exports encrypted CSVs that can't be dealt with, so you might need to export as `.xls` and then convert the file to `.csv`
Name the file however you want, but for this example we'll say the file is called `anobii.csv`

---

### 2. Convert

To convert `anobii.csv` to `anobii_converted.csv`, run the following command:

    python3 anobii2goodreads/anobii2goodreads.py [-l LANG] [-o] anobii.csv anobii_converted.csv

`anobii_converted.csv` can then be imported in Goodreads or The StoryGraph.

> [!TIP]
> As you may have noticed, it is possible to use optional flags as explained below:
> | Flags         | Options       | Description                                                                                      |
> |---------------|---------------|--------------------------------------------------------------------------------------------------|
> | `-l LANG`     | `en`, `zh-tw` | Language of the csv tables. Defaults to `en`.                                                    |
> | `-o`          |               | Keep only the ISBN, preventing Goodreads from auto-matching books that may have different ISBNs. |
> 
> For instance, running `python3 anobii2goodreads/anobii2goodreads.py -l zh-tw -o anobii.csv anobii_converted.csv` would tell the script to use a csv with taiwanese headings, and only export ISBN codes with no author and title data.

---

### 3. Import

#### Goodreads

Go on the Goodreads [import page](http://www.goodreads.com/review/import) and upload `anobii_converted.csv`

#### The StoryGraph

Go on [The StoryGraph](https://www.thestorygraph.com/), visit your Profile, navigate to Manage Account > Goodreads Import, and upload `anobii_converted.csv`

---

### 4. Add missing books (optional)

Sometimes, certain books may not be present in the Goodreads database, so you might accidentally be missing some books. 
In that case, go to the Goodreads [Import/Export](https://www.goodreads.com/review/import) page, and press the Export Library button to get a `goodreads_exported.csv` file.
You can then use `auto_add.py` to compare your original file `anobii_converted.csv` and `goodreads_exported.csv`, to add the non-imported books:

    python3 anobii2goodreads/auto_add.py -c COOKIE_JSON -a anobii_converted.csv -g goodreads_exported.csv

You'll need your session cookie from your browser to access Goodreads from `auto_add.py`.

However, reading progress is not entirely preserved in the process. But it's still possible to obtain complete reading history by directly crawling Anobii website:

    cd anobiicrawl/
    scrapy crawl progress -a visited=CACHE_PATH_FOR_CRAWL -a user=YOUR_USER_NAME -a login_path=anobii.login.json -o anobii_progress.jl

Afterwards, we could update the reading dates for books on Goodreads:

    cd ../
    python3 anobii2goodreads/update_date.py -c COOKIE_JSON -b anobiicrawl/anobii_progress.jl -d `CACHE_PATH_FOR_UPDATE`
