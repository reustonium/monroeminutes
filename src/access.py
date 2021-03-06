import json

from time import strftime
from pymongo import MongoClient

from searchapi import Search

class Access(object):

    def __init__(self,uri='mongodb://localhost:27017/',db='monroeminutesdb',DEBUG=False):

        self.DEBUG = DEBUG

        if self.DEBUG:
            print "Starting Access() INIT ..."

        self.dbclient = MongoClient(uri)
        self.db = self.dbclient[db]
        self.documents = self.db['documents']
        self.entities = self.db['entities']
        self.orgs = self.db['orgs']
        self.runs = self.db['runs']
        self.statuses = self.db['statuses']
        self.searches = self.db['searches']

        self.searchapi = Search()

        if self.DEBUG:
            print "Access() INIT completed successfully."

    def addentity(self,entity):
    
        #
        # TODO: sanity check entity input has correct fields within dict
        #

        """
        
        entity = {
            'name':'Brighton, NY',
            'description':'Town of Brighton, NY',
            'website':'http://www.townofbrighton.org/',
            'creationdatetime':'2014-02-23 21:24:26',
        }

        """


        # add entity to the database
        entity['creationdatetime'] = str(strftime("%Y-%m-%d %H:%M:%S"))
        self.entities.insert(entity)

        return True

    def getentities(self):

         # get all of the entities
        results = self.entities.find()
        docs = []
        for result in results:
            docs.append(result)
        return docs

    def addorg(self,org):

        #
        # TODO: snity check org input has correct fields within dict
        #

        """

        org = {
            'name': 'Brighton Town Board',
            'description': 'Brighton, NY Town Board',
            'matchs': [
                'town board',
                'brighton',
            ]
            'entityid': ObjectID(' ... '),
            'creationdatetime': '2014-03-14 22:01:30',
        }

        """

        org['creationdatetime'] = str(strftime("%Y-%m-%d %H:%M:%S"))
        self.orgs.insert(org)

        return True

    def setdocorg(self,doc,orgid):

        # update the orgid field
        doc['orgid'] = orgid

        origdoc = doc

        # update the doc in the database
        newdoc = self.documents.update(
            { 'docurl': doc['docurl'] },
            doc,
        );

        return origdoc

    def getorgs(self):

        # get all of the orgs from the database
        results = self.orgs.find()
        docs = []
        for result in results:
            docs.append(result)
        return docs

    def geturls(self):

        # get all of the URLs from the engities 
        results = self.getentities()
        docs = []
        for result in results:
            docs.append(result['website'])
        return docs

    def logrun(self,stats):

        # log the scraper run tot he database
        success = True
        try:
            self.runs.insert(stats)
        except:
            success = False
        return success

    def getruns(self):

        # get all the runs
        try:
            data = self.runs.find()
            scraperruns = []
            for d in data:
                scraperruns.append(d)
        except:
            scraperruns = None
        return scraperruns

    def logstatus(self, scraperid, statuspacket):

        #try:
        if True:

            # update the dict to include the scraper id, as we will be
            # querying off of that
            statuspacket['scraperid'] = scraperid
            statuspacket['date'] = str(strftime("%Y-%m-%d"))
            statuspacket['time'] = str(strftime("%H:%M:%S"))

            # log the status of the scraper
            result = self.statuses.update(
                { 'scraperid': scraperid },
                statuspacket,
                True, # upsert
            )

            success = True

        #except:
        #    success = False

        return success

    def getstatuses(self):

        #try:
        if True:    
            results = self.statuses.find()
            statuses = []
            for result in results:
                statuses.append(result)

            #success = True

        #except:
        #    statuses = []
        #    #success = False

        return statuses

    def getdocbydocurl(self,docurl):

        # get the document by docurl.  If it does not exist, it will be None

        try:
            result = self.documents.find_one({'docurl': docurl})
        except:
            result = None

        return result

    def adddoc(self,docurl,linktext,docname,filename,scrapedatetime,urldata):

        # see if we already have the doc in the database
        result = self.documents.find_one({'docurl': docurl})

        # if the doc doesn't exist, create it
        if result == None:
            doc = {
                'docurl': docurl,
                'linktext': linktext,
                'docname': filename,
                'filename': docname,
                'scrapedatetime': scrapedatetime,
                'being_converted': False,
                'converted': False,
                'being_processed': False,
                'processed': False,
                'pdftext': '',
                'pdfhash': '',
                'created': '',
                'minutesdate': '',
                'orgid': '',
                'entityid': urldata['entityid'],
                'urldata': urldata,
            }
            docid = self.documents.insert(doc)
        else:
            # doc already in db
            docid = None
            pass

        return docid

    def getdoc(self,docurl):

        # get the entry based on the docurl
        result = self.documents.find_one( {'docurl': docurl} )
        return result

    def getdocsbyentityid(self,entityid):
       
        # get the entries based on the entity
        results = self.documents.find( {'entityid': entityid} )
        docs = []
        for result in results:
            docs.append(result)
        return docs

    def getdocs(self):

        # return all docs in the database
        results = self.documents.find()
        docs = []
        for result in results:
            docs.append(result)
        return docs

    def getconverted(self):

        # return all docs in the database
        results = self.documents.find({
            'converted':True,
        })
        docs = []
        for result in results:
            docs.append(result)
        return docs

    def _clearall(self):

        # blow away the entire database
        self.documents.remove()
        self.entities.remove()
        self.runs.remove()
        self.orgs.remove()

        return True

    def getunprocessed(self,entityid=None):

        if entityid == None:
            query = {
                'being_processed': False,
                'processed': False,
            }
        else:
            query = {
                'being_processed': False,
                'processed': False,
                'entityid': entityid,
            }

        # get the doc, and mark the 'being_processed' flag
        doc = self.documents.find_and_modify(
            query=query,
            update={
                '$set':{
                    'being_processed': True
                },
            },
            full_response=False,
            multi=False,
        )
        return doc

    def setprocessed(self,docurl):

        # get the doc, and mark the 'being_processed' flag
        doc = self.documents.find_and_modify(
            query={
                'docurl':docurl
            },
            update={
                '$set': {
                    'being_processed': False,
                    'processed': True
                },
            },
            full_response=False,
            multi=False,
        )
        return doc

    def setprocessdata(self,entityid,orgid,minutesdate):

       # update the doc with the pdftext, and return the new doc
        doc = self.documents.find_and_modify(
            query={
                'docurl': docurl
            },
            update={
                '$set': {
                    'entityid': entityid,
                    'orgid': orgid,
                    'minutesdate': minutesdate,
                }
            },
            full_response=False,
            multi=False,
        )
        return doc

    def getunconverted(self,entityid=None):
   
        if entityid == None:
            query = {
                'being_converted': False,
                'converted': False,
            }
        else:
            query = {
                'being_converted': False,
                'converted': False,
                'entityid': entityid,
            }
 
        # get the doc, and mark the 'being_processed' flag
        doc = self.documents.find_and_modify(
            query=query,
            update={
                '$set':{
                    'being_converted': True
                }
            },
            full_response=False,
            multi=False,
        )
        return doc

    def resetprocessed(self):

        docs = self.getdocs()

        for d in docs:

            doc = self.documents.find_and_modify(
                query = {
                    '_id': d['_id']
                },
                update={
                    '$set':{
                        'being_processed': False,
                        'processed': False,
                    }
                },
                full_response=False,
                multi=True,
            )

        return True

    def resetconverted(self,entityid):

        doc = self.documents.find_and_modify(
            query={
                'entityid': entityid
            },
            update={
                '$set':{
                    'being_converted': False,
                    'converted': False,
                }
            },
            full_response=False,
            multi=True,
        )
        return True

    def setconverted(self,docurl):

        # get the doc, and mark the 'being_processed' flag
        doc = self.documents.find_and_modify(
            query={
                'docurl': docurl
            },
            update={
                '$set': {
                    'being_converted': False, 
                    'converted': True,
                }
            },
            full_response=False,
            multi=False,
        )
        return doc

    def setconvertdata(self,docurl,pdftext,pdfhash,created):

        # update the doc with the pdftext, and return the new doc
        doc = self.documents.find_and_modify(
            query={
                'docurl': docurl
            },
            update={
                '$set': {
                    'pdftext': pdftext,
                    'pdfhash': pdfhash,
                    'created': created,
                }
            },
            full_response=False,
            multi=False,
        )
        return doc

    def resetflags(self):

        # get the doc, and mark the 'being_processed' flag
        docs = self.documents.find_and_modify(
            query={
            },
            update={
                '$set':{
                    'being_converted': False,
                    'being_processed': False,
                },
            },
            full_response=False,
            multi=True,
        )

        return len(docs)

    def _resetstates(self):

        # get the doc, and mark the 'being_processed' flag
        docs = self.documents.find_and_modify(
            query={
            },
            update={
                '$set':{
                    'being_converted': False,
                    'converted': False,
                    'being_processed': False,
                    'processed': False,
                },
            },
            full_response=False,
            multi=True,
        )

        return len(docs)

    # 
    # elastic search functions
    # 

    def search(self,phrase,orgid='',entityid='',pagesize=20,page=0):

       results = self.searchapi.search(
           phrase=phrase,
           orgid=orgid,
           entityid=entityid,
           pagesize=pagesize,
           page=page
       )

       search = {
           'phrase': phrase,
           'orgid': orgid,
           'entityid': entityid,
           'datetime': str(strftime("%Y-%m-%d %H:%M:%S")),
       }
       self.searches.insert(search)

       return results

    def getsearches(self):

        docs = self.searches.find()

        results = []
        for d in docs:
            d['_id'] = str(d['_id'])
            results.append(d)

        return results

    def indexdoc(self,doc):

        """

        Note: orgid and entityid are mongodb str( ObjectID() )

        doc = {
            'docurl': 'http://henrietta.org/minutes/town_board/town_board_minutes_2014_01_23.pdf',
            'linktext': 'Minutes for Jan 23rd, 2014',
            'docname': 'town_board_minutes_2014_01_23.pdf',
            'filename: '/downloads/town_board_minutes_2014_01_23.pdf_423062309486.download',
            'scrapedatetime': '2014-02-23 21:24:26',
            'being_converted': False,
            'converted': True,
            'being_processed': False,
            'processed': True,
            'pdftext': ' ... ',
            'pdfhash': ' ... ',
            'created': '???',
            'minutesdate': '2014-01-30',
            'orgid': '507f1f77bcf86cd799439011',
            'entityid': '507f191e810c19729de860ea',
            'urldata': {
                'targeturl': 'http://henrietta.org/',
                'title': 'Henrietta, NY',
                'description': 'Town of Henrietta, NY',
                'maxlinklevel': 4,
                'creationdatetime': '2014-02-16 07:13:46',
                'doctype': 'application/pdf',
                'frequency': 10080,
            },
        }

        """

	doc.pop('_id',None) # = str(doc['_id'])
        #doc['orgid'] = " " + doc['orgid']
        #doc['entityid'] = " " + doc['entityid']

        success = self.searchapi.indexdoc(
            body=doc,
        )

        return success

if __name__ == '__main__':

    docurl='http://timduffy.me/Resume-TimDuffy-20130813.pdf'
    linktext='resume'
    docname='Resume-TimDuffy-20130813.pdf'
    filename='Resume-TimDuffy-20130813.pdf_341236213461.download'
    scrapedatetime=str(strftime("%Y-%m-%d %H:%M:%S"))
    urldata = {
        'maxlinklevel': 1, 
        'doctype': 'application/pdf', 
        'targeturl': 'http://timduffy.me',
    }

    access = Access(db='testdb')

    access.documents.remove()

    doc = access.adddoc(docurl,linktext,docname,filename,scrapedatetime,urldata)

    result = access.getunconverted()

    result = access.getdoc(docurl)

    result = access.setconverted(docurl)

    result = access.getunprocessed()

    result = access.getdoc(docurl)

    result = access.setprocessed(docurl)

    result = access.setconvertdata(docurl=docurl,pdftext="some pdf text",pdfhash='0000',created=str(strftime("%Y-%m-%d %H:%M:%S")))

    result = access.getdoc(result['docurl'])

    result = access.setprocessdata(orgid="0000",entityid="1111",minutesdate=str(strftime("%Y-%m-%d %H:%M:%S")))

    print 'done'
