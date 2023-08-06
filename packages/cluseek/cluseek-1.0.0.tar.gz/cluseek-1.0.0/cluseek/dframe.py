import gc
import re
from collections import Counter
import enum

# This file describes most of the common classes used to store
#   the data being processed.


# * * * Front/Nucleotide Tree
# These classes describe the position of a given nucleotide sequence
#  EG. CodingSequence1 is on Scaffold5, which is a sequence from Taxon319's genome
#
# When adding elements to the data structure without calling the constructor, 
#   always use the add_[element] method to add elements lower in the hierarchy 
#   to ensure interconnectedness.

class Strand(enum.Enum):
    PRIMARY = "+"
    COMPLEMENTARY = "-" #This is the reverse complement
    BOTH = "0" #This is the default if you don't care about strandedness
    

class Root():
    def __init__(self):
        super().__init__()
        self.txAll  = {}
        self.scAll  = {}
        self.ptAll  = {}
        self.iptAll = {}
        self.detached = False
    def scAll(self):
        scAll = {}
        for tx in self.txAll.values():
            scAll.update(tx.scs)
        return(scAll)
    def ptAll(self):
        ptAll = {}
        for ipt in sself.iptAll.values():
            ptAll.update(ipt.pts)
        return(ptAll)
    def detach(self):
        #The detach method disintegrates the data structure of a given element
        
        if self.detached:
            return
        self.detached = True
        for tx in [x for x in self.txAll.values()]:
            tx.detach()
        for ipt in [x for x in self.iptAll.values()]:
            ipt.detach()
        del self
        #Force a garbage collection pass after detaching everything.
        #    This likely won't release that much memory to the os right away,  
        #    but it should save us some memory fragmentation later (maybe?).
        #Atlernative solution is to just subprocess anything that handles
        #    big piles of data and delete the process afterwards.
        #    This'll definitely free up all the memory heaps, but is also
        #    a pain for different reasons.
        gc.collect()
    def detacheck_all(self):
        for sc in [x for x in self.scAll.values()]:
            sc.detacheck()
        for tx in [x for x in self.txAll.values()]:
            tx.detacheck()
        for pt in [x for x in self.ptAll.values()]:
            pt.detacheck()
        for ipt in [x for x in self.iptAll.values()]:
            ipt.detacheck()
class Taxon():
    sciname_pattern = re.compile(r"(?P<genus>\[?[a-zA-Z0-9]+\[?)( (?P<species>(Sp. )?[a-zA-Z0-9]+))?( (?P<strain>.+))?")
    def __init__(self, taxid, root, sciname=None, strain=None):
        super().__init__()
        # * Non-args
        self.scs = {}
        self.detached = False
        # * Mandatory args
        self.taxid = taxid
        self.root = root
        self.root.txAll[self.taxid] = self
        # * Optional args
        self.sciname = sciname
        
        match = re.match(self.sciname_pattern, self.sciname)
        if match is None and sciname: # If we passed sciname, but it didn't pass parser
            print(f"Failed matching sciname: {self.sciname}")
        else:
            self.genus = match["genus"]
            self.species = match["species"]
            self.strain = match["strain"]
        #self.strain = strain
    def add_scaffold(self, scaffold):
        if scaffold.accession in self.scs:
            warnstr = "WARNING: Scaffold {} already in taxon {}. Overwriting..."
            self.scs[scaffold.accession].detach()
            print(warnstr.format(scaffold.accession, self.taxid))
        self.scs[scaffold.accession] = scaffold
        scaffold.tx = self
    def detach(self):
        if self.detached:
            return
        self.detached = True
        for sc in [x for x in self.scs.values()]:
            sc.detach()
        del self.root.txAll[self.taxid]
        del self
    def detacheck(self):
        if len(self.scs)==0:
            self.detach()
class Scaffold():
    #Roughly corresponds to a genbank sequence record
    def __init__(self, accession, taxon):
        super().__init__()
        # * Non-args
        self.fts = {}
        self.detached = False
        self.tx = None
        # * Mandatory args
        self.accession = accession
        taxon.add_scaffold(self)
        self.tx.root.scAll[self.accession] = self
    def detach(self):
        if self.detached:
            return
        self.detached = True
        for ft in [x for x in self.fts.values()]:
            ft.detach()
        del self.tx.root.scAll[self.accession]
        del self.tx.scs[self.accession]
        self.tx.detacheck()
        del self
    def detacheck(self):
        if len(self.fts)==0:
            self.detach()
    #def __repr__(self):
    #    pass
    #def __str__(self):
    #    pass
    pass
class Feature():
    #Sequence feature, attached to a Sequence Record
    def __init__(self, scaffold, reference, start, stop, fttype, strand, attach=True):
        super().__init__()
        # * Non-args
        self.detached = False
        # * Mandatory args
        self.start = start
        self.stop  = stop
        self.type  = fttype #Possible values: "cds", "genecluster"
        
        assert strand in Strand, "Strand not specified for a coding sequence!"
        self.strand = strand
        
        #The only real way of hooking up sc/refs right now        
        #TODO: The following will break horribly if a non-accession 
        #   element is referred to by a feature.
        #   Possibly use an "add_as_feature()" method that 
        #   adds features implicitly.
        self.sc    = scaffold
        self.ref   = reference
        if attach:
            self.sc.fts[self.ref.accession] = self
            self.ref.fts[self.sc.accession] = self
        # * Optional args
        pass
    def __repr__(self):
        return("Feature ({}) from {} to {} on {}".format(
                                                self.type,
                                                self.start, 
                                                self.stop, 
                                                self.sc.accession))
    def __str__(self):
        return("Feature ({}) from {} to {} on {}".format(
                                                self.type,
                                                self.start, 
                                                self.stop, 
                                                self.sc.accession))
    def is_inside(self, ft):
        #Check if this feature is inside another feature
        #This is useful when we use features to define regions
        if self.sc is not ft.sc:
            print("Error: Features {} and {} are not on the same scaffold!")
            return(None)
        if ((ft.start <= self.start) and (ft.stop >= self.stop)):
            #"If the other feature starts sooner and ends later"
            return(True)
        else:
            return(False)
    def overlaps(self, ft):
        #Returns True of features overlap
        if self.sc is not ft.sc:
            print("Error: Features {} and {} are not on the same scaffold!")
            return(None)
        if ((self.start <= ft.stop <= self.stop)
          or (ft.start <= self.stop <= ft.stop)):
            #If the stop of either feature is within the bounds
            #of the other, they're overlapped.
            return(True)
    def distance_from(self, ft):
        #Calculates distance between features.
        if self.overlaps(ft):
            return(None)
        #We don't need to do a check if the features are on the
        # same scaffold, because self.overlaps() already does that.
        #
        d1 = ft.start - self.stop
        d2 = self.start - ft.stop
        #If the features aren't overlapping, either d1 or d2 will
        # be negative.
        return(max(d1, d2))
    def detach(self):
        if self.detached:
            return
        self.detached = True
        del self.sc.fts[self.ref.accession]
        del self.ref.fts[self.sc.accession]
        self.sc.detacheck()
        self.ref.detacheck()
        del self
    def length(self):
        return(self.stop-self.start)
# Search Result
class GeneticRegion(Feature):
    def __init__(self, scaffold, start, stop, hit_score=None):
       # Initialize the superclasss.   
       #    We'll be using attach=False until/unless
       #    an AbstractGeneCluster class gets written
       #    to track multiple instances of the same
       #    cluster (eg. APD cluster in multiple species)
        super().__init__(scaffold=scaffold, start=start, strand=Strand.BOTH,
                         stop=stop, reference=self, fttype="genecluster",
                         attach=False)
        self.hit_score = hit_score
    @property
    def fts(self):
        fts = {}
        for ftname in self.sc.fts:
            ft = self.sc.fts[ftname]
            if ft.is_inside(self):
                fts[ftname] = ft
        return(fts)

# * * * Back/Protein Tree
# These classes help cover the relationship between peptide
#  sequences -- identical proteins, homologous proteins, etc.
#  
# Included are also other classes like Regions -- all share
# the trait of being linked from the main tree through Feature.ref
class Protein():
    def __init__(self, accession, iprotein, seq=None, name=None, type=None):
        super().__init__()
        # *Non-arguments
        self.fts   = {}   # Coding sequences
        self.homs  = []   # Homologies to
        self.qhoms = []   # Homologies 
        self.detached = False
        self.ipt   = None #Declaring var
        self.cluster = None #Declaring var
        # *Mandatory args
        self.accession = accession.split(".")[0] # GenBank Accession
        iprotein.add_protein(self)
        self.ipt.root.ptAll[self.accession] = self
        # *Optional args
        self.name  = name # (Slightly more) human-readable name
        self.type  = type # Description, usually from GenBank
        self.seq   = seq  # Amino acid sequence
    def __repr__(self):
        return(f"Protein {self.accession}, {self.type}, {self.name}")
    def __str__(self):
        return(self.__repr__())
    def detach(self):
        if self.detached:
            return
        self.detached = True
        for ft in [x for x in self.fts.values()]:
            ft.detach()
        del self.ipt.root.ptAll[self.accession]
        del self.ipt.pts[self.accession]
        self.ipt.detacheck()
        del self
    def detacheck(self):
        if len(self.fts)==0:
            self.detach()
    #def __repr__(self):
    #    pass
    #def __str__(self):
    #    pass
    pass
class IdenticalProteinSet():
    #Roughly corresponds to the genbank ipg record
    def __init__(self, accession, root, proteins=[]):
        super().__init__()
        # *Non-args
        self.pts = {}
        self.detached = False
        #fts - features are generated via self.fts()
        # *Mandatory arguments
        self.accession = accession
        self.root = root
        if self.accession in self.root.iptAll:
            print("WARNING: iProtein {} already in root, overwriting...".format(self.accession))
        self.root.iptAll[self.accession] = self
        # *Optional args
        for pt in proteins:
            self.add_protein(pt)
    def add_protein(self, protein):
        if protein.accession in self.pts:
            print("WARNING: Protein {} already in iProtein {}, overwriting...".format(protein.accession, self.accession))
            self.pts[protein.accession].detach()
        self.pts[protein.accession] = protein
        protein.ipt = self
    def fts(self):
        #TODO: DEPRICATED
        #Inaccurate if there are multiple instances of the same protein on the same scaffold.
        #It shouldn't really be possible normally, but hacking things opens it to bugs
        #TODO: return an iterator instead of a dict, that's the only way
        myFeatures = {}
        for pt in self.pts.values():
            myFeatures.update(pt.fts)
        return(myFeatures)
    def __getitem__(self,item):
        return(self.pts[item])
    def __contains__(self,item):
        return(item in self.pts)
    def detach(self):
        if self.detached:
            return
        self.detached = True
        for pt in [x for x in self.pts.values()]:
            pt.detach()
        del self.root.iptAll[self.accession]
        del self
    def detacheck(self):
        if len(self.pts)==0:
            self.detach()
    #def __repr__(self):
    #    pass
    #def __str__(self):
    #    pass
    pass
#
class ReferenceDummy():
    def __init__(self):
        super().__init__()
        self.accession = None
        self.fts = {}
    def __repr__(self):
        return("ReferenceDummy")
    def __str__(self):
#

        return("ReferenceDummy")


# Classes for protein clustering based on global alignment identity
# NOTE: Due to rewrites, "protein" can refer to both a protein, or a pcluster

def get_member_ident(member):
    if isinstance(member, ProteinCluster):
        return(member._id)
    elif isinstance(member, Protein):
        return(member.accession)
    else:
        assert True, "Member objects can be either Protein or ProteinCluster"
class PClusteringResult():
    def __init__(self, root, identity=None, evalue=None):
        super().__init__()
        self.identity = identity #%identity to which members were clustered
        self.evalue = evalue #Evalue to which members were clustered
        self.clusters = {}
        self.root = root
        self.member_to_cluster = {}
    def add_cluster(self, cluster):
        cluster.clustering = self
        self.clusters[cluster._id] = cluster
        for member in cluster.members.values():
            self.add_member(member)
    def remove_cluster(self, cluster):
        del self.clusters[cluster._id]
        for member_id in cluster.members:
            del self.member_to_cluster[member_id]
    def add_member(self, member, cluster):
        #Add a member to the central dictionary
        #   to make it possible to tell which member is in
        #   which cluster without attaching the information
        #   to the members.
        self.member_to_cluster[get_member_ident(member)] = cluster
    def get(self, _id):
        if _id not in self.clusters:
            #print(f"Making cluster {_id}")
            return(ProteinCluster(_id, self))
        else:
            return(self.clusters[_id])
    def merge(self, children):
        master = ProteinCluster("+"+children[0]._id, self)
        self.add_cluster(master)
        for child in children:
            # Shouldn't need to entirely remove cluster,
            #   since all its members entries in the
            #   member to cluster dict will be overwritten
            #self.remove_cluster(child)
            del self.clusters[child._id]
            master.add_member(child)
    def unmerge(self, master):
        for child in master.member_subclusters.values():
            self.add_cluster(child)
            child.master = None
        del self.cluster[master._id]
class ProteinCluster():
    def __init__(self, _id, clustering):
        super().__init__()
        #Add clustering
        self._id = _id
        self.clustering = clustering
        self.members = {}
        self.member_subclusters = {}
        self.member_identities = {}
        self.member_evalues = {}
        self._master = None
        self.centroid = None #Only valid for globally aligned clusters
        #The following must always come *after* self._id is set
        self.clustering.add_cluster(self)
    def add_member(self, member, identity=None, evalue=None):
        if isinstance(member, ProteinCluster):
            #If it's a subcluster, wsrite it down
            self.member_subclusters[get_member_ident(member)] = member
            member.master = self
            #Then add the subcluster's members to own
            for subcluster_member in member.members.values():
                self.add_member(subcluster_member)
                #This method is not as fast, but probably not by
                #   as much since we need to make the 
                #   PClusteringResult.member_to_cluster dictionary work
            #We don't record identities/evalues since superclusters
            #   are most likely a heterogenous mess anyway:
            #self.member_identities.update(member.member_identities)
            #self.member_evalues.update(member.member_evalues)
            member.on_merge()
        else:
            # Otherwise, assume it's a protein, add it to the cluster
            self.members[get_member_ident(member)] = member
            self.member_identities[get_member_ident(member)] = identity
            self.member_evalues[get_member_ident(member)] = evalue
            # Register the member with the Results object
            self.clustering.add_member(member, self)
    def _get_composition(self):
        composition = Counter()
        for member in self.members.values():
            if isinstance(member, Protein):
                #If it's a protein, get the type
                composition[member.type] += 1
            elif isinstance(member, ProteinCluster):
                #If it's a protein cluster, count the types inside of it
                composition.update(member._get_composition())
            else:
                assert f"ProteinCluster has undefined member: ({type(member)})"
        return(composition)
    
    @property
    def master(self):
        if self._master:
            return self._master
        else:
            return self
    @master.setter
    def master(self, master):
        self._master = master
    
    def on_merge(self):
        pass
    def on_unmerge(self):
        pass