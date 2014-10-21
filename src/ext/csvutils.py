# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import csv, logging

def process_csv_line(line, pack_size=None):
#    logging.debug("type(): %s" % type(line))
    if isinstance(line, unicode):
        line = line.encode('utf-8')
    pack = [s.decode('utf-8').strip() for s in csv.reader((line,), delimiter=';').next()]

    if not pack_size:
        return pack
    size = len(pack)
    if size < pack_size:
        for i in range(pack_size - size):
            pack.append(None)
    return pack[:pack_size]


def encode_csv_text(unicode_csv_text):
    for line in unicode_csv_text:
        yield line.encode('utf-8')


def decode_csv_data(csv_reader):
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

