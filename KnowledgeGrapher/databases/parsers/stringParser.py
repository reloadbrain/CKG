#########################
#   STRING like DBs     #
#########################
def getSTRINGMapping(source = "BLAST_UniProt_AC", download = True):
    mapping = defaultdict(set)
    url = config.STRING_mapping_url
    
    directory = os.path.join(config.databasesDir, "STRING")
    fileName = os.path.join(directory, url.split('/')[-1])

    if download:
        downloadDB(url, "STRING")
    
    f = os.path.join(directory, fileName)
    mf = gzip.open(f, 'r')
    first = True
    for line in mf:
        if first:
            first = False
            continue
        data = line.decode('utf-8').rstrip("\r\n").split("\t")
        stringID = data[0]
        alias = data[1]
        sources = data[2].split(' ')
        if source in sources:
            mapping[stringID].add(alias)
        
    return mapping

def parseSTRINGLikeDatabase(mapping, db= "STRING", download = True):
    string_interactions = set()
    cutoff = config.STRING_cutoff
    
    if db == "STITCH":
        evidences = ["experimental", "prediction", "database","textmining", "score"]
        relationship = "COMPILED_INTERACTS_WITH"
        url = config.STITCH_url
    elif db == "STRING":
        evidences = ["experimental", "prediction", "database","textmining", "score"]
        relationship = "COMPILED_TARGETS"
        url = config.STRING_url

    directory = os.path.join(config.databasesDir, db)
    fileName = os.path.join(directory, url.split('/')[-1])

    if download:
        downloadDB(url, db)
    
    f = os.path.join(directory, fileName)
    associations = gzip.open(f, 'r')
    first = True
    for line in associations:
        if first:
            first = False
            continue
        data = line.rstrip("\r\n").split()
        intA = data[0]
        intB = data[1]
        scores = data[2:]
        fscores = [str(float(score)/1000) for score in scores]
        if intA in mapping and intB in mapping and fscores[-1]>=cutoff:
            for aliasA in mapping[intA]:
                for aliasB in mapping[intB]:
                    string_interactions.add((aliasA, aliasB, relationship, "association", db, ",".join(evidences), ",".join(fscores[0:-1]), fscores[-1]))
        elif db == "STITCH":
            if intB in mapping and fscores[-1]>=cutoff:
                aliasA = intA
                for aliasB in mapping[intB]:
                    string_interactions.add((aliasA, aliasB, relationship, "association", db, ",".join(evidences), ",".join(fscores[0:-1]), fscores[-1]))
    return string_interactions
