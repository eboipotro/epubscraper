#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import xmltodict
import re
import json
from zipfile import ZipFile
from PIL import Image
from multiprocessing import Pool
from functools import partial

"""
Book subject and types data
"""

typelib = ["উপন্যাস", "বড়গল্প", "ছোটগল্প", "কবিতা", "প্রবন্ধ", "নাটক", "গান", "সমগ্র"]

sublib = {"Absurd": "স্বপ্নবাস্তবতা", "Action": "দুঃসাহসিক", "Adventure": "দুঃসাহসিক", "Autobiography": "আত্নজীবনী", "Biography": "জীবনী", "Children's literature": "শিশুসাহিত্য", "Classic": "চিরায়ত সাহিত্য", "Collection": "সমগ্র", "Comedy": "রম্যরচনা", "Crime": "অপরাধ", "Detective": "গোয়েন্দা", "Drama": "নাটক", "Epic": "মহাকাব্য", "Essay": "প্রবন্ধ", "Fable": "রূপকথা", "Fairy tale": "রূপকথা", "Fanciful": "স্বপ্নবাস্তবতা", "Fantasy": "রূপকথা", "Folklore": "লোকসাহিত্য", "Historical fiction": "ঐতিহাসিক উপন্যাস", "History": "ইতিহাস", "Horror": "ভৌতিক", "Humour": "রস", "Legend": "উপ্যাখান", "Magical realism": "জাদুবাস্তবতা", "Memoir": "স্মৃতিচারণ", "Mystery": "রহস্য", "Mythology": "পুরাণ", "Novel": "উপন্যাস", "Novella": "বড়গল্প", "Philosophy": "দর্শন", "Play": "নাটক", "Poem": "কবিতা", "Politics": "রাজনীতি", "Realistic fiction": "বাস্তবিক", "Religion": "ধর্ম", "Romance": "প্রেম", "Satire": "ব্যাঙ্গরচনা", "Science": "বিজ্ঞান", "Science fiction": "কল্পবিজ্ঞান", "Song": "গান", "Speech": "ভাষণ", "Story": "ছোটগল্প", "Short story": "ছোটগল্প", "Surreal": "স্বপ্নবাস্তবতা", "Travel": "ভ্রমণকাহিনী", "Dance-drama": "নৃত্যনাট্য"}

def namef (string):
    return string.split('/')[-1]

def imscrap (booklink, imagedir, imagename, imagelink, overwrite):
    """
    Scrap Cover image from epub.
    """
    target = os.path.join(imagedir, imagename)
    if overwrite == True:
        try:
            os.remove(target)
        except:
            pass
    if os.path.isfile(target) == True:
        return "/images/" + imagename
    else:
        with ZipFile(booklink) as book:
            with book.open(imagelink) as cover:
                img = Image.open(cover)
                img = img.resize((225, 318), Image.ANTIALIAS)
                img.save(target)
        return "/images/" + imagename
    
def link_parser(dstring):
    """
    Github repository link perser
    """
    data = dstring.split('(http')
    if len(data) == 2:
        return [data[0].strip(), 'http' + data[1].split(')')[0].strip()]
    else:
        return [data[0].strip(), ""]

def book_keeper (booklink):
    """
    Book cataloger based on metadata
    """
    with ZipFile(booklink) as book:
        with book.open('OEBPS/content.opf') as cont:
            data = xmltodict.parse(cont.read())['package']
    meta = data['metadata']
    version = data['@version'][0]
    catalog = {'author': [], 'publisher': [], 'translator': [], 'editor': [], 'illustrator': [], 'subject': []}
    for key, val in meta.items():
        if key == 'dc:title':
            catalog['title'] = val
        elif key == 'dc:creator':
            if version == '2':
                if isinstance(val, list):
                    for v in val:
                        if v['@opf:role'] == 'aut':
                            catalog['author'].append(link_parser(v['#text']))
                else:
                    if val['@opf:role'] == 'aut':
                        catalog['author'].append(link_parser(val['#text']))
            elif version == '3':
                if isinstance(val, list):
                    metas = {}
                    for m in meta['meta']:
                        try:
                            if m['#text'] in ['aut', 'ill', 'edt', 'trl', 'pbl']:
                                if m['@refines'][0] == "#":
                                    res = m['@refines'][1:]
                                else:
                                    res = m['@refines']
                                metas[res] = m['#text']
                        except:
                            pass
                    vals = {}
                    for v in val:
                        if v['@id'][0] == "#":
                            res = v['@id'][1:]
                        else:
                            res = v['@id']
                        vals[res] = v['#text']
                    for k, v in metas.items():
                        if v == 'aut':
                            catalog['author'].append(link_parser(vals[k]))
                        elif v == 'trl':
                            catalog['translator'].append(link_parser(vals[k]))
                        elif v == 'edt':
                            catalog['editor'].append(link_parser(vals[k]))
                        elif v == 'ill':
                            catalog['illustrator'].append(link_parser(vals[k]))
                        elif v == 'pbl':
                            catalog['publisher'].append(link_parser(vals[k]))
                else:
                    metas = {}
                    for m in meta['meta']:
                        try:
                            if m['#text'] in ['aut', 'ill', 'edt', 'trl', 'pbl']:
                                if m['@refines'][0] == "#":
                                    res = m['@refines'][1:]
                                else:
                                    res = m['@refines']
                                metas[res] = m['#text']
                        except:
                            pass
                    vals = {}
                    if val['@id'][0] == "#":
                        res = val['@id'][1:]
                    else:
                        res = val['@id']
                    vals[res] = val['#text']
                    for k, v in metas.items():
                        if v == 'aut':
                            catalog['author'].append(link_parser(vals[k]))
                        elif v == 'trl':
                            catalog['translator'].append(link_parser(vals[k]))
                        elif v == 'edt':
                            catalog['editor'].append(link_parser(vals[k]))
                        elif v == 'ill':
                            catalog['illustrator'].append(link_parser(vals[k]))
                        elif v == 'pbl':
                            catalog['publisher'].append(link_parser(vals[k]))
        elif key == 'dc:language':
            catalog['language'] = val
        elif key == 'dc:description':
            catalog['description'] = val
        elif key == 'dc:publisher':
            if isinstance(val, list):
                for v in val:
                    catalog['publisher'].append(link_parser(v))
            else:
                catalog['publisher'].append(link_parser(val))
        elif key == 'dc:type' or key == 'dc:subject':
            try:
                if isinstance(val, list):
                    for v in val:
                        catalog['subject'].append(sublib[v.capitalize()])
                else:
                    catalog['subject'].append(sublib[val.capitalize()])
            except:
                pass
        elif key == 'dc:contributor':
            if isinstance(val, list):
                for v in val:
                    role = v['@opf:role']
                    if role == 'trl':
                        catalog['translator'].append(link_parser(v['#text']))
                    elif role == 'edt':
                        catalog['editor'].append(link_parser(v['#text']))
                    elif role == 'ill':
                        catalog['illustrator'].append(link_parser(v['#text']))
            else:        
                role = val['@opf:role']
                if role == 'trl':
                    catalog['translator'].append(link_parser(val['#text']))
                elif role == 'edt':
                    catalog['editor'].append(link_parser(val['#text']))
                elif role == 'ill':
                    catalog['illustrator'].append(link_parser(val['#text']))
        elif key == 'dc:date':
            if version == '3':
                catalog['pubdate'] = val
            else:
                if isinstance(val, list):
                    for v in val:
                        event = v['@opf:event']
                        if event == 'publication' or event == 'creation':
                            catalog['pubdate'] = v['#text']
                        elif event == 'modification':
                            catalog['moddate'] = v['#text']
                else:
                    try:
                        event = val['@opf:event']
                        if event == 'publication' or event == 'creation':
                            catalog['pubdate'] = val['#text']
                        elif event == 'modification':
                            catalog['moddate'] = val['#text']
                    except:
                        try:
                            catalog['pubdate'] = val
                        except:
                            pass
        elif key == 'meta':
            for v in val:
                try:
                    if v['@name'] == 'cover':
                        catalog['cover'] = "OEBPS/Images/" + v['@content']
                except:
                    try:
                        if v['@property'] == 'dcterms:modified':
                            catalog['moddate'] = v['#text'][:10]
                    except:
                        pass
    subject = catalog['subject']
    precount = len(subject)
    for s in subject:
        if s in typelib:
            catalog['type'] = s
            catalog['subject'].remove(s)
    if len(catalog['subject']) == precount:
        catalog['type'] = 'অন্যান্য'
    return catalog

def authmaker(nestedvec, blogdir, name):
    items = []
    for author in nestedvec:
        dname = author[0].replace(" ", "-")
        page = os.path.join(blogdir, "_authors/", dname) + ".markdown"
        if os.path.isfile(page):
            items.append(" - " + name + ": \"" + author[0] + "\"\n   link: \"https://eboipotro.github.io/author/" + dname + "/\"")
        else:
            items.append(" - " + name + ": \"" + author[0] + "\"\n   link: \"" + author[-1] + "\"")
    return "\n".join(items)

def arraymaker(nestedvec, name=False):
    if name == False:
        dvec = []
        for i in nestedvec:
            dvec.append(i[0])
        return "\"" + '\", \"'.join(dvec) + "\""
    else:
        dvec = []
        for i in nestedvec:
            dvec.append(" - " + name + ": \"" + i[0] + "\"\n   link: \"" + i[-1] + "\"")
        return "\n".join(dvec)

def autgen(path, blogdir):
    """
    Author page creator
    """
    try:
        with open(os.path.join(path, "author")) as dfile:
            autdata = json.load(dfile)
            for aut in autdata:
                with open(os.path.join(blogdir, "_authors", aut['name'].replace(" ", "-")) + ".markdown", 'w') as autfile:
                    autfile.truncate()
                    dstr = "---\nlayout: author\ntitle: \"" + aut['name'] + "\"\nautlink: \"" + aut['link'] + "\"\npermalink: /author/" + aut['name'].replace(" ", "-") + "/\n"
                    try:
                        dstr = dstr + "img: \"" + aut['image'] + "\"\n"
                    except:
                        pass
                    dstr = dstr + "---\n" + aut['description']
                    autfile.write(dstr)
    except:
        pass

def postmaker(dmap, blogdir):
    """
    Book page data creator
    """
    try:
        moddate = dmap['moddate']
    except:
        moddate = dmap['pubdate']
    try:
        pubdate = dmap['pubdate']
    except:
        pubdate = dmap['moddate']
    if dmap['type'] == 'নাটক':
        if 'নৃত্যনাট্য' in dmap['subject']:
            ptype = "নাটক-নৃত্যনাট্য"
        else:
            ptype = "নাটক"
    else:
        ptype = dmap['type']
    mname = re.sub('-+', "-", re.sub('[_/ ]+', "-", dmap['title'])) + "-" + re.sub(' +', "-", ptype) + "-" + re.sub(' +', "-", dmap['author'][0][0])
    filename = moddate + "-" + mname + ".markdown"
    permalink = "/library/" + mname + "/"
    categories = dmap['subject'] + [dmap['type']]
    out = [
        filename,
        "---",
        "layout: post",
        "published: true",
        "title: " + "\"" + dmap['title'] + "\"",
        "tags: [" + arraymaker(dmap['author'] + dmap['translator']) + "]",
        "categories: [\"" +  "\", \"".join(categories) + "\"]",
        "img: \"" + dmap['cover'] + "\"",
        "type: \"" + dmap['type'] + "\""]

    if len(dmap['subject']) > 0:
        out.append("subject: [\"" + "\", \"".join(dmap['subject']) + "\"]")
    out = out + [
        "dlink: \"" + dmap['link'] + "\"",
        "lang: \"" + dmap['language'] + "\"",
        "publishers: \n" + arraymaker(dmap['publisher'], "publisher"),
        "moddate: \"" + moddate + "\"",
        "pubdate: \"" + pubdate + "\"",
        "comments: true",
        "authors: \n" + authmaker(dmap['author'], blogdir, "author")]
    if len(dmap['translator']) > 0:
        out.append("translators: \n" + authmaker(dmap['translator'], blogdir, "translator"))
    if len(dmap['illustrator']) > 0:
        out.append("illustrators: \n" + arraymaker(dmap['illustrator'], "illustrator"))
    if len(dmap['editor']) > 0:
        out.append("editors: \n" + arraymaker(dmap['editor'], "editor"))
    try:
        out.append("description: \"" + dmap['description'] + "\"")
    except:
        pass
    out.append("permalink: \"" + permalink + "\"")
    out.append("---")
    return out

# def printer(outdir, blogdir, dmap):
#     """
#     Book page creator
#     """
#     data = postmaker(dmap, blogdir)
#     dname = data[0][11:]
#     for f in os.listdir(outdir):
#         if re.search(dname, f):
#             try:
#                 os.remove(os.path.join(outdir, f))
#             except:
#                 pass
#     with open(os.path.join(outdir, data[0]), 'w') as dfile:
#         for line in data[1:]:
#             dfile.write(line + "\n")

def file_linker(dfile, path, blogdir, postdir, posts, link, imagedir, overwrite):
    """
    Add file and image links.
    """
    meta = book_keeper(dfile)
    filepath = re.sub(path, '', dfile).strip("/")
    imagelink = meta['cover']
    if meta['type'] == 'নাটক':
        if 'নৃত্যনাট্য' in meta['subject']:
            ptype = "নাটক-নৃত্যনাট্য"
        else:
            ptype = "নাটক"
    else:
        ptype = meta['type']
    imgname = re.sub('-+', "-", re.sub('[_/ ]+', "-", meta['title'])) + "-" + re.sub(' +', "-", ptype) + "-" + re.sub(' +', "-", meta['author'][0][0]) + "." + namef(imagelink).split('.')[-1]
    image = imscrap(dfile, imagedir, imgname, imagelink, overwrite)
    meta['cover'] = image
    meta['link'] = os.path.join(link, "raw/master", filepath)
    data = postmaker(meta, blogdir)
    dname = data[0][11:]
    dwritefile = os.path.join(postdir, data[0])
    while os.path.isfile(dwritefile) == False:
        dwrite =  open(dwritefile, 'w')
        dwrite.truncate()
        for line in data[1:]:
            dwrite.write(line + "\n")
        dwrite.close()
    tposts = []
    for tp in posts:
        if tp.split("/")[-1][11:] == dname:
            tposts.append(tp)
    tposts = sorted(tposts)
    if len(tposts) > 1:
        for tp in tposts[:-1]:
            os.remove(tp)

def mapmaker(path, outdir, overwrite, ps):
    """
    Get data of a whole repo.
    """
    imagedir = os.path.join(outdir, "images")
    authorfile = os.path.join(outdir, "author")
    postdir = os.path.join(outdir, "_posts")
    with open(os.path.join(path, '.git/config')) as con:
        for line in con:
            if 'url' in line:
                metadata = line.split('=')[-1].strip()
        if "https" in metadata:
            link = metadata
        else:
            link = metadata.replace('git@github.com:', 'https://github.com/').replace('.git', '')
    dfiles = []
    for p, subdirs, files in os.walk(path):
        for f in [f for f in files if f.endswith(".epub")]:
            dfiles.append(os.path.join(p, f))
    posts = []
    for p, subdirs, files in os.walk(postdir):
        for f in [f for f in files if f.endswith(".markdown")]:
            posts.append(os.path.join(p, f))
    partial_file_linker = partial(file_linker, path=path, blogdir=outdir, postdir=postdir, posts=posts, link=link, imagedir=imagedir, overwrite=overwrite)
    with Pool(processes=ps) as pool:
        pool.map(partial_file_linker, dfiles)
    print(len(dfiles))

def postgen(path, blogdir, overwrite=False, ps=8):
    """
    Viola! Do everything!
    """
    autgen(path, blogdir)
    mapmaker(path, blogdir, overwrite, ps)
    
