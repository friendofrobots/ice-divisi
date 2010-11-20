import facebook
import auth_fb
import pickle
import sys
from csc import divisi2

class FBGraphError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Profile:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.data = data
        self.likes = []
        self.gender = None
        self.hometown = None
        self.category = None

    def __str__(self):
        self.name


class Page:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.data = None
        self.likes = None
        self.gender = None
        self.hometown = None
        self.category = data['category']

    def __str__(self):
        self.name


class FBGraph():
    def __init__(self):
        self.idtable = {}
        self.profiles = []
        self.pages = []

        self.filename = None
        self.ready = False

    def readyToExport(self):
        return self.ready

    def setReady(self):
        self.ready = True

    def exported(self):
        return self.filename

    def getProfiles():
        return self.profiles

    def getPages():
        return self.pages

    def getById(id):
        if id in self.idtable:
            return self.idtable[id]
        else:
            raise FBGraphError("That id isn't in the graph")

    def dlMe(self,graph):
        me = self.addProfileFromId('me',graph)
        self.idtable[me.id] = me
        return me

    def dlFriends(self,profileId,graph):
        count = 0
        friendData = graph.get_connections(profileId,"friends")['data']
        friends = []
        for f in friendData:
            print 'downloading friends',count,'/',len(friendData),'\r',
            sys.stdout.flush()
            while(True):
                try:
                    friend = self.addProfileFromId(f['id'],graph)
                    break
                except IOError as e:
                    print e, 'on friend', count,'/',len(friendData)
            friends.append(friend)
            count += 1
        print 'downloading friends',count,'/',len(friendData)
        return friends

    def dlLikes(self,profile,graph):
        likes = []
        while(True):
            try:
                for l in graph.get_connections(profile.id, "likes")['data']:
                    like = self.addPageFromData(l)
                    likes.append(like)
                profile.likes = likes
                break
            except IOError as e:
                print e
        return likes

    def addProfileFromId(self,profileId,graph):
        if profileId in self.idtable:
            profile = self.idtable[profileId]
        else:
            profile = Profile(graph.get_object(profileId))
            if 'gender' in profile.data:
                profile.gender = self.addPageFromData({'name':profile.data['gender'],
                                                       'category':'Gender',
                                                       'id':profile.data['gender'],
                                                       'created_time':'a long time ago'})
            if 'hometown' in profile.data:
                if profile.data['hometown']['id']:
                    profile.hometown = self.addPageFromData({'name':profile.data['hometown']['name'],
                                                             'category':'City',
                                                             'id':profile.data['hometown']['id'],
                                                             'created_time':'a while ago'})
            self.idtable[profileId] = profile
            self.profiles.append(profile)
        return profile

    def addProfilesFromId(self,profileIds,graph):
        profiles = []
        for id in profileIds:
            self.addProfileFromId(id,graph)
        return profiles

    def addPageFromData(self,pageData):
        if pageData['id'] in self.idtable:
            page = self.idtable[pageData['id']]
        else:
            page = Page(pageData)
            self.idtable[page.id] = page
            self.pages.append(page)
        return page

    def export(self,filename='fb.graph'):
        f = open(filename,'w')
        f.close()
        with open(filename,'a') as gf:
            for profile in self.profiles:
                self.add_profile_to_graph(profile,gf)
            for page in self.pages:
                self.add_page_to_graph(page,gf)
        self.filename = filename
        self.save()
        return filename

    def append_to_file(self,subject,object,rel,file):
        line = subject+'\t'+object+"\t{'freq': 1, 'score': 1, 'rel': u'"+rel+"'}\n"
        file.write(line)

    def add_profile_to_graph(self,profile,file):
        if profile.gender:
            self.append_to_file(profile.id,profile.gender.id,"hasProperty",file)
        if profile.hometown:
            self.append_to_file(profile.id,profile.hometown.id,"isFrom",file)
        for like in profile.likes:
            self.append_to_file(profile.id,like.id,"likes",file)

    def add_page_to_graph(self,page,file):
        self.append_to_file(page.id,page.category,"isA",file)

    def save(self,filename="FBGraph.pickle"):
        with open(filename,'wb') as fbgf:
            pickle.dump(self,fbgf)

    # Edit graph capabilities
    def copy(self):
        fbgraph = FBGraph()
        # TODO: fill this out
        return fbgraph
        
    def removeLikeFromProfile(self,profileId,pageId):
        profile = self.getById(profileId)
        page = self.getById(pageId)
        if page in profile.likes:
            profile.likes.remove(page)

    def addProfile(self,profile):
        self.idtable[profileId] = profile
        self.profiles.append(profile)


class DivisiFB:
    def __init__(self, filename=None):
        # Initialize FBGraph either empty or from file
        if filename:
            self.fbgraph = self.loadGraph(filename)
        else:
            self.fbgraph = FBGraph()
        self.cache = {}

    # Build Graph
    def authenticate(self):
        token = auth_fb.get_access_token()
        return facebook.GraphAPI(token)

    def downloadGraph(self):
        graph = self.authenticate()

        print 'downloading me 0/1','\r',
        sys.stdout.flush()
        me = self.fbgraph.dlMe(graph)
        myLikes = self.fbgraph.dlLikes(me,graph)
        print 'downloading me 1/1'

        friends = self.fbgraph.dlFriends('me',graph)
        count = 0
        for friend in friends:
            print 'downloading like',count,'/',len(friends),'\r',
            sys.stdout.flush()
            self.fbgraph.dlLikes(friend,graph)
            count += 1
        print 'downloading like',count,'/',len(friends)
        self.fbgraph.setReady()
        self.fbgraph.save()
        print 'finished.'

    def loadGraph(self,filename):
        with open(filename,'rb') as fbgf:
            fbg = pickle.load(fbgf)
        return fbg

    # Access Objects
    def getById(self,id):
        return self.fbgraph.idtable[id]

    def getProfiles(self):
        return self.fbgraph.getProfiles()

    def getPages(self):
        return self.fbgraph.getPages()

    # Build Matrix
    def getSMatrix(self):
        if 'smatrix' in self.cache:
            return self.cache['smatrix']
        graphFilename = self.fbgraph.exported()
        if not graphFilename:
            if not self.fbgraph.readyToExport():
                self.downloadGraph()
            graphFilename = self.fbgraph.export()
        matrix = divisi2.load(graphFilename)
        smatrix = divisi2.network.sparse_matrix(matrix, 'nodes', 'features', cutoff=1)
        return smatrix

    def getSVD(self,k=25,normalized=False):
        if normalized:
            return self.getSMatrix().normalize_all().svd(k=25)
        else:
            return self.getSMatrix().svd(k=k)

    # Note: checks post first, then pre, never does both.
    def getSimilarity(self, post_normalize=True, pre_normalize=False):
        if post_normalize:
            if 'sim_post' in self.cache:
                return self.cache['sim_post']
            U,S,V = self.getSVD()
            sim_post = divisi2.reconstruct_similarity(U, S, post_normalize=True)
            self.cache['sim_post'] = sim_post
            return sim_post
        if pre_normalize:
            if 'sim_pre' in self.cache:
                return self.cache['sim_pre']
            U,S,V = self.getSVD(normalized=True)
            sim_pre = divisi2.reconstruct_similarity(U, S, post_normalize=False)
            self.cache['sim_pre'] = sim_pre
            return sim_pre
        else:
            if 'sim' in self.cache:
                return self.cache['sim']
            U,S,V = self.getSVD()
            sim = divisi2.reconstruct_similarity(U, S, post_normalize=False)
            self.cache['sim'] = sim
            return sim

    def getPredictions(self):
        if 'predictions' in self.cache:
            return self.cache['predictions']
        U,S,V = self.getSVD()
        predictions = divisi2.reconstruct(U,S,V)
        self.cache['predictions'] = predictions
        return predictions

    # Use Matrix - similarity and predictions
    def topSimilarity(self,id,n=10):
        sim = self.getSimilarity(post_normalize=False,pre_normalize=True)
        return sim.row_named(id).top_items(n)

    def topPredictions(self,id,n=10):
        predictions = self.getPredictions()
        return predictions.row_named(id).top_items(n)
    
    def compare(self,id1,id2):
        sim = self.getSimilarity(post_normalize=False,pre_normalize=True)
        return sim.entry_named(id1,id2)

    # Use Matrix - categories
    def createCategory(self,ids):
        return divisi2.category(dict([(id,1) for id in ids]))

    def categoryTopFeatures(self,category,n=10):
        category_features = divisi2.aligned_matrix_multiply(category, self.getSMatrix())
        return category_features.to_dense().top_items(n)

    def categoryTopSimilarity(self,category,n=10):
        sim = self.getSimilarity(post_normalize=False,pre_normalize=True)
        return sim.left_category(category).top_items(n)

    def categoryTopPredictions(self,category,n=10):
        predictions = self.getPredictions()
        return predictions.left_category(category).top_items(n)

    # Use Matrix - projections
    def project_prediction(self,id1,id2,thresh=.03):
        predictions = self.getPredictions()
        profile1 = self.getById(id1)
        profile2 = self.getById(id2)
        projected_likes = []
        for like in profile1.likes:
            if predictions.entry_named(profile2.id, ('right', 'likes', like.id)) > thresh:
                projected_likes.append(like)
        return projected_likes

    def project_brute(self,id1,id2,thresh=.5):
        sim = self.getSimilarity(post_normalize=False,pre_normalize=True)
        profile1 = self.getById(id1)
        profile2 = self.getById(id2)
        projected_likes = []
        for like in profile1.likes:
            for compare in profile2.likes:
                if sim.entry_named(like.id,compare.id) > thresh:
                    projected_likes.append(like)
                    break
        return projected_likes
