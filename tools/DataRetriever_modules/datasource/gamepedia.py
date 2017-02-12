from bs4 import BeautifulSoup
import urllib2
import re

# constants
GAMEPEDIA_URLS = {"engrams": "http://ark.gamepedia.com/Engrams"}
GAMEPEDIA_CHECKSUMS = {"engrams": 38}
GAMEPEDIA_AGENT_FAKE = ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")

def _get_parse_url(url):
    opener = urllib2.build_opener()
    opener.addheaders = [GAMEPEDIA_AGENT_FAKE]
    response = opener.open(url)
    data = response.read()
    return BeautifulSoup(data, "html.parser")

def _parse_tekgram_table(table):
    
    data = []
    last_item = None
    rowspan = 1

    # iterate through all rows
    for row in table.find_all("tr"):

        # table header? no? ok!
        if "Item" not in str(row) and "Tek Engrams" not in str(row):
            
            # get all columns
            tds = row.find_all("td")
            
            # if we"ve finished an item, save it
            if rowspan == 0:
                data.append(last_item)
                # ... and overwrite the old one
                last_item = None
            
            #print tds[0]
            # do we expect multiple rows for one item?
            if tds[0].has_attr("rowspan"):
                rowspan = int(tds[0]["rowspan"])
            else:
                rowspan = 1
            
            # save the results into the last item, but if no last item is there, we may 
            if last_item is None:
                # check if this is an entry with links, then we need to get the second a element to get the name beneath the linked boss icon
                if len(tds[1].find_all("a")) > 1:
                    last_item = {"item": tds[0].find_all("a")[1].string, "bosses": [{"name": tds[1].find_all("a")[1].string, "min_difficulty": tds[2].string, "arena_level_requirement": int(re.search(r"\d+", str(tds[3])).group())}]}
                else:
                    last_item = {"item": tds[0].find_all("a")[1].string, "bosses": [{"name": tds[1].string, "min_difficulty": tds[2].string, "arena_level_requirement": int(re.search(r"\d+", str(tds[3])).group())}]}
            else:
                if len(tds[0].find_all("a")) > 1:
                    last_item["bosses"].append({"name": tds[0].find_all("a")[1].string, "min_difficulty": tds[1].string, "arena_level_requirement": int(re.search(r"\d+", str(tds[2])).group())})
                else:
                    last_item["bosses"].append({"name": tds[0].string, "min_difficulty": tds[1].string, "arena_level_requirement": int(re.search(r"\d+", str(tds[2])).group())})
                
            rowspan -= 1
        
    return data

def get_engrams():
    soup = _get_parse_url(GAMEPEDIA_URLS["engrams"])
    data = {"vanilla": [], "tekgrams": [], "dlc_scorched_earth": []}
    current_section = "vanilla"
    
    wikitables = soup.find_all("table", {"class": "wikitable"})

    # iterate over all tables in HTML code with class "wikitable"
    for table in wikitables:

        # if there is no "Required level bla bla bla", and no caption caused by the missing headline, we won"t continue, except it is the tekgram table
        if table.caption is None:
        
            # ah sh*t waaaait, we"ve the tekgram table - and it"s different than the other tables... let"s do that in an external function
            if "Tekgrams" in str(table.tr):
                data["tekgrams"] = _parse_tekgram_table(table)
                x = True
                # lets go to the next table, but now we"ve the DLC section - don"t forget!
                current_section = "dlc_scorched_earth"
                continue
            else:
                break
        
        # get the required level to learn the engram from the caption
        # -> there was one table with no content, but it gets parsed so I just make a None check
        if re.search(r"\d+", table.caption.i.b.string) is not None:
            required_level = int(re.search(r"\d+", table.caption.i.b.string).group())
        else:
            required_level = 0
        
        # iterate through all table rows
        for row in table.find_all("tr"):
        
            # get all columns
            tds = row.find_all("td")
            
            #print str(tds[0]) + "\n-----------\n"
            # if it"s the table head (Icon, Engram Name, ...), we skip
            if "Icon" not in str(tds[0]):

                # new engram
                new = {}
                new["icon"] = tds[0].a.img["src"]
                new["name"] = tds[1].a["title"]
                
                # if engram needs ep (starter don"t need any EP obviously)
                #print str(tds[2])
                if "-" in str(tds[2]):
                    new["ep_to_unlock"] = 0
                else:
                    new["ep_to_unlock"] = int(re.search(r"\d+", str(tds[2])).group())
            
                # add our new engram definition to the engram list
                data[current_section].append(new)

    return data
