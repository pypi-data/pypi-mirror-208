

#TODO:
#    Make a local-alignment based clustering algorithm that
#    1.  Splits the sequences into smaller non-homogenous groups
#    2.  Aligns the sequences and tries to establish clear clusters
#        - Either via length checking or motif checking
#        - Maybe compare k-mers? I dunno.



from Bio.Blast import NCBIXML
from Bio.Blast import NCBIWWW
import xml.etree.ElementTree as ET
from Bio import Entrez
import gzip
import bz2
import math
import time
import os
import re
import io


from cluseek import dframe

import subprocess

#Debug
from collections import Counter

#Debug2
import code
#code.interact(local=locals())

#TODO: Set user's email, and config the sleep between tries
#NOTE: When downloading neighbourhoods, a failure results in waiting 340s
#      although the average time to download a gb is at most 2s 
#      (at least on this machine)
#      (Why are we waiting this long? It's kind of inconvenient.)
Entrez.email = "hrebiceo@gmail.com"
Entrez.sleep_between_tries=15

#For UI interactions, override this if necessary.

def verify_folder():
    if not os.path.isdir(os.path.join(os.getcwd(), "data")):
        os.mkdir(os.path.join(os.getcwd(), "data"))
verify_folder()
class DummyDownloadManager():
    def __init__(self):
        pass
    def download_starting(self, type, number_to_download):
        # type = What kind of data is being downloaded. 
        #        Valid so far: "IPG", "GB"
        # number_to_download = number of entries present locally,
        #                       which will need to be downloaded
        # False = Download is OK, proceed
        # True = Do not start download
        return False
    def download_status(self, number_left_to_download):
        # Same as before, but interrupts download.
        return False
    def download_ended(self):
        pass
DOWNLOAD_MANAGER = DummyDownloadManager()
#
class ManagerIPG():
    def __init__(self, dbpath, overwrite=False, verbose=True, offline=False):
        super().__init__()
        self.path = dbpath
        # Check if the dbfile exists, or if we're overwriting it anyway,
        # and if so, create a new dbfile.
        if overwrite or not os.path.isfile(dbpath):
            with open(dbpath, mode="w") as file:
                file.close()
        self.file = open(dbpath, mode="a+")
        self.indices = {}
        self.lastadded = None
        self.temppath = "./data/temp_ipgdownload.xml.gz"
        self.verbose = verbose
        self.offline = offline
        #A list of accessions that NCBI simply won't return
        #   so we don't keep bouncing them off of the server
        #   in the same session.
        
        #Leave this as last:
        self.index_file()
        
    def index_file(self):
        debug_t0 = time.time()
        #creates a dictionary of {str protein_accession: int position_in_index}
        #to allow
        # a) checking which proteins are already in the db
        # b) quickly obtaining required data on demand
        self.indices = {}
        #find the end of the file, then go back to start
        fileend = self.file.seek(0, os.SEEK_END)
        self.file.seek(0)
        #read the position of the stream just before it reads the next entry
        linestart = self.file.tell()
        while linestart != fileend:
            line = self.parse_line(self.file.readline())
            if line["ptacc"] not in self.indices:
                self.indices[line["ptacc"]] = []
            self.indices[line["ptacc"]].append(linestart)
            #read the position of the stream just before it reads the next entry
            linestart = self.file.tell()
        debug_t1 = time.time()
        print(f"Indexing IPG databse took {debug_t1 - debug_t0} seconds.")
    def add_entry(self, entrydict):
        #entry must be a dictionary in a format
        # * Check if ID is already in db
        if entrydict["ptacc"] != self.lastadded \
          and entrydict["ptacc"] in self.indices:
            return(False)
        # * Write the actual entry
        entries = []
        #save the time this entry was added in time since epoch
        #  so we can remove entries that are too old if needed
        entrydict["added"] = time.time()
        for key in entrydict:
            value = entrydict[key]
            if type(value) is str:
                #NOTE: We need to replace any | characters.
                # It'd be fine if the parser could
                #   ignore special characters within "" quotes,
                #   but it doesn't.
                # I'm gambling that keys do not contain pipes.
                value = f"\"{value}\""
            elif type(value) is int or type(value) is float:
                pass
            elif type(value) is tuple:
                value = f"\"{', '.join([str(x) for x in value])}\""
            elif value is None:
                value = "\"N/A\""
            if type(value) is str:
                value = value.replace('|','')
            entries.append(f"{key}|{value}")
        self.file.seek(0, os.SEEK_END) #Explicitly seek the end
        #write down the index
        if entrydict["ptacc"] not in self.indices:
            self.indices[entrydict["ptacc"]] = []
        self.indices[entrydict["ptacc"]].append(self.file.tell()) 
        self.file.write("\t".join(entries))
        self.file.write("\n")
        self.lastadded = entrydict["ptacc"]
        return(True)
    def import_ipgxml(self, path):
        for feature in parse_ipgxml_basic(path):
            self.add_entry(feature)
    @staticmethod
    def parse_line(line):
        line = line.rstrip("\n")
        line = line.split("\t")
        pline = {}
        for i in range(len(line)):
            key,value = line[i].split("|")
            if value[0]=="\"" and value[-1]=="\"":
                value = value.strip("\"")
            elif "." in value:
                value = float(value)
            elif value == "\"N/A\"":
                value = None
            else:
                value = int(value)
            pline[key] = value
        return(pline)
    def read_entries(self, qindices):
        #Read the file and output the results
        for index in qindices:
            if index != self.file.tell():
                self.file.seek(index)
            yield(self.parse_line(self.file.readline()))
    def read_entries_dumb(self, keys):
        entries_by_ipg = {}
        ipgs_to_get = set()
        for entry in open(self.path, mode="r"):
            # Parse the line
            entry = self.parse_line(entry)
            
            # Check if this entry's accession is on The List
            if entry["ptacc"] in keys:
                #If so, we'll grab its whole ipg later
                ipgs_to_get.add(entry["iptacc"])
            
            # Save it in case the ipg is needed later
            if entry["iptacc"] not in entries_by_ipg:
                entries_by_ipg[entry["iptacc"]] = []
            entries_by_ipg[entry["iptacc"]].append(entry)
            # Saving it like this is not the most memory efficient thing ever,
            #   but ipgsets are pretty mild compared to everything else,
            #   so it should be fine. Maybe.
        
        total_number_of_proteins = 0
        # Finally, yield all relevant ipgsets.
        for iptacc in ipgs_to_get:
            for entry in entries_by_ipg[iptacc]:
                total_number_of_proteins += 1
                yield(entry)
        print(f"Yielded a total of {total_number_of_proteins} proteins, including IPGs.")
    def fetch_entries_old(self, keys):
        keys = list(keys) #this duplicates the keys argument
                          # otherwise we'll be modifying the original
                          # thing as the function runs
                          # (and also enforces type)
        qindices = [] #target positions in file
        numtoget = len(keys)
        for iternum in range(2,0,-1):
            #First: Check what's already present locally
            i=0
            while i < len(keys):
                if keys[i] in self.indices:
                    qindices += self.indices[keys[i]]
                    del keys[i]
                else:
                    i+=1
            #Second:
            if iternum > 1 and len(keys) > 0 and not self.offline:
                if self.verbose:
                    print(f"{len(keys)} accessions not present locally, downloading...")
                #Don't do this on last iteration
                #Try to download missing requests
                download_ncbi(
                        filepath=self.temppath, id=keys, 
                        chunksize=500, verbose=self.verbose, 
                        db="protein", retmode="xml", rettype="ipg")
                self.import_ipgxml(self.temppath)
        qindices.sort()
        
        if self.verbose:
            print((f"Retrieved {numtoget-len(keys)}/{numtoget} accessions "
                   f"({len(keys)} failed)."))
        return(self.read_entries(qindices))
    def fetch_entries(self, keys):
        keys = set(keys)
        
        keys_present_locally = keys.intersection(self.indices)
        keys_to_download = keys.difference(self.indices)
        
        
        if keys_to_download and not self.offline:
            
            if self.verbose:
                print(f"{len(keys_to_download)} accessions not present locally, downloading...")
            
            path,aborted = download_ncbi(
                    filepath=self.temppath, id=list(keys_to_download), 
                    chunksize=500, verbose=self.verbose, 
                    db="protein", retmode="xml", rettype="ipg")
            if path: # and not aborted:
                self.import_ipgxml(self.temppath)
                self.index_file()
        
        failed = keys.difference(self.indices)
        
        return(self.read_entries_dumb(keys))
    def build_ipg_tree(self, ftdicts, root=None):
        if root is None:
            root = dframe.Root()
        
        duplicateFeatures = 0
        for ftdict in ftdicts:
            #get taxon
            if ftdict["txid"] in root.txAll:
                tx = root.txAll[ftdict["txid"]]
            else:
                tx = dframe.Taxon(
                    ftdict["txid"], root, sciname=ftdict["sciname"],
                    strain=ftdict["txstrain"])
            #get scaffold
            if ftdict["scacc"] in root.scAll:
                sc = root.scAll[ftdict["scacc"]]
            else:
                sc = dframe.Scaffold(ftdict["scacc"], tx)
            #get ipt
            if ftdict["iptacc"] in root.iptAll:
                ipt = root.iptAll[ftdict["iptacc"]]
            else:
                ipt = dframe.IdenticalProteinSet(ftdict["iptacc"], root)
            #get protein
            if ftdict["ptacc"] in root.ptAll:
                pt = root.ptAll[ftdict["ptacc"]]
            else:
                pt = dframe.Protein(ftdict["ptacc"], ipt, name=ftdict["ptname"])

            #finally, make feature
            if ftdict["scacc"] in pt.fts:
                duplicateFeatures += 1
            if ftdict["ftstrand"] == "+":
                ftdict["ftstrand"] = dframe.Strand.PRIMARY
            elif ftdict["ftstrand"] == "-":
                ftdict["ftstrand"] = dframe.Strand.COMPLEMENTARY
            ft = dframe.Feature(scaffold=sc, 
                                reference=pt, 
                                start=ftdict["ftstart"], 
                                stop=ftdict["ftstop"],
                                fttype=ftdict["fttype"],
                                strand=ftdict["ftstrand"])
        return(root)
    def set_offline(self, offline):
        self.offline = offline
#
class ManagerGB():
    #TODO: Ensure that offset calculations don't insert
    #   an extra bp
    #   eg. gene.start = 1 (first position in sequence)
    #       offset = 1500
    #       
    #       adjusted gene.start should be 1500, not 1501
    #   EDIT: Yeah it does exactly that by the looks of it.
    #         Adding fix now.
    accession_pattern = re.compile("<GBSeq_primary-accession>"
                                   "(?P<accession>.+?)"
                                   "</GBSeq_primary-accession>")
    seqlength_pattern = re.compile("<GBSeq_length>"
                                   "(?P<seqlength>.+?)"
                                   "</GBSeq_length>")
    def __init__(self, dbpath, overwrite=False, verbose=True, offline=False):
        super().__init__()
        self.path = dbpath
        #If our db file doesn't exist, or we've been told to overwrite it,
        #    just touch it to create a new file with that path.
        if overwrite is True or not os.path.isfile(dbpath):
            with bz2.open(dbpath, mode="w") as file:
                file.close()
        
        #Indices are in the format (ACCESSION, OFFSET, LENGTH}
        #   Both offset and length are in base pairs.
        self.indices = {}
        
        self.file = None
        
        self.lastadded = None
        self.verbose = verbose
        self.offline = offline
        
        #A list of accessions that NCBI simply won't return
        #   so we don't keep bouncing them off of the server
        #   over and over.
        #   This is reset on restart (assuming we're in an app)
        
        self.maxtries = 2
        self._index_db()
    def _index_db(self):
        debug_t0 = time.time()
        self.indices = set()
        
        with bz2.open(self.path, mode="rt", encoding="utf-8") as infile:
            for line in infile:
                if line:
                    # There's an obscene amount of empty lines in this file.
                    # This conditional genuinely cuts down on processing time.
                    if "<GBSeq_locus>" in line:
                        accession = line.split("<GBSeq_locus>")[1]\
                            .split("</GBSeq_locus>")[0]
                    elif "!REQUEST:" in line:
                        start,stop = [int(x) for x in line.strip("\n").split(":")[1:]]
                        self.indices.add((
                            accession,
                            start,
                            stop
                        ))
        
        debug_t1 = time.time()
        print(f"Indexing GB databse took {debug_t1 - debug_t0} seconds.")
    def _index_db_old(self):
        debug_t0 = time.time()
        self.indices = {}
        entry = []
        with bz2.open(self.path, mode="rt", encoding="utf-8") as self.file:
            linestart = 0
            fileend = self.file.seek(0, os.SEEK_END)
            recording = False
            
            self.file.seek(0)
            while linestart != fileend:
                linestart = self.file.tell()
                line = self.file.readline()
                if "<GBSeq>" in line:
                    #print("Found GBSeq")
                    entry = []
                    entry_start = linestart
                    recording = True
                if recording is True:
                    entry.append(line)
                if "</GBSeq>" in line:
                    #print("GBSeq ended")
                    recording = False
                    entry = "".join(entry)
                    entry_accession = re.search(self.accession_pattern, 
                                                entry)["accession"]
                    self.file.readline() 
                                    # Move the cursor over the final 
                                    #    line, then calculate length
                    #Measured in characters
                    entry_length = self.file.tell() - entry_start
                    
                    #Measured in basepairs
                    sequence_length = re.search(self.seqlength_pattern,
                                                entry)["seqlength"]
                if line.startswith("!REQUEST"):
                    #print("!REQUEST found")
                    request = line.strip("\n").split(":")
                    if entry_accession is None:
                        print("Error! Invalid entry accession!")
                        continue
                    entry_identifier = (entry_accession,
                                        int(request[1]), #start
                                        int(request[2])) #stop
                    if entry_identifier in self.indices:
                        print("Duplicate entry found.")
                        continue
                    #print("Added indices")
                    self.indices[entry_identifier] = \
                        (entry_start, entry_length)
        self.file = None
        debug_t1 = time.time()
        print(f"Indexing GB databse took {debug_t1 - debug_t0} seconds.")
    def add_entry(self, entry, start, stop):
        #print("Writing file")
        if self.file is None:
            #print("Getting new file IO")
            gotfile = False
            self.file = bz2.open(self.path, mode="a")
        else:
            #print("Already got file IO")
            gotfile=True
        
        #length = len(entry)
        self.file.write(entry.encode("utf-8"))
        #We record the exact request, because sometimes sequences
        #    return shorter than the request asked for.
        self.file.write(f"\n!REQUEST:{start}:{stop}\n\n\n".encode("utf-8"))
        self.file.flush()
        
        
        #accession = re.search(self.accession_pattern, 
        #                      entry)["accession"]
        
        #I'd love to track the index at time of writing, but
        # it's a bit obnoxious to arrange without a stream seek
        # function due to line breaks sometimes taking up 2 chars 
        # (\n\r) and only 1 at other times (\n)
        #At present, the only way to update the record is to _index_db
        # and this is quite time-consuming.
        
        self.file.flush()
        
        if gotfile is False:
            #If we didn't get the file object passed,
            #  we clean up after ourselves.
            self.file.close()
            self.file = None
    def _read_entry(self, identifier):
        if self.file is None:
            gotfile = True
            self.file = bz2.open(self.path, mode="rt", encoding="utf-8")
        else:
            gotfile = False
        
        position,length = self.indices[identifier]
        self.file.seek(position)
        entry = self.file.read(length)
        
        #Search for 100 lines after the end of the record
        i=100
        line=""
        while not line.startswith("!REQUEST:"):
            line = self.file.readline()
            i -= 1
            if i == 0:
                #If none is found, the db is probably broken
                print("ERROR: No offset found.")
                break
        
        offset = line.strip("\n").split(":")
        request_start = int(offset[0])
        request_stop = int(offset[1])
        
        # Our parsing function accepts file-like objects
        #     so we wrap our entry string in a io.StringIO buffer
        #     to make it the same ducktype as a file object.
        entry = io.StringIO(entry)
        record = self.parse_gb_xml(entry, offset)
        
        if gotfile is False:
            self.file.close()
            self.file = None
        return(record)
    def _read_entry_by_index(self, position, length):
        if self.file is None:
            gotfile = True
            self.file = bz2.open(self.path, mode="rt", encoding="utf-8")
        else:
            gotfile = False
        
        self.file.seek(position)
        entry = self.file.read(length)
        
        i=100
        line=""
        while not line.startswith("!REQUEST:"):
            line = self.file.readline()
            i -= 1
            if i == 0:
                print("ERROR: No offset found.")
                break
        
        request = line.strip("\n").split(":")
        offset = int(request[1]) #Sequence start
        
        # Our parsing function accepts file-like objects
        #     so we wrap our entry string in a io.StringIO
        #     to make it the same ducktype as a file object.
        entry = io.StringIO(entry)
        record = self.parse_gb_xml(entry, offset)
        
        if gotfile is False:
            self.file.close()
            self.file = None
        
        return(record)
    def _download_neighbourhood(self, accession, start, stop):
        chunks = []
        done = False
        tries = 0
        #Calculate the read positions
        if start < 1:
            start = 1
        #The basic issue here is that we know that all sequences
        #   start at 1, but we do not know where they end.
        #   That means the start position of a downloaded sequence
        #   will always be the same as the request (unless the
        #   request was for a start less than 1), but we do not
        #   know where the stop is.
        #   We need to know the true start position within the
        #   original NCBI sequence, as well as have a consistent
        #   identifier to know which sequences are already downloaded.
        #   To this end, we save "stop" of the request, but, change
        #   the "start" to fit the sequence.
        
        while not done and tries < self.maxtries:
            tries += 1
            print("Downloading...", end="\n")
            try:
                handle = Entrez.efetch(
                    id=accession, db="nuccore", rettype="gb", 
                    retmode="xml", seq_start=start, 
                    seq_stop=stop)
                for line in handle:
                    line = line.decode("utf-8")
                    chunks.append(line)
                self.add_entry("".join(chunks), start, stop)
                done = True
                break
            except:
                #Have to retry
                pass
        if tries == self.maxtries:
            print(f"\rFailed download of {accession}")
            return(False)
        else:
            return(True)
        #Then save the entry
        pass
    def fetch_entries(self, queries):
        #Alt format:
        # [("accession", start, stop), ...]
        nqueries = set()
        for item in queries:
            #Turn queries into identifiers using the format
            #   (ACCESSION, SEQ_START, REQUEST_STOP)
            #   This lets us play with them using sets.
            # Request stop is the stop position as requested
            #    SEQ_START can be less if the sequence in GenBank
            #    ends before the REQUEST_STOP
            nqueries.add((item[0], #accession
                         max(item[1], 1), #Start can be 1 or higher
                         item[2])) #We don't know what the maximum for stop is
        queries = nqueries
        del nqueries
        
        #Download the missing neighbourhoods
        retries = 0
        
        #We need_to_get all query identifiers that aren't present
        
        need_to_get = queries.difference(set(self.indices))
        
        # Check with download manager if it's OK to download this much.
        if len(need_to_get) > 0:
            abort = DOWNLOAD_MANAGER.download_starting(type="nuccore", 
                                                   number_to_download=len(need_to_get))
        
        download_size = len(need_to_get)
        if need_to_get and not self.offline and not abort:
            #If there's stuff we need to get AND we're online
            while retries < self.maxtries and len(need_to_get) > 0 and not abort:
                #While we have tried fewer tries than the max allowed
                #  AND there are still entries to fetch
                
                processed = set()
                i=0
                for identifier in need_to_get:
                    i += 1
                    outcome = self._download_neighbourhood(
                        identifier[0], #accession
                        identifier[1], #start
                        identifier[2]) #stop
                    if outcome:
                        #If the file downloaded successfully
                        processed.add(identifier)
                        print(f"\rDownloaded ({i}/{download_size})", end="")
                    need_to_get = need_to_get.difference(processed)
                    abort = DOWNLOAD_MANAGER.download_status(
                        number_left_to_download = len(need_to_get))
            DOWNLOAD_MANAGER.download_ended()
            self._index_db()
        
        
        #Return all queries except for the ones that failed to retrieve
        #   (as in, we KNOW we don't have them)
        return_queries = queries.difference(need_to_get)
        
        # Convert all the query identifiers into database indices,
        #   then sort them in the order they are found inside the file.
        #EDIT: This is unnecessary when using the
        #       self._results_generator_dumb(), commenting out.
        #return_indices = []
        #for identifier in return_queries:
        #    return_indices.append(self.indices[identifier])
        #return_indices.sort(key=lambda x: x[0])
        
        results = self._results_generator_dumb(return_queries)
        #Yield results
        return(results)
    #
    def _results_generator_dumb(self, return_queries):
        # This is a somewhat more optimized generator function which doesn't
        #   try to pretend that it's a database, but instead simply scans the
        #   storage file, and grabs everything that's on the shopping list.
        # The nice thing about this is that we can more or less drop the
        #   endless indexing and speed everything up.
        # The not so nice thing is that things will slow back down as the db
        #   gets bigger and sequential read times worse.
        
        
        # First, get all the accessions into a hash so we can perform
        #   set operations on the cheap.
        accessions_to_get = {}
        for identifier in return_queries:
            accessions_to_get[identifier[0]] = identifier
        
        with bz2.open(self.path, mode="rt", encoding="utf-8") as infile:
            for line in infile:
                if line:
                    # There's an obscene amount of empty lines in this file.
                    # This conditional genuinely cuts down on processing time.
                    if "<?xml" in line:
                        store=True
                        record = []
                    elif "<GBSeq_locus>" in line:
                        identifier = accessions_to_get.get(line.split("<GBSeq_locus>")[1]\
                            .split("</GBSeq_locus>")[0])
                        if not identifier:
                            # If the accession isn't in our queries to get, identifier will be None
                            store=False
                    elif "!REQUEST:" in line:
                        if store:
                            # The format of the request line is:
                            #   !REQUEST:{start}:{stop}
                            #   ergo, the offset is {start}, so we just split by : and keep trucking.
                            # Additionally, we concatenate the lines stored in record, and wrap them
                            #   inside of a StringIO to turn the record string
                            #   into the same ducktype as a file, since that's what the method
                            #   self.parse_gb_xml actually uses.
                            #   All using a one liner for xtreme speed.
                            try:
                                parsed_record = self.parse_gb_xml(io.StringIO("".join(record)),
                                                 int(line.split(":")[1]))
                            except ET.ParseError:
                                print(f"XML Error while reading {identifier}!!")
                            else:
                                yield(parsed_record)
                        store=False
                    if store:
                        record.append(line)
    def _results_generator(self, queries_to_get):
        #The generator is separate to ensure that data is downloaded
        #    before any attempts to read the results can be made.
        with bz2.open(self.path, mode="rt", encoding="utf-8") as self.file:
            for query in queries_to_get:
                # query = (position, length)
                yield(self._read_entry_by_index(query[0], 
                                                query[1]))
        self.file = None
        #TODO: variable names, define arguments properly
    @staticmethod
    def parse_gb_xml(handle, offset):
        #Reads a genbank XML file.
        #  This parser could originally read through multiple records inside a single XML,
        #  but this has been changed due to problems with keeping track of the offset.
        #This parser *needs* to know the offset of the genbank file relative to the contig, as
        #  without it, the neighbourhood will be misaligned relative to the reference, and
        #  may end up overlapping with other neighbourhoods in the same contig.
        #  By as of writing, the offset (or rather the start/stop positions of the neighbourhood)
        #  are listed both in genbank(.gb) filenames and in the _index.txt
        def parse_position(raw, position_offset):
            #Handles (some) of the shapes position data can manage
            #Likely can't handle anything with introns or otherwise eukaryotic
            #TODO:
            #The current implementation is painfully hacky, but it stays until I can figure out
            #  how to make python process functional statements in strings without using eval
            raw=raw.replace(">","")
            raw=raw.replace("<","")
            if "complement" in raw:
                strand=dframe.Strand.COMPLEMENTARY
                raw = raw.lstrip("complement(").rstrip(")")
            else:
                strand=dframe.Strand.PRIMARY
            if "join" in raw:
                raw = raw.lstrip("join(").rstrip(")").split(",")
                raw = "..".join([raw[0].split("..")[0], raw[1].split("..")[1]])
            raw=raw.split("..")
            try:
                #TODO: A bizzare behaviour from the xml.etree parser occurs where
                #  an element.tag gets read as <1 instead of whatever it should be
                #  I have no idea why this happens or how to stop it--
                #  So for now, I just handle the exceptions.
                #NOTE: The -1 below is compensating for offset calculations being one bp off.
                #      Best not to ask. Probably.
                start = int(raw[0]) + position_offset - 1
                stop  = int(raw[1]) + position_offset - 1     
                return(start,stop,strand)
            except:
                return None
        
        
        #Recorded qualifier tags:
        recquals = set(["product", "protein_id", "translation"])
        feature = None
        record = None
        qname = None
        for event, elem in ET.iterparse(handle, events=("start","end")):
            #Handling qualifiers
            if event=="end" and elem.tag=="GBQualifier_value":
                if qname:
                    feature[qname] = elem.text
                    qname = None
            elif event=="end" and elem.tag=="GBQualifier_name":
                if elem.text in recquals:
                    qname = elem.text
            #/Handling qualifiers
            elif event=="end" and elem.tag=="GBFeature_location":
                res = parse_position(elem.text, offset)
                if res is None:
                    res = (-1, -1, None)
                    print("Encountered bizarre error while parsing sequence {}.".format(record["accession"]))
                    skip_feature = True
                feature["start"],feature["stop"],feature["strand"] = res
            elif event=="end" and elem.tag=="GBFeature_key":
                feature["type"] = elem.text.lower()
            elif event=="start" and elem.tag=="GBFeature":
                #Integrate previous feature
                if feature:
                    if feature["type"] != "source" and not skip_feature:
                        record["features"].append(feature)
                #Create new feature
                skip_feature = False
                feature = {
                    "type": None,
                    "start": None,
                    "stop": None,
                    "product": None,
                    "protein_id": None,
                    "translation": None,
                    "strand": None,
                    #Also includes any recquals declared above
                }
            elif event=="start" and elem.tag=="GBSeq_feature-table":
                record["features"] = []
            elif event=="end" and elem.tag=="GBSeq_organism":
                record["sciname"] = elem.text
            elif event=="end" and elem.tag=="GBSeq_primary-accession":
                record["accession"] = elem.text
            elif event=="start" and elem.tag=="GBSeq":
                record = {
                    "accession": None,
                    "sciname": None,
                    "features": None,
                }
        return(record)
    @staticmethod
    def add_features(gbrecord, root, types_=None):
        if gbrecord["accession"] not in root.scAll:
            return(False)
        sc = root.scAll.get(gbrecord["accession"])
        for rawfeature in gbrecord["features"]:
            if types_ is not None and rawfeature["type"] not in types_:
                continue
            if rawfeature["type"] == "cds":
                if rawfeature["protein_id"] is None:
                    #Sometimes pseudogenes get a CDS
                    # with a nonexistent protein.
                    # -- it's not actually a coding sequence, so it gets ignored.
                    continue
                #Trim the version number from the accession
                rawfeature["protein_id"] = rawfeature["protein_id"]\
                    .split(".")[0]
                #Build protein/iprotein if they're missing
                #   We don't know which proteins are identical,
                #   so we just set up an iprotein for each protein
                if (rawfeature["protein_id"]
                        not in root.iptAll):
                    #If ipt doesn't exist, create it
                    ipt = dframe.IdenticalProteinSet(
                        rawfeature["protein_id"], root)
                else:
                    #Otherwise, just grab it
                    ipt = root.iptAll[rawfeature["protein_id"]]
                if (rawfeature["protein_id"].split(".")[0] 
                        not in root.ptAll):
                    #If protein doesn't exist, create it
                    pt = dframe.Protein(
                        rawfeature["protein_id"], 
                        ipt, 
                        seq=rawfeature["translation"], 
                        name=rawfeature["protein_id"], 
                        type=rawfeature["product"])
                else:
                    #If the protein already exists
                    pt = root.ptAll[ rawfeature["protein_id"].split(".")[0]  ]
                    #Update its optional attributes instead
                    pt.seq = rawfeature["translation"]
                    pt.type = rawfeature["product"]
                    
                    #Leaving this out because it's likely already been set
                    #pt.name = rawfeature["protein_id"]
                dframe.Feature(scaffold=sc, 
                               reference=pt, 
                               start=rawfeature["start"], 
                               stop=rawfeature["stop"], 
                               fttype=rawfeature["type"],
                               strand=rawfeature["strand"])
    def set_offline(self, offline):
        self.offline = offline
#
class ManagerClus():
    usearch_file_win = re.compile("usearch.*\.exe")
    usearch_file = re.compile("usearch.*")
    def __init__(self):
        super().__init__()
        self.p_proteinfasta = os.path.join(os.path.curdir, "data", "neighborhood_proteins.fsa")
        
        self.p_results = os.path.join(os.path.curdir, "data", "clustering_results.uc")
        self.p_usearch = None
        
        self.p_blastp = None
        self.p_blastquery = os.path.join(os.path.curdir, "data", "local_blast_query.fsa")
        self.p_blastresult = os.path.join(os.path.curdir, "data", "local_blast_results.xml")
        self.p_ublastresult = os.path.join(os.path.curdir, "data", "local_ublast_results.txt")
    def fasta_dump(self, accessions, root, verbose=True, key=lambda x: len(x.seq), path=None):
        t0 = time.time()
        errors = Counter()
        
        #Get all the proteins
        pts = []
        for accession in accessions:
            pt = root.ptAll[accession]
            if pt.seq is None:
                errors["No sequence in protein"] += 1
                continue
            errors["Completed"] += 1
            pts.append(pt)
        
        #Sort sequences from shortest to longest
        pts.sort(key=key)
        
        #Write all sequences
        if path == None:
            path = self.p_proteinfasta
        with open(path, mode="w") as fastadump:
            for pt in pts:
                fastadump.write(f">{pt.accession}\n{pt.seq}\n")
        if verbose:
            print(errors)
        print(f"Completed fasta dump in {time.time()-t0} seconds.")
    def get_usearch_path(self):
        if self.p_usearch == None:
            #If no path specified
            #Try to find the usearch executable in the local directory
            usearches = []
            for item in os.scandir(os.path.curdir):
                if item.is_file() and re.match(self.usearch_file, item.name):
                    usearches.append(item)
            if len(usearches) == 0:
                raise Exception("usearch not found in local directory! " 
                                "the executable name must start with \"usearch!\". "
                                "Please specify a path or add usearch.")
            elif len(usearches) == 1:
                return(usearches[0].path)
            elif len(usearches) > 1:
                raise Exception("Multiple files starting with \"usearch\" found in "
                                "local directory!\nUnable to determine correct one. "
                                "Ensure only one executable is present, or specify "
                                "a path.")
        #Otherwise, just return it.
        return(self.p_usearch)
    def get_blastp_path(self):
        if self.p_blastp is not None:
            return(self.p_blastp)
        else:
            raise Exception("Path to blastp.exe not found! "
                            "Make sure to specify cluster manager's p_blastp.")
    def run_usearch(self, identity):
        usearch_path = self.get_usearch_path()
        
        arguments = [
                usearch_path,
                "-cluster_fast", self.p_proteinfasta,
                "-id", str(identity),
                "-uc", self.p_results,
            ]
        subprocess.call(arguments)
    def parse_cluster_results(self, root, identity, verbose = True):
        with open(self.p_results, mode="r", encoding="utf-8") as results_handle:
            _main_fields = [
                    "type",
                    "cluster_id",
                    "seq_length",
                    "percent_identity",
                    "strand",
                    "?",
                    "alignment",
                    "query",
                    "identifier",
                    "??"]
            result = dframe.PClusteringResult(root, identity=identity)
            errors = Counter()
            for line in results_handle:
                line = line.split("\t")
                lineD = {}
                errors["Processed line"] += 1
                for i in range(0, len(line)):
                    lineD[_main_fields[i]] = line[i]
                if lineD["type"] == "S" or lineD["type"] == "H":
                    protein = result.root.ptAll.get(lineD["identifier"])
                    if protein is None:
                        errors["Clustered protein identifier not found in root!"]
                        continue
                    if lineD["percent_identity"] == "*":
                        identity = 100.0
                    else:
                        identity = float(lineD["percent_identity"])
                    cluster = result.get(lineD["cluster_id"])
                    cluster.add_member(protein, identity)
                    if lineD["type"] == "S":
                        if cluster.centroid is not None:
                            print("Bro, what's wrong with your cluster?")
                        cluster.centroid = protein
            if verbose:
                errors["Clusters Created"] = len(result.clusters)
                print(errors)
            return(result)
    def neighborhood_blast(self, query, bonus_args=[]):
        #TODO: Maybe add a check if the fastas are there.
        
        #query can be str or list of sequences
        
        # get executable path
        blast_path = self.get_blastp_path()
        
        # create query fasta
        if not isinstance(query, list):
            query = [query]
            
        with open(self.p_blastquery, mode="w") as queryfile:
            i=0
            for x in query:
                if isinstance(query, str):
                    queryfile.write(f">unnamed_sequence_{i}\n{x}\n")
                    i+=1
                else:
                    queryfile.write(f">{x.accession}\n{x.seq}\n")
            queryfile.flush()
            queryfile.close()
        
        #TODO: We're counting on the fasta dump already being there!
        #      Maybe ensure that is the case somewhere upstream.
        
        # put together all the arguments
        # TODO: Maybe allow the user to set the blast options. MAYBE!
        #       For now I'm adding an argument to allow this to be implemented.
        arguments = [
            blast_path,
            "-query", self.p_blastquery,
            "-subject", self.p_proteinfasta,
            "-outfmt", "5",
            "-out", self.p_blastresult,
            "-num_threads", "9",
        ]
        
        # Append whatever else was specified by the caller
        #   if it crashes BLAST, it's their fault.
        arguments.extend(bonus_args)
        if "-max_target_seqs" not in arguments:
            # If max_target_seqs was not specified in bonus_args, add it now.
            # We want MAXIMUM blasting, even if it's bad for us.
            # (Also, max_target_seqs tends to skewer results because of
            #  how it's implemented unless we get all the results.)
            arguments.extend(["-max_target_seqs", "999999"])
        
        print(arguments)
        # Call BLAST itself
        subprocess.call(arguments)
        
        # Then we parse those results.
        results = load_blastp_xmls([self.p_blastresult])
        
        return(results)
    def parse_blast6out_results(self, resultfile):
        #Column description:
        # (0)label, (1)target, (2)%identity, (3)align_length, (4)n_mismatches,
        # (5)n_gap_opens, (6)startpos_in_query, (7)endpos_in_query,
        # (8)startpos_in_hit, (9)endpos_in_hit,
        # (10)evalue, (11)bitscore
        # S,S,F,I,I,I,I,I,I,I,F,F
        results = {}
        with open(resultfile) as ffile:
            rfile = [None if line=="" else (line.split("\t")) for line in ffile.read().split("\n")]
            ffile.close()
        for line in rfile:
            if line is None:
                continue
            results[line[1]] = {
                "query": line[0], 
                "hit": line[1], 
                "pidentity": float(line[2]), 
                "align_length": int(line[3]), 
                "n_mismatches": int(line[4]), 
                "n_gap_opens": int(line[5]), 
                "startpos_in_query": int(line[6]), 
                "endpos_in_query": int(line[7]), 
                "startpos_in_hit": int(line[8]), 
                "endpos_in_hit": int(line[9]), 
                "evalue": float(line[10]), 
                "bitscore": float(line[11])}
        return(results)
    def neighborhood_ublast(self, query, evalue=None,accel=1.0,identity=None):
        #TODO: Maybe add a check if the fastas are there.
        #IMPORTANT NOTE: This function just uses any database of fasta sequences
        #   at self.p_proteinfasta, but does not generate it! Beware! Beware!
        
        
        # create query fasta
        if not isinstance(query, list):
            query = [query]
        
        with open(self.p_blastquery, mode="w") as queryfile:
            i=0
            for x in query:
                if isinstance(x, str):
                    #If it's a string, just give it an arbitrary ID
                    queryfile.write(f">unnamed_sequence_{i}\n{x}\n")
                    i+=1
                elif isinstance(x, dframe.ProteinCluster):
                    #If it's a cluster, use the cluster's _id and the centroid
                    queryfile.write(f">{x._id}\n{x.centroid.seq}\n")
                else:
                    #And if it's not either of those, it's PROBABLY a dbdl.Protein
                    queryfile.write(f">{x.accession}\n{x.seq}\n")
            queryfile.flush()
            queryfile.close()
        
        #TODO: We're counting on the fasta dump already being there!
        #      Maybe ensure that is the case somewhere upstream.
        
        # put together all the arguments
        # TODO: Maybe allow the user to set the blast options. MAYBE!
        #       For now I'm adding an argument to allow this to be implemented.
        arguments = [
            self.get_usearch_path(),
            "-ublast", self.p_blastquery,
            "-db", self.p_proteinfasta,
            "-blast6out", self.p_ublastresult,
            "-accel", str(accel),
        ]
        if evalue:
            arguments.extend(["-evalue", str(evalue)])
        if identity:
            identity.extend(["-identity", str(identity)])
        if not evalue and not identity:
            assert ("Neither evalue nor identity specified!"
                    "Must specify at least one!")
        
        print(arguments)
        # Call UBLAST itself
        subprocess.call(arguments)
        
        # Then we parse those results.
        results = self.parse_blast6out_results(self.p_ublastresult)
        
        return(results)
    def ublast_meta_cluster(self, clustering_result, root, evalue=None, identity=None):
        errors = Counter()
        
        # Generates non-repeating alphabetic names.
        # Basically a base26 id generator.
        def id_generator():
            output = [-1]
            alphabet="abcdefghijklmnopqrstuvwxyz".upper()
            while True:
                output[0] += 1
                for i in range(len(output)):
                    if output[i] == len(alphabet):
                        output[i] = 0
                        try:
                            output[i+1] += 1
                        except:
                            output.append(0)
                yield("".join([alphabet[pos] for pos in output[::-1]]))
        def id_generator_numbers():
            i = -1
            while True:
                i += 1
                yield(str(i))
        #ids = id_generator()
        ids = id_generator_numbers()
        
        #inclusters are globally aligned clusters
        #make a list of clusters sorted by length of centroid)
        #TODO: It may be possible for a None cluster to get passed to this function
        #      find out why (Email from jirka)
        inclusters = set([clus for clus in clustering_result.clusters.values()])
        
        #Check and debug for missing clusters
        error_missing_centroids = 0
        get_rid = set()
        for clus in inclusters:
            if not clus.centroid:
                get_rid.add(clus)
                error_missing_centroids += 1
        inclusters = list(inclusters - get_rid)
        if error_missing_centroids:
            print(f"DEBUG: {error_missing_centroids} had a None centroid.")
        
        #outclusters are locally aligned clusters
        #Clustering result to store our meta clusters in
        outclusters = dframe.PClusteringResult(root, identity=identity, evalue=evalue)
        #We will only need these at the end
        
        #Create db of centroids, with homo_clusters _ids as sequence headers
        path = self.p_proteinfasta
        with open(path, mode="w") as fastadump:
            for clus in inclusters:
                fastadump.write(f">{clus._id}\n{clus.centroid.seq}\n")
        
        #Create a bunch of arrays (bins) each containing only one input member
        #   We'll slowly merge the bins over the course of clustering.
        uniquebins = []
        bins = {}
        for i in range(len(inclusters)):
            bins[inclusters[i]._id] = [inclusters[i]]
            uniquebins.append(bins[inclusters[i]._id])
        
        #And start looping.
        finished = False
        chunk_size = 50000
        while len(inclusters) != 0:
            # * Take {chunk_size} shortest clusters
            chunk = inclusters[0:min(chunk_size, len(inclusters))]
            
            #Remove these clusters
            inclusters = inclusters[min(chunk_size, len(inclusters)):]
            
            # * Align it with the database
            alignments = self.neighborhood_ublast(chunk, evalue=evalue)
            
            # Since we used homo_cluster ids as identifiers of the
            #    centroid sequences, instead of the sequences' accessions,
            #    the process of clustering is relatively simple.
            
            
            
            for alignment in alignments.values():
                if bins[alignment["query"]] is bins[alignment["hit"]]:
                    #If they're already grouped, move on
                    continue
                else:
                    #Otherwise, combine the two bins
                    bins[alignment["query"]].extend(bins[alignment["hit"]])
                    
                    #Then clear the latter (so we can identify empty bins)
                    bins[alignment["hit"]].clear()
                    
                    #And overwrite the bins entry to point to the former
                    #    (so we can find where a given member belongs quickly)
                    bins[alignment["hit"]] = bins[alignment["query"]]
        
        
        
        #Now we create clusters!
        assigned = set()
        
        for bin in uniquebins:
            if not bin:
                # Gets rid of cleared bins
                continue
            if len(bin) != len(set(bin)):
                print(bin, set(bin))
                assert "Multiple assignments of the same member to the same bin."
            
            outcluster = dframe.ProteinCluster(ids.__next__(), outclusters)
            
            for member in bin:
                if member in assigned:
                    print(member_id, bin)
                    assert True, "Member assigned multiple times!"
                assigned.add(member)
                outcluster.add_member(member)
        
        return(outclusters)
#
class BLASTManager():
    def __init__(self):
        pass
    def new_search(self):
        pass
    def start_search(self):
        pass
    def ping_search(self):
        pass
    def end_search(self):
        pass
    @staticmethod
    def remote_blast(query, db="nr", expect=10.0, filter=None, 
                     entrez_query=None, nhits=20000,
                     gapcosts="11 1", 
                     matrix_name="BLOSUM62", 
                     threshold=11, 
                     word_size=6, 
                     comp_based_statistics=2):
        if isinstance(query, list):
            query = "\n".join(query)
        blast = NCBIWWW.qblast("blastp", database=db, sequence=query, expect=expect, 
                        descriptions=nhits, alignments=nhits, filter=filter, 
                        format_type="XML", entrez_query=entrez_query, hitlist_size=nhits,
                        gapcosts=gapcosts, matrix_name=matrix_name, threshold=threshold, 
                        word_size=word_size, composition_based_statistics=comp_based_statistics)
        return(blast)
#
def condense_ipgs(inputPaths, outputPath):
    with gzip.open(outputPath, mode="wt") as output:
        output.write("<IPGSet>\n")
        for inputPath in inputPaths:
            with gzip.open(inputPath, mode="rt") as input:
                write = False
                for line in input:
                    #if line[:10] == "<IPGReport": #IPGSETSET
                    if ("<IPGReport " in line): #TODO: does xml use \t instead of space?
                        write = True
                        line = line.split("<IPGReport")[-1]
                        output.write("<IPGReport"+line)
                    elif "</IPGReport>" in line:
                        write = False
                        line = line.split("</IPGReport>")[0]
                        output.write(line+"</IPGReport>\n")
                    elif write:
                        output.write(line)
                    #/Transfer
                    #if line[-13:] == "</IPGReport>\n":
        output.write("</IPGSet>\n")
        output.flush()
#
def load_blastp_xmls(paths):
    # For loading the BLASTP results data, we just use the default
    #   biopython record classes and hang some of our own variables
    #   on top of them so they can be used in the data structure.
    #
    # record.als is a dict of alignments by protein accession
    #   I'd put this into record.alignments, but I'm a little scared
    #   to break compatibility with the original data structure,
    #   just in case.
    def facc(accession):
        return(accession.split(".")[0])
    records = {}
    if len(paths) == 0:
        raise ValueError("Argument \"paths\" does not contain any elements!")
    for path in paths:
        # For badly formed XML, we need to read the full file first and get
        #   rid of what breaks the parser (CREATE_VIEW).
        handle = io.StringIO(open(path).read().replace("CREATE_VIEW", ""))
        # I think the NCBI BLAST output just does this to signal information
        #   to the web data viewer, but biopython's XML parser doesn't know
        #   how to process it so it crashes.
        
        file = NCBIXML.parse(handle)
        fasta_blast = False
        for record in file:
            record.query_id = facc(record.query_id)
            record.als = {}
            #Check if this is blast is derived from a 
            #   multifasta database, using this hack:
            try:
                if "subject" in record.alignments[0].accession.lower():
                    #If so, flip a flag
                    fasta_blast = True
            except IndexError:
                print("Error! Record contains no alignments!!")
            else:
                for alignment in record.alignments:
                    if fasta_blast:
                        #If this is a fasta_blast, the sequence identifiers
                        #   will be found in a different field:
                        alignment.accession = facc(alignment.hit_id)
                    else:
                        alignment.accession = facc(alignment.accession)
                    #Set up links to record and protein
                    alignment.record = record
                    alignment.pt = None
                    #
                    record.als[alignment.accession] = alignment
                    alignment.tophsp = max(alignment.hsps, 
                                           key=lambda hsp: hsp.score)
                records[record.query_id] = record
        file.close()
    return(records)
#
def download_ncbi(filepath=None, id=None, chunksize=500, verbose=True, **kwargs):
    if filepath is None:
        raise ValueError("Argument \"filepath\" is unspecified or None. Requires a path str (Eg. C:/thing.txt).")
    if id is None:
        raise ValueError("Argument \"id\" is unspecified or None. Use a list of GenBank accession codes.")
    accessions = id #Confusion bonus
    
    # Check with download manager
    if len(id) > 0:
        abort = DOWNLOAD_MANAGER.download_starting(
            kwargs["db"],
            number_to_download=math.ceil(len(id)/chunksize)*chunksize)
        if abort: return(None, None)
    
    #How many full-sized accession blocks to expect
    #  There will usually be one final chunk that's smaller than chunksize
    nchunks = math.floor(len(accessions)/chunksize)
    querychunks=[] #The blocks of accessions we'll iterate over
    
    XML = False
    if kwargs["retmode"] == "xml":
        XML = True
    
    last = 0
    for i in range(0, nchunks):
        #Compose our chunks into strings
        last = ((i+1)*chunksize)
        querychunks.append(",".join(accessions[i*chunksize:last]))
    # - Add final chunk to fill in the rest
    if len(accessions) > last:
        querychunks.append(",".join(accessions[last:len(accessions)]))
    
    # - - - Start writing our output file.
    #maybe don't do this, people can name their stuff what they like:
    #if ".gz" not in filepath:
    #    filepath+=".gz"
    first=True
    with gzip.open(filepath, mode="wt") as output:
        if verbose:
            print("Opened file at {}\n".format(filepath))
        #IF XML
        if XML:
            #TODO: Deleting header and inserting our own is hacky, fix later
            output.write("<?xml version=\"1.0\" encoding=\"UTF-8\"  ?>\n")
            output.write("<ReportSetSet>\n")
        #IF OTHER
            #TODO: Fill in other modes if needed.
        #Now iterate the requests
        i=0
        imax = len(querychunks)
        while i < imax and not abort: #We're using while to facilitate retries
            # abort is a signal from Download Manager as to whether we should
            #   interrupt the download for some reason.
            
            chunkcontent = [] #We'll save the chunk into this variable
            #Save the chunk into memory in case transfer fails
            time.sleep(0.1)
            chunk = querychunks[i]
            if verbose:
                print("Downloading {}-long chunk {}/{}...\r".format(len(chunk.split(",")),i+1,imax))
            #try:
            try:
                handle = Entrez.efetch(id=chunk, **kwargs)
                for line in handle:
                    line = line.decode("utf-8")
                    if ((XML) and ("<?xml" in line)):
                        continue
                    chunkcontent.append(line)
                i+=1
            except:
                if verbose:
                    print("Failed, retrying...")
                continue
                #The transfer failed, do not increment i, which will result in a retry next iteration
            for line in chunkcontent:
                output.write(line)
            abort = DOWNLOAD_MANAGER.download_status(
                number_left_to_download=(imax-i)*chunksize)
        if XML:
            output.write("\n</ReportSetSet>\n")
        output.flush()
        output.close()
        if verbose:
            print("Complete.")
        DOWNLOAD_MANAGER.download_ended()
    return(filepath, abort)
#
def download_neighbors(inputs, folder=None, verbose=True, **kwargs):
    #This function is derived from download_ncbi, but is built for a specific purpose
    #input should be a list of tuples in the format (nucletoide_id, start, stop)
    # EG: inputs = [(id1, 200, 500), (id2, 800, 1200), (id3, 0, 300)]
    if folder is None:
        raise ValueError("Argument \"folder\" is unspecified or None. Requires a path str (Eg. C:/thing.txt).")
    db="nuccore"
    rettype="fasta_cds_aa"
    retmode="text"
        
    #Initialize verbose mode variables    
    verbosemax = 1
    verbosei = 0
    #The goal is to avoid spamming the output when too many files are downloaded
    #The verbose output reports less and less frequently the more iterations it's gone through
    
    # - - - Start writing our output file.
    #maybe don't do this, people can name their stuff what they like:
    #if ".gz" not in filepath:
    #    filepath+=".gz"
    first=True
    i=0
    imax = len(inputs)
    with open(folder+"_index.txt", mode="w") as indexfile:
        while i < imax: #We're using while to facilitate retries
            #Save the chunk into memory until the transfer completes
            time.sleep(0.1)
            if verbose:
                #see verbosemax/i explanation above
                verbosei += 1
                if verbosei==verbosemax:
                    print("Downloading neighbourhood {}/{}...".format(i+1,imax+1))
                    verbosei = 0
                    verbosemax = verbosemax + 1 + math.floor(verbosemax*0.2)
            #Unpack the input
            id,start,stop = inputs[i]
            filepath = folder+"{}_{}-{}.gb.gz".format(id,start,stop)
            try:
                chunk = []
                handle = Entrez.efetch(id=id, db="nuccore", rettype="gb", 
                                       retmode="xml", seq_start=start, 
                                       seq_stop=stop, **kwargs)
                #store the downloaded genbank file in memory
                for line in handle:
                    line = line.decode("utf-8")
                    chunk.append(line)
                #once the download is complete, save the file
                with gzip.open(filepath, mode="wt") as output:
                    #May need to use mode="wt" if the handle returns strings
                    for line in chunk:
                        output.write(line)
                i+=1
                #also add the file to the index
                indexfile.write("{}\t{}\t{}\t{}\n".format(id,start,stop,filepath))
            except:
                if verbose:
                    print("Failed, retrying...")
                continue
            #    #The transfer failed, just try again
        return(filepath)
def download_neighbors_old(inputs, filepath=None, verbose=True, **kwargs):
    #This function is derived from download_ncbi, but is built for a specific purpose
    #input should be a list of tuples in the format (nucletoide_id, start, stop)
    # EG: inputs = [(id1, 200, 500), (id2, 800, 1200), (id3, 0, 300)]
    if filepath is None:
        raise ValueError("Argument \"filepath\" is unspecified or None. Requires a path str (Eg. C:/thing.txt).")
    db="nuccore"
    rettype="fasta_cds_aa"
    retmode="text"
    
    
    XML = True
        
    #Initialize verbose mode variables    
    verbosemax = 1
    verbosei = 0
    #The goal is to avoid spamming the output when too many files are downloaded
    #The verbose output reports less and less frequently the more iterations it's gone through
    
    # - - - Start writing our output file.
    #maybe don't do this, people can name their stuff what they like:
    #if ".gz" not in filepath:
    #    filepath+=".gz"
    first=True
    with gzip.open(filepath, mode="wt") as output:
        if verbose:
            print("Opened file at {}".format(filepath))
        if XML:
            #TODO: Deleting header and inserting our own is hacky, fix later
            output.write("<?xml version=\"1.0\" encoding=\"UTF-8\"  ?>\n")
            output.write("<ReportSetSet>\n")
        #IF OTHER
            #TODO: Fill in other modes if needed.
        #Now iterate the requests
        i=0
        imax = len(inputs)
        while i < imax: #We're using while to facilitate retries
            chunkcontent = [] #We'll save the chunk into this variable
            #Save the chunk into memory until the transfer completes
            time.sleep(0.1)
            if verbose:
                #see verbosemax/i explanation above
                verbosei += 1
                if verbosei==verbosemax:
                    print("Downloading neighbourhood {}/{}...".format(i+1,imax+1))
                    verbosei = 0
                    verbosemax = verbosemax + 1 + math.floor(verbosemax*0.2)
            #Unpack the input
            id,start,stop = inputs[i]
            try:
                handle = Entrez.efetch(id=id, db="nuccore", rettype="gb", retmode="xml", seq_start=start, 
                                       seq_stop=stop, **kwargs)
                for line in handle:
                    if ((XML) and ("<?xml" in line)):
                        continue
                    elif ((XML) and ("<!DOCTYPE" in line)):
                        continue
                    chunkcontent.append(line)
                i+=1
            except:
                if verbose:
                    print("Failed, retrying...")
                continue
                #The transfer failed, just try again
            for line in chunkcontent:
                output.write(line)
        if XML:
            output.write("\n</ReportSetSet>\n")
        output.flush()
        output.close()
        if verbose:
            print("Complete. Downloaded {}/{} files.".format(i+1, imax+1))
    return(filepath)
#
def parse_ipgxml(filepath):
    counter = collections.Counter()
    with gzip.open(filepath, mode="rt") as handle:
        #Starting vars:
        iptAll = {} #All identicalProteins in dataset
        scAll  = {} #All scaffolds in dataset
        txAll  = {} #All taxons in dataset
        #XML parsing loop:
        for event, elem in ET.iterparse(handle, events=("start",)):
            #Loop triggers at the start of a given tag (I hope, anyway)
            #The tag-processing elifs should be sorted from deepest 
            #    (=most common) tags.
            if elem.tag == "CDS":
                scName = elem.get("accver").split(".")[0]
                #Scaffold check
                if scName not in scAll:
                    #If the scaffold hasn't been created, create it
                    #First we need to check if its master taxon exists though
                    txID = elem.get("taxid")
                    if txID not in txAll:
                        #If the taxon hasn't been created, create it
                        txNew = dframe.Taxon(
                            sciname=elem.get("org"),
                            taxid=txID
                        )
                        txAll[txNew.taxid] = txNew
                    #Now add the new scaffold
                    scNew = dframe.Scaffold(
                        accession=scName,
                        strand=elem.get("strand"),
                        strain=elem.get("strain"),
                        taxon=txAll[txID],
                    )
                    scAll[scNew.accession] = scNew
                #Add feature
                ftNew = dframe.Feature(
                    start=elem.get("start"),
                    stop=elem.get("stop"),
                    type="cds",
                    ref=ptNew,
                    scaffold=scAll[scName],
                    reference=ptNew,
                )
                #TODO: This will need to be changed if/ONCE the way
                #    features are added changes.
            elif elem.tag == "CDSList":
                pass
            elif elem.tag == "Protein":
                ptNew = dframe.Protein(
                    name=elem.get("name"),
                    accession=elem.get("accver").split(".")[0],
                    type="cds",
                )
                iptNew.add_protein(ptNew)
            elif elem.tag == "ProteinList":
                pass
            elif elem.tag == "IPGReport":
                #This is a set of identical proteins
                iptNew = dframe.IdenticalProteinSet(
                    accession=elem.get("ipg"),
                )
                iptAll[iptNew.accession] = iptNew
            else:
                pass
    return(txAll, scAll, iptAll)
#
def parse_ipgxml_i(filepath, queries=None, index=None):
    with gzip.open(filepath, mode="rt") as handle:
        #Starting vars:
        if index is None:
            #Providing an index keyword argument lets us extend an existing index
            index  = dframe.Index()
        skip   = False
        #XML parsing loop:
        for event, elem in ET.iterparse(handle, events=("start",)):
            #Loop triggers at the start of a given tag (I hope, anyway)
            #The tag-processing elifs should be sorted from deepest 
            #    (=most common) tags.
            if skip and elem.tag != "IPGReport":
                continue
            if elem.tag == "CDS":
                scName = elem.get("accver").split(".")[0]
                #Scaffold check
                if scName not in index.scAll:
                    #If the scaffold hasn't been created, create it
                    #First we need to check if its master taxon exists though
                    txID = elem.get("taxid")
                    if txID not in index.txAll:
                        #If the taxon hasn't been created, create it
                        txNew = dframe.Taxon(
                            sciname=elem.get("org"),
                            taxid=txID,
                            index=index,
                        )
                    #Now add the new scaffold
                    scNew = dframe.Scaffold(
                        accession=scName,
                        strand=elem.get("strand"),
                        strain=elem.get("strain"),
                        taxon=index.txAll[txID],
                    )
                #Add feature
                ftNew = dframe.Feature(
                    start=elem.get("start"),
                    stop=elem.get("stop"),
                    type="cds",
                    ref=ptNew,
                    scaffold=index.scAll[scName],
                    reference=ptNew,
                )
                #TODO: This will need to be changed if/ONCE the way
                #    features are added changes.
            elif elem.tag == "CDSList":
                pass
            elif elem.tag == "Protein":
                ptNew = dframe.Protein(
                    name=elem.get("name"),
                    accession=elem.get("accver").split(".")[0],
                    iprotein=iptNew,
                    type="cds",
                )
            elif elem.tag == "ProteinList":
                pass
            elif elem.tag == "IPGReport":
                ipgAcc = elem.get("ipg")
                if queries is None:
                    #If we're not filtering by querylist, just skip
                    pass
                elif ipgAcc not in queries:
                    #If the ipg is not in queries, just keep iterating
                    #This is likely to come up more often in bigger datasets (maybe?)
                    skip = True
                    if len(queries)==0:
                        #If there are no more queries, break the iteration
                        #This'd ideally exec after parsing each matching query
                        break
                    continue
                else:
                    #Otherwise, just 
                    skip = False
                    queries.remove(ipgAcc)
                #This is a new set of identical proteins
                iptNew = dframe.IdenticalProteinSet(
                    accession=ipgAcc,
                    index=index,
                )
            else:
                pass
    # * Once parsing is complete, verify all the data elements
    #   We want to do this to ensure that there aren't branches
    #   with no underlying features.
    #   We can't run detachecks during parsing since the data
    #   structure isn't finalized yet.
    for sc in [x for x in index.scAll.values()]:
        sc.detacheck()
    for tx in [x for x in index.txAll.values()]:
        tx.detacheck()
    for pt in [x for x in index.ptAll.values()]:
        pt.detacheck()
    for ipt in [x for x in index.iptAll.values()]:
        ipt.detacheck()
    failed = queries
    return(index, failed)
#
def parse_ipgxml_basic(filepath):
    #Iterates through an ipgxml and returns a dict of values 
    #   for each coding sequence(cds)
    with gzip.open(filepath, mode="rt") as handle:
        #XML parsing loop:
        for event, elem in ET.iterparse(handle, events=("start",)):
            if elem.tag == "CDS":
                feature = {
                    "fttype": "cds",
                    "ftstart": int(elem.get("start")),
                    "ftstop": int(elem.get("stop")),
                    "ftstrand": elem.get("strand"),
                    "ptacc": ptAcc,
                    "ptname": ptName,
                    "iptacc": iptAcc,
                    "sciname": elem.get("org"),
                    "scacc": elem.get("accver").split(".")[0],
                    "txid": elem.get("taxid"),
                    "txstrain": elem.get("strain"),
                }
                yield(feature)
            elif elem.tag == "CDSList":
                pass
            elif elem.tag == "Protein":
                ptName = elem.get("name"),
                ptAcc = elem.get("accver").split(".")[0]
            elif elem.tag == "ProteinList":
                pass
            elif elem.tag == "IPGReport":
                iptAcc = elem.get("ipg")
            else:
                pass
#

def parse_neighbor_gb_legacy(filepath, offset):
    #Reads a genbank XML file.
    #  This parser could originally read through multiple records inside a single XML,
    #  but this has been changed due to problems with keeping track of the offset.
    #This parser *needs* to know the offset of the genbank file relative to the contig, as
    #  without it, the neighbourhood will be misaligned relative to the reference, and
    #  may end up overlapping with other neighbourhoods in the same contig.
    #  By as of writing, the offset (or rather the start/stop positions of the neighbourhood)
    #  are listed both in genbank(.gb) filenames and in the _index.txt
    def parse_position(raw, position_offset):
        #Handles (some) of the shapes position data can manage
        #Likely can't handle anything with introns or otherwise eukaryotic
        #TODO:
        #The current implementation is painfully hacky, but it stays until I can figure out
        #  how to make python process functional statements in strings without using eval
        complement=False
        raw=raw.replace(">","")
        raw=raw.replace("<","")
        if "complement" in raw:
            complement=True
            raw = raw.lstrip("complement(").rstrip(")")
        if "join" in raw:
            raw = raw.lstrip("join(").rstrip(")").split(",")
            raw = "..".join([raw[0].split("..")[0], raw[1].split("..")[1]])
        raw=raw.split("..")
        try:
            #TODO: A bizzare behaviour from the xml.etree parser occurs where
            #  an element.tag gets read as <1 instead of whatever it should be
            #  I have no idea why this happens or how to stop it--
            #  So for now, I just handle the exceptions.
            start = int(raw[0]) + position_offset
            stop  = int(raw[1]) + position_offset        
            return(start,stop)
        except:
            return None
    
    
    #Recorded qualifier tags:
    recquals = set(["product", "protein_id", "translation"])
    feature = None
    record = None
    qname = None
    with gzip.open(filepath, mode="rt") as handle:
        for event, elem in ET.iterparse(handle, events=("start","end")):
            #Handling qualifiers
            if event=="end" and elem.tag=="GBQualifier_value":
                if qname:
                    feature[qname] = elem.text
                    qname = None
            elif event=="end" and elem.tag=="GBQualifier_name":
                if elem.text in recquals:
                    qname = elem.text
            #/Handling qualifiers
            elif event=="end" and elem.tag=="GBFeature_location":
                res = parse_position(elem.text, offset)
                if res is None:
                    res = (-1, -1)
                    print("Encountered bizzarre error while parsing sequence {}.".format(record["accession"]))
                feature["start"],feature["stop"] = res
            elif event=="end" and elem.tag=="GBFeature_key":
                feature["type"] = elem.text.lower()
            elif event=="start" and elem.tag=="GBFeature":
                #Integrate previous feature
                if feature:
                    if feature["type"] != "source":
                        record["features"].append(feature)
                #Create new feature
                feature = {
                    "type": None,
                    "start": None,
                    "stop": None,
                    "product": None,
                    "protein_id": None,
                    "translation": None,
                    #Also includes any recquals declared above
                }
            elif event=="start" and elem.tag=="GBSeq_feature-table":
                record["features"] = []
            elif event=="end" and elem.tag=="GBSeq_organism":
                record["sciname"] = elem.text
            elif event=="end" and elem.tag=="GBSeq_primary-accession":
                record["accession"] = elem.text
            elif event=="start" and elem.tag=="GBSeq":
                record = {
                    "accession": None,
                    "sciname": None,
                    "features": None,
                }
        return(record)
#
def process_neighbor_gb_record(record, index):
    #this function takes a single record from the parse_neighbor_gb() function
    #  and adds all coding sequences from it to the data structure (index)
    #  
    
    #TODO: Rework this function to completely wrap the
    #      dbdl.parse_neighbor_gb() generator rather than be called 
    #      per record in order to keep track of relevant variables,
    #      and to ease error reporting
    
    #First, try getting the scaffold this record corresponds to
    sc = index.scAll.get(record["accession"])
    if sc == None:
        #if the scaffold is not in the index, exit
        return(False)
    
    #Second, get or create our kitchen sink iprotein to dump all of
    #  our neighbourhood proteins into.
    #  TODO: This is a hack and can break dframe in certain use cases. Fix.
    ipt = index.iptAll.get("Unsorted")

    
    #start iterating over the features in the record
    for rfeat in record["features"]:
        if rfeat["protein_id"] is None:
            #  if we don't have the accession code for the protein, it's pointless
            #    to process it -- skip
            #  TODO: Isn't this identical to checking if type=="cds"?
            #        If not, maybe there should be some kind of error reporter
            continue
        
        rfeat["protein_id"] = rfeat["protein_id"].split(".")[0]
        
        if rfeat["type"] == "cds":
            #If the feature is a coding sequence, we process it
            
            #first, try getting the protein ID from index
            if rfeat["protein_id"] not in index.ptAll:
                #make up an iprotein
                if rfeat["protein_id"] in index.iptAll:
                    ipt = index.iptAll[rfeat["protein_id"]]
                else:
                    ipt = dframe.IdenticalProteinSet(rfeat["protein_id"], index)
                #If our reference hasn't been added yet, create it
                ref = dframe.Protein(
                    rfeat["protein_id"],
                    ipt,
                    type=rfeat["product"],
                    name=rfeat["protein_id"],
                    seq=rfeat["translation"],
                )
            else:
                ref = index.ptAll[rfeat["protein_id"]]
                ref.seq = rfeat["translation"]
                ref.type = rfeat["product"]
            ft = dframe.Feature(sc, ref, rfeat["start"], 
                                rfeat["stop"], rfeat["type"])
    return(True)
#
def index_ipgxml(filepath):
    with gzip.open(filepath, mode="rt") as handle:
        #Starting vars:
        pt_to_ipt  = {} #Protein names as keys linked to iprotein ids
        #XML parsing loop:
        for event, elem in ET.iterparse(handle, events=("start",)):
            if elem.tag == "Protein":
                ptAcc = elem.get("accver").split(".")[0]
                if ptAcc in pt_to_ipt:
                    print("WARNING: IPG file contains duplicate protein ({})".format(ptAcc))
                pt_to_ipt[ptAcc] = iptAcc
            elif elem.tag == "IPGReport":
                iptAcc = elem.get("ipg")
    return(pt_to_ipt)
