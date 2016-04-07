#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import xmltodict
import re
import json
from zipfile import ZipFile
from PIL import Image

"""
Book subject and types data
"""

typelib = ["উপন্যাস", "বড়গল্প", "ছোটগল্প", "কবিতা", "প্রবন্ধ", "নাটক", "গান", "সমগ্র"]

sublib = {"Absurd": "স্বপ্নবাস্তবতা", "Action": "দুঃসাহসিক", "Adventure": "দুঃসাহসিক", "Autobiography": "আত্নজীবনী", "Biography": "জীবনী", "Children's literature": "শিশুসাহিত্য", "Classic": "চিরায়ত সাহিত্য", "Collection": "সমগ্র", "Comedy": "রম্যরচনা", "Crime": "অপরাধ", "Detective": "গোয়েন্দা", "Drama": "নাটক", "Essay": "প্রবন্ধ", "Fable": "রূপকথা", "Fairy tale": "রূপকথা", "Fanciful": "স্বপ্নবাস্তবতা", "Fantasy": "রূপকথা", "Folklore": "লোকসাহিত্য", "Historical fiction": "ঐতিহাসিক উপন্যাস", "History": "ইতিহাস", "Horror": "ভৌতিক", "Humour": "রস", "Legend": "উপ্যাখান", "Magical realism": "জাদুবাস্তবতা", "Memoir": "স্মৃতিচারণ", "Mystery": "রহস্য", "Mythology": "পুরাণ", "Novel": "উপন্যাস", "Novella": "বড়গল্প", "Philosophy": "দর্শন", "Play": "নাটক", "Poem": "কবিতা", "Politics": "রাজনীতি", "Realistic fiction": "বাস্তবিক", "Religion": "ধর্ম", "Romance": "প্রেম", "Satire": "ব্যাঙ্গরচনা", "Science": "বিজ্ঞান", "Science fiction": "কল্পবিজ্ঞান", "Song": "গান", "Speech": "ভাষণ", "Story": "ছোটগল্প", "Short story": "ছোটগল্প", "Surreal": "স্বপ্নবাস্তবতা", "Travel": "ভ্রমণকাহিনী", "Dance-drama": "নৃত্যনাট্য"}

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
            meta = xmltodict.parse(cont.read())['package']['metadata']
    catalog = {'author': [], 'publisher': [], 'translator': [], 'editor': [], 'illustrator': [], 'subject': []}
    for key, val in meta.items():
        if key == 'dc:title':
            catalog['title'] = val
            print (catalog['title'])
        elif key == 'dc:creator':
            if isinstance(val, list):
                for v in val:
                    try:
                        if v['@opf:role'] == 'aut':
                            catalog['author'] == catalog['author'].append(link_parser(v['#text']))
                    except:
                        if v['@id'] == 'cre':
                            catalog['author'] == catalog['author'].append(link_parser(v['#text']))
            else:
                try:
                    if val['@opf:role'] == 'aut':
                        catalog['author'] == catalog['author'].append(link_parser(val['#text']))
                except:
                    if val['@id'] == 'cre':
                        catalog['author'] == catalog['author'].append(link_parser(val['#text']))
        elif key == 'dc:language':
            catalog['language'] = val
        elif key == 'dc:description':
            catalog['description'] = val
        elif key == 'dc:publisher':
            if isinstance(val, list):
                for v in val:
                    catalog['publisher'] == catalog['publisher'].append(link_parser(v))
            else:
                catalog['publisher'] == catalog['publisher'].append(link_parser(val))
        elif key == 'dc:type' or key == 'dc:subject':
            try:
                if isinstance(val, list):
                    for v in val:
                        catalog['subject'] == catalog['subject'].append(sublib[v.capitalize()])
                else:
                    catalog['subject'] == catalog['subject'].append(sublib[val.capitalize()])
            except:
                pass
        elif key == 'dc:contributor':
            if isinstance(val, list):
                for v in val:
                    role = v['@opf:role']
                    if role == 'trl':
                        catalog['translator'] == catalog['translator'].append(link_parser(v['#text']))
                    elif role == 'edt':
                        catalog['editor'] == catalog['editor'].append(link_parser(v['#text']))
                    elif role == 'ill':
                        catalog['illustrator'] == catalog['illustrator'].append(link_parser(v['#text']))
            else:        
                role = val['@opf:role']
                if role == 'trl':
                    catalog['translator'] == catalog['translator'].append(link_parser(val['#text']))
                elif role == 'edt':
                    catalog['editor'] == catalog['editor'].append(link_parser(val['#text']))
                elif role == 'ill':
                    catalog['illustrator'] == catalog['illustrator'].append(link_parser(val['#text']))
        elif key == 'dc:date':
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

def file_linker(path, link, files, imagedir, overwrite):
    """
    Add file and image links.
    """
    out = []
    for f in files:
        meta = book_keeper(f)
        filepath = re.sub(path, '', f).strip("/")
        imagelink = meta['cover']
        if meta['type'] == 'নাটক':
            if 'নৃত্যনাট্য' in meta['subject']:
                ptype = "নাটক-নৃত্যনাট্য"
            else:
                ptype = "নাটক"
        else:
            ptype = meta['type']
        imgname = re.sub('-+', "-", re.sub('[_/ ]+', "-", meta['title'])) + "-" + re.sub(' +', "-", ptype) + "-" + re.sub(' +', "-", meta['author'][0][0]) + "." + namef(imagelink).split('.')[-1]
        image = imscrap(f, imagedir, imgname, imagelink, overwrite)
        meta['cover'] = image
        meta['link'] = os.path.join(link, "raw/master", filepath)
        out.append(meta)
    return out

def mapmaker(path, outdir, overwrite):
    """
    Get data of a whole repo.
    """
    imagedir = os.path.join(outdir, "images")
    authorfile = os.path.join(outdir, "author")
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
    return file_linker(path, link, dfiles, imagedir, overwrite)

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
        out.append("illustrators: \n" + arraymaker(dmap['translator'], "editor"))
    if len(dmap['editor']) > 0:
        out.append("editors: \n" + arraymaker(dmap['editor'], "editor"))
    try:
        out.append("description: \"" + dmap['description'] + "\"")
    except:
        pass
    out.append("permalink: \"" + permalink + "\"")
    out.append("---")
    return out

def printer(outdir, blogdir, dmap):
    """
    Book page creator
    """
    data = postmaker(dmap, blogdir)
    dname = data[0][11:]
    for f in os.listdir(outdir):
        if re.search(dname, f):
            os.remove(os.path.join(outdir, f))
    with open(os.path.join(outdir, data[0]), 'w') as dfile:
        for line in data[1:]:
            dfile.write(line + "\n")

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


def postgen(path, blogdir, overwrite=False):
    """
    Viola! Do everything!
    """
    autgen(path, blogdir)
    data = mapmaker(path, blogdir, overwrite)
    postdir = os.path.join(blogdir, "_posts")
    for d in data:
        printer(postdir, blogdir, d)
