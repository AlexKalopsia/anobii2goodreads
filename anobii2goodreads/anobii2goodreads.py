#!/usr/bin/env python3
"""Convert Anobii CSV to Goodreads CSV."""
import argparse
import csv
import logging
import re

import pyisbn
from config import CONFIG


class Anobii2GoodReads(object):
    """Convert Anobii CSV to Goodreads CSV."""

    OUTPUT_HEADERS = ['Book Id', 'Title', 'Author', 'Author l-f', 'Additional Authors',
                      'ISBN', 'ISBN13', 'My Rating', 'Average Rating', 'Publisher',
                      'Binding', 'Number of Pages', 'Year Published',
                      'Original Publication Year', 'Date Read', 'Date Added',
                      'Bookshelves', 'Bookshelves with positions', 'Exclusive Shelf',
                      'My Review', 'Spoiler', 'Private Notes', 'Read Count',
                      'Owned Copies']

    @staticmethod
    def _convert_linebreak(line):
        """Convert linkbreak in aNobii to HTML <br> tags."""
        if line:
            return line.replace('\r\n', '\n').replace('\n', '<br>')
        else:
            return None


    @staticmethod
    def _convert_comment(title, content):
        if content:
            content = Anobii2GoodReads._convert_linebreak(content)
            if title:
                logging.debug('convert comment for %s', title)
                content = '<p><b>{}</b></p>{}'.format(title.strip(), content)
            return content
        else:
            return None

    @staticmethod
    def _parse_status(status):
        text = status[:-10].rstrip()
        date = status[-10:].replace('-','/')
        return text, date

    @staticmethod
    def _convert_date(status):
        nochinese = re.sub(u'[⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]',
                           '',
                           status,
                           flags=re.UNICODE)
        tokens = re.split(r'[，, ]+', nochinese)
        year, month, day = None, 1, 1

        if len(tokens[-1]) == 4 and tokens[-1].isdigit():
            year = tokens[-1]
            if len(tokens) > 1:
                temp = tokens[-2]
                if temp.isdigit():
                    day = temp
                    if len(tokens) > 2:
                        temp = tokens[-3]
                month = {
                    'Jan': 1,
                    'Feb': 2,
                    'Mar': 3,
                    'Apr': 4,
                    'May': 5,
                    'Jun': 6,
                    'Jul': 7,
                    'Aug': 8,
                    'Sep': 9,
                    'Oct': 10,
                    'Nov': 11,
                    'Dec': 12
                }.get(temp[:3], month)
            return '{}/{}/{}'.format(year, month, day)
        return None

    def _detect_status(self, date, text):
        date_read, date_added = None, None
        bookshelves = []

        if self.detect_strings['Not Started'] in text:
            bookshelves = ['to-read']
        elif self.detect_strings['Being read'] in text:
            bookshelves.append('currently-reading')
            date_added = date
        elif self.detect_strings['Unfinished'] in text:
            bookshelves = ['unfinished']
            date_added = date
        elif self.detect_strings['Finished'] in text:
            bookshelves = ['read']
            date_read = date
        elif self.detect_strings['Reference'] in text:
            bookshelves = ['reference']
            date_added = date
        elif self.detect_strings['Abandoned'] in text:
            bookshelves = ['abandoned']
            date_added = date

        return date_read, date_added, bookshelves

    def _convert_status(self, status, tags):
        if status:
            date = self._convert_date(status)
            if tags is not None:
                tag_items = {tag.strip() for tag in tags.split('/')}
            else:
                tag_items = set()
            if any(shelve_title in tag_items
                   for shelve_title in self.detect_strings.values()):
                return self._detect_status(date, tag_items)

            else:
                return self._detect_status(date, status)
        else:
            return None, None, ['to-read']

    def convert_entry(self, entry):
        ISBN, TITLE, SUBTITLE = 'ISBN', 'Title', 'Subtitle' 
        AUTHOR, FORMAT = 'Author', 'Format'

        NUM_OF_PAGES, PRIVATE_NOTES = 'Number of pages', 'Private notes'
        PUBLISHER, PUB_DATE = 'Publisher', 'Date of publication'

        COMMENT_TITLE, COMMENT_CONTENT = 'Comment Title', 'Comment Content'
        STATUS, VOTE = 'Reading status', 'Vote'

        TAGS = 'Tags'

        ISBN = self.headers[ISBN]
        TITLE = self.headers[TITLE]
        SUBTITLE = self.headers[SUBTITLE]
        AUTHOR = self.headers[AUTHOR]
        FORMAT = self.headers[FORMAT]
        NUM_OF_PAGES = self.headers[NUM_OF_PAGES]
        PUBLISHER = self.headers[PUBLISHER]
        PUB_DATE = self.headers[PUB_DATE]
        PRIVATE_NOTES = self.headers[PRIVATE_NOTES]
        COMMENT_TITLE = self.headers[COMMENT_TITLE]
        COMMENT_CONTENT = self.headers[COMMENT_CONTENT]
        STATUS = self.headers[STATUS]
        VOTE = self.headers[VOTE]
        TAGS = self.headers[TAGS]

        title = entry.get(TITLE)

        author, author_lf, additional_authors = None, '', None
        if AUTHOR in entry:
            all_authors = list(map(str.strip, entry[AUTHOR].split(',')))
            if len(all_authors) > 0:
                author = all_authors[0]
            if len(all_authors) > 1:
                additional_authors = ', '.join(all_authors[1:])

        book_id = ''
        isbn = entry.get(ISBN)
        isbn13 = None
        isbn10 = None

        if (isbn):
            if len(isbn) == 10:
                isbn10 = isbn
                try:
                    isbn13 = pyisbn.convert(isbn10)
                except pyisbn.IsbnError:
                    # ignore inconvertible ISBNs
                    pass
            elif len(isbn) == 13:
                isbn13 = isbn
                try:
                    isbn10 = pyisbn.convert(isbn13)
                except pyisbn.IsbnError:
                    # ignore inconvertible ISBNs
                    pass
            logging.warning(isbn10)

        publisher = entry.get(PUBLISHER)
        binding = entry.get(FORMAT)
        num_of_pages = entry.get(NUM_OF_PAGES)

        year_published = entry.get(PUB_DATE)
        if year_published:
            year_published = year_published.replace('-', '/').replace('xx','01')
        original_year_published = ''

        private_notes = self._convert_linebreak(entry.get(PRIVATE_NOTES))

        my_rating = entry.get(VOTE)
        avg_rating = ''
        my_review = self._convert_comment(
            entry.get(COMMENT_TITLE), entry.get(COMMENT_CONTENT))

        spoiler = ''
        tags = entry.get(TAGS)
        status = entry.get(STATUS)
        date_read, date_added, bookshelves = self._convert_status(status,
                                                                    tags)
        bookshelves_w_pos = ''
        exclusive_shelf = ''

        if len(bookshelves) == 0:
            logging.warning('cannot parse %s: %s', title, status)
        elif len(bookshelves) == 1:
            exclusive_shelf = bookshelves[0]

        read_count = 0 if exclusive_shelf == 'to-read' else 1
        owned_copies = 0 if exclusive_shelf == 'to-read' else 1

        if self.only_isbn:
            book_id = ''
            title = ''
            author = ''
            author_lf = ''
            additional_authors = ''
            publisher = ''
            binding = ''
            num_of_pages = ''
            year_published = ''
            original_year_published = ''

        return (book_id, title, author, author_lf, additional_authors, isbn10, isbn13,
                my_rating, avg_rating, publisher, binding, num_of_pages, year_published,
                original_year_published, date_read, date_added, ','.join(bookshelves),
                bookshelves_w_pos, exclusive_shelf, my_review, spoiler, private_notes,
                read_count, owned_copies)

    def __init__(self, *, detect_strings, headers, only_isbn):
        self.detect_strings = detect_strings
        self.headers = headers
        self.only_isbn = only_isbn


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert aNobii csv to GoodReads csv.')
    # parser.add_argument('-w', dest='wishlist', action='store_true',
    #                     help='Process a wish list.')
    parser.add_argument('-l',
                        dest='lang',
                        default=CONFIG['default_lang'],
                        choices=tuple(CONFIG['detect_strings']),
                        help='Input language.')
    parser.add_argument('-o',
                        '--only-isbn',
                        action='store_true',
                        help='Keep only ISBN, discard book info.')
    parser.add_argument('input_file',
                        metavar='anobii_csv',
                        help='aNobii CSV file')
    parser.add_argument('output_file',
                        metavar='goodreads_csv',
                        help='GreedReads CSV file export path')
    return parser.parse_args()


def main():
    """Convert Anobii CSV to Goodreads CSV."""
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    with open(args.input_file, newline='',
              encoding='utf8') as anobii_csv, open(
                  args.output_file,
                  'w', newline='',
                  encoding='utf8') as goodread_csv:
        anobii_reader = csv.DictReader(anobii_csv)
        goodreads_writer = csv.writer(goodread_csv)
        a2g = Anobii2GoodReads(
            detect_strings=CONFIG['detect_strings'][args.lang],
            headers=CONFIG['headers'][args.lang], only_isbn=args.only_isbn)

        not_convertable = []
        goodreads_writer.writerow(a2g.OUTPUT_HEADERS)
        for entry in anobii_reader:
            isbn = entry.get('ISBN')
            # Skip book with no ISBN provided
            if not isbn:
                not_convertable.append(entry)
                continue

            goodreads_writer.writerow(a2g.convert_entry(entry))

        logging.info('Conversion done.')
        if len(not_convertable) > 0:
            logging.warning('%d entries not convertable.',
                            len(not_convertable))
            for entry in not_convertable:
                logging.warning('%s by %s', entry[a2g.headers['Title']],
                                entry[a2g.headers['Author']])


if __name__ == '__main__':
    main()
