#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ARK DataRetriever

This program makes it easy to query several different sites maintained by the ARK: Survival Evolved community and store in-game related information in developer-friendly formats.
Please use it like you want, but please be fair and don't use it for resource-expensive things, since the community platforms aren't for software to query but for real humans enjoying the game.
Ah, and, of course, no warranty!

Usage:
python DataRetriever.py [--help]
(Please use the built-in help to get into the parameters!)

Current retrievable information:
- engrams
- more coming soon! or just add things by yourself on Github

Current data sources:
- Gamepedia Wiki (hopefully it is okay, if not just tell me)
"""

# imports
import sys
import argparse
import pprint
import importlib

# set module path
sys.path.append('./DataRetriever_modules')

__author__ = "Jon-Mailes 'Jonniboy' Gr"
__copyright__ = "Copyright 2017 - Jon-Mailes 'Jonniboy' Gr"
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Jon-Mailes Gr"
__email__ = "mail ät jonni pünktchen it"

# constants
NATIVE_DATASOURCES = ['gamepedia']

# variables
args = None
datasource = None
data = {}

def fetch_engrams():
    data['engrams'] = datasource.get_engrams()

def fetch_all():
    fetch_engrams()

def get_data(what = False):
    if what is not False:
        return data[what]
    return data

def output(format, file_name):
    if format == 'stdout':
        print('\nOutputting data to stdout now:\n')
        pprint.pprint(data)
        print("Output to stdout done! We're finished now.")
    else:
        if format == 'json_file':
            import json
            with open(file_name, 'w') as outfile:
                if args.prettify == 'true':
                    json.dump(data, outfile, indent=4)
                else:
                    json.dump(data, outfile)
                outfile.close()
        elif format == 'xml_file':
            if file_name == 'data.json':
                file_name = 'data.xml'
            from dicttoxml import dicttoxml
            import xml.dom.minidom
            with open(file_name, 'w') as outfile:
                if args.prettify == 'true':
                    outfile.write(xml.dom.minidom.parseString(dicttoxml(data, cdata=True)).toprettyxml())
                else:
                    outfile.write(dicttoxml(data))
                outfile.close()
        print('\nFinished with everything! Saved data to: ' + file_name)

def main():
    global datasource, args
    
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', help='Select one of the following sources: gamepedia (default)', default='gamepedia')
    parser.add_argument('--what', help='Sets the type of data which is going to be retrieved: all (default), engrams', default='all')
    parser.add_argument('--how', help='Sets the output format: json_file, xml_file, stdout (default)', default='stdout')
    parser.add_argument('--file', help='Sets the file name, if the output format is the file. Default: data.json/data.xml', default='data.json')
    parser.add_argument('--prettify', help='Should the output to file be prettified or as space-saving as possible? Default: false', default='false')
    args = parser.parse_args()
    
    print('')
    
    # import datasource
    if args.source in NATIVE_DATASOURCES:
        print("Data source:\t'" + args.source + "' (native)")
        datasource = importlib.import_module('datasource.gamepedia')
    else:
        print('No native data source module found! Trying to import foreign module...')
        
        try:
            datasource = importlib.import_module('datasource.' + args.source)
        except:
            raise ValueError("I don't know the given source. Sry!")
    
    # various information
    print('Output as:\t' + args.how)
    if args.how is not 'stdout':
        print('Save to file:\t' + args.file)
    
    # query data
    if args.what == 'all':
        print('Included data:\tengrams\n')
        print('Retrieving information...')
        fetch_all()
        print('Done! Fetched information.')
    elif args.what == 'engrams':
        print('Output will contain:\tengrams\n')
        print('Retrieving information...')
        fetch_engrams()
        print('Done! Fetched information.')
    
    # gift the gifts
    output(args.how, args.file)

if __name__ == '__main__':
    print(u'#################################################################')
    print(u'#                [Python] ARK DataRetriever tool                #')
    print(u'# (C) by Jon-Mailes "Jonniboy" Gr. (mail ät jonni pünktchen it) #')
    print(u'#################################################################')
    
    main()