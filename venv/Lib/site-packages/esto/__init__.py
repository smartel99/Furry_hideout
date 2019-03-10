import os
import sys
import json
import urllib.request

e6url = "https://e621.net/post/index.json?limit=1&tags="
def _req(url):
    req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
    return urllib.request.urlopen(req).read()

def _retid(url):
    try:
        print(url)
        req = _req(url)
        jsonreq = json.loads(req.decode())
        i = jsonreq
        pornobj = e621Post(str(i['id']), i['tags'].split(' '), i['description'], str(i['creator_id']), str(i['author']), int(i['change']), i['source'], int(i['score']), int(i['fav_count']), i['md5'], str(i['file_size']), i['file_url'], i['file_ext'], i['preview_url'], i['preview_width'], i['preview_height'], i['sample_url'], i['sample_width'], i['sample_height'], i['rating'], i['status'], i['width'], i['height'], i['has_comments'], i['has_notes'], i['has_children'], i['children'], i['parent_id'], i['artist'], i['source'])
        return pornobj
    except ValueError:
        warnings.warn("Warning: post deleted or undefined error. Setting all values to none.")
        return e621Post(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)



def _rettags(tags):
    try:
        if type(tags) is list:
            taglist = '+'.join(tags)
        elif type(tags) is str:
            taglist = tags.replace(" ", "+")
        else:
            raise UnsupportedType("the given var type is not supported, must be either list or str")
        url = e6url + taglist
        req = _req(url)
        jsonreq = json.loads(req.decode())
        for i in jsonreq:
            pornobj = e621Post(str(i['id']), i['tags'].split(' '), i['description'], str(i['creator_id']), str(i['author']), int(i['change']), i['source'], int(i['score']), int(i['fav_count']), i['md5'], str(i['file_size']), i['file_url'], i['file_ext'], i['preview_url'], i['preview_width'], i['preview_height'], i['sample_url'], i['sample_width'], i['sample_height'], i['rating'], i['status'], i['width'], i['height'], i['has_comments'], i['has_notes'], i['has_children'], i['children'], i['parent_id'], i['artist'], i['source'])
        return pornobj
    except UnboundLocalError:
        return e621Post(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
    except ValueError:
        warnings.warn("Warning: post deleted or undefined error. Setting all values to none.")
        return e621Post(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
def resolveid(id):
    url = "https://e621.net/post/show.json?id=" + id
    pornobj = _retid(url)
    return pornobj
def resolvehash(filehash):
    url = 'https://e621.net/post/show.json?md5=' + filehash
    pornobj = _retid(url)
    return pornobj
def getdata(tags):
    pornobj = _rettags(tags)
    return pornobj
def downloadfile(tags,filename):
    pornobj = _rettags(tags)
    if pornobj.id != None:
        file = open(filename, "w")
        file.write(_req(pornobj.file_url))
        file.close()
        
class e621Post:
    def __init__(self,id,tags,description,creator_id,author,change,source,score,fav_count,md5,file_size,file_url,file_ext,preview_url,preview_width,preview_height,sample_url,sample_width,sample_height,rating,status,width,height,has_comments,has_notes,has_children,children,parent_id,artists,sources):
        self.id = id
        self.tags = tags
        self.description = description
        self.creator_id = creator_id
        self.author = author
        self.change = change
        self.source = source
        self.score = score
        self.fav_count = fav_count
        self.md5 = md5
        self.file_size = file_size
        self.file_url = file_url
        self.file_ext = file_ext
        self.preview_url = preview_url
        self.preview_width = preview_width
        self.preview_height = preview_height
        self.sample_url = sample_url
        self.sample_width = sample_width
        self.sample_height = sample_height
        self.rating = rating
        self.status = status
        self.width = width
        self.height = height
        self.has_comments = has_comments
        self.has_notes = has_notes
        self.has_children = has_children
        self.children = children
        self.parent_id = parent_id
        self.artists = artists
        self.sources = sources
class UnsupportedType(Exception):
    def __init__(self,message):
        self.message = message
