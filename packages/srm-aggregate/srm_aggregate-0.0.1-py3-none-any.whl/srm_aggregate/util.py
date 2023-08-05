import datetime as dt
import json
from pathlib import Path
import re

import pandas as pd


p_filename = re.compile(r'PCO(?P<subject>\d{3})_(?P<visit>\d{3})_\d{3}_SR2(?P<condition>\w+)(?P<date>(_\d{2}){6})')


def parse_filename(filename):
    file_info = p_filename.match(filename.stem).groupdict()
    file_info['date'] = dt.datetime.strptime(file_info['date'], '_%y_%m_%d_%H_%M_%S')
    return file_info


def load_file(filename):
    filename = Path(filename)
    with filename.open() as fh:
        header = json.loads(fh.readline())
        data = pd.read_csv(fh, sep='|', header=None, index_col=0)
    return header, data


def _aggregate_file(filename):
    file_info = parse_filename(filename)
    _, data = load_file(filename)
    n_re = len(re.findall('True', filename.read_text()))
    n_pd = data.loc[:, 5].sum()
    file_info['averaged_tmr'] = 10 - data.loc[:, 5].sum()
    return file_info


def aggregate(files):
    bgc_files = []
    for filename in files:
        if filename.suffix == '.bgc':
            bgc_files.append(filename)
        else:
            bgc_files.extend(filename.glob('**/*.bgc'))
    bgc_files = set(bgc_files)

    results = []
    errors = []
    for bgc_file in bgc_files:
        try:
            results.append(_aggregate_file(bgc_file))
        except Exception as e:
            mesg = f'Error processing {bgc_file.stem}: {e}'
            errors.append(mesg)
    results = pd.DataFrame(results) \
        .sort_values(['subject', 'visit']) \
        .reset_index(drop=True)
    return results, errors
