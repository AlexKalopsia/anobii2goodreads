"""Config file for anobii2goodreads.py

detect_strings: used to detect reading status
headers: CSV headers
"""

CONFIG = {
    'default_lang': 'en',
    'detect_strings': {
        'en': {
            'Not Started': 'Not Started',
            'Being read': 'Being read',
            'Unfinished': 'Unfinished',
            'Finished': 'Finished',
            'Reference': 'Reference',
            'Abandoned': 'Abandoned'
        },
        'zh-tw': {
            'Not Started': '還未開始',
            'Being read': '開始閱讀',
            'Unfinished': '開始還未完成',
            'Finished': '讀完',
            'Reference': '參考',
            'Abandoned': '捨棄'
        }
    },
    'headers': {
        'en': {
            'ISBN': 'ISBN',
            'Title': 'Title',
            'Subtitle': 'Subtitle',
            'Author': 'Author',
            'Format': 'Format',
            'Number of pages': 'Number of pages',
            'Publisher': 'Publisher',
            'Date of publication': 'Date of publication',
            'Private notes': 'Private notes',
            'Comment Title': 'Comment Title',
            'Comment Content': 'Comment Content',
            'Reading status': 'Reading status',
            'Vote': 'Vote',
            'Priority': 'Priority',
            'Tags': 'Tags'
        },
        'zh-tw': {
            'ISBN': 'ISBN',
            'Title': '書名',
            'Subtitle': '字幕',
            'Author': '作者',
            'Format': '裝訂規格',
            'Number of pages': '頁數',
            'Publisher': '出版者',
            'Date of publication': '出版日期',
            'Private notes': '私人筆記',
            'Comment Title': '評論標題',
            'Comment Content': '評論內容',
            'Reading status': '狀態',
            'Vote': '評等',
            'Priority': '優先順序',
            'Tags': '標籤',
        },
    }
}
