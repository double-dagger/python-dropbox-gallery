#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import flask
import dropbox

index_g = []

class GalleryImage(object):
    d = None

    def __init__(self, d, gallery):
        self.d = d
        print('processing... ', d.name.encode('utf-8'), d.is_downloadable, d.sharing_info, d.path_display.encode('utf-8'))
        existing_link = gallery.dbx.sharing_list_shared_links(d.path_display, direct_only=True)
        if existing_link and existing_link.links:
            self.link = existing_link.links[0].url
        else:
            self.link = gallery.dbx.sharing_create_shared_link_with_settings(d.path_display).url


class GalleryFolder(object):
    d = None
    name = '.'
    path = '/'
    images = []
    subfolders = []

    def __init__(self, d, path_prefix='/gallery'):
        self.d = d
        self.images = []
        self.subfolders = []
        if d is not None:
            self.name = d.name
            self.path = '/'.join([path_prefix, self.name,])
        else:
            self.path = path_prefix

    def __str__(self):
        return('{0} [{1}][{2}]'.format(self.name.encode('utf-8'), len(self.subfolders), len(self.images)))

    def get_name(self):
        return self.name


class DropboxGallery(object):
    DBX_TOKEN = ''
    g = None

    def __init__(self):
        with open('/opt/token', 'r') as dbx_token_file:
            self.DBX_TOKEN = dbx_token_file.read().strip()
            self.dbx = dropbox.Dropbox(self.DBX_TOKEN)
        self.sync()

    def load_folder(self, folder_path, parent):
        for entry in self.dbx.files_list_folder(folder_path).entries:
            if isinstance(entry, dropbox.files.FolderMetadata):
                gf = GalleryFolder(entry, parent.path)
                parent.subfolders.append(gf)
                self.load_folder(entry.path_display, gf)
            elif isinstance(entry, dropbox.files.FileMetadata) and entry.name.split('.')[-1].lower() in ('jpg', 'jpeg', 'png', 'webp'):
                gi = GalleryImage(entry, self)
                parent.images.append(gi)
            elif isinstance(entry, dropbox.files.FileMetadata) and entry.name == 'title':
                index_g.append(parent)
        parent.subfolders = sorted(parent.subfolders, key=lambda x: x.d.name)
        parent.images = sorted(parent.images, key=lambda x: x.d.name)

    def sync(self):
        self.g = GalleryFolder(None)
        self.load_folder('/phototest/', self.g)

    def get_gallery(self, folder, subfolder=None):
        gallery = next(filter(lambda g: g.name == folder, self.g.subfolders), None)
        if subfolder and gallery:
            gallery = next(filter(lambda g: g.name == subfolder, gallery.subfolders), None)
        return gallery


dg = DropboxGallery()
app = flask.Flask(__name__)


@app.route('/')
def gallery_index():
    return flask.render_template(
        'index.html',
        dg=dg,
        index_g=index_g,
        menu='index',
    )

@app.route('/about')
def gallery_about():
    return flask.render_template(
        'about.html',
        dg=dg,
        menu='about',
    )

@app.route('/contact')
def gallery_contact():
    return flask.render_template(
        'contact.html',
        dg=dg,
        menu='contact',
    )

@app.route('/gallery/<folder>')
def gallery_view(folder):
    return flask.render_template(
        'gallery.html',
        dg=dg,
        gallery=dg.get_gallery(folder),
        menu='gallery',
    )

@app.route('/gallery/<folder>/<subfolder>')
def gallery_view_sub(folder, subfolder):
    return flask.render_template(
        'gallery.html',
        dg=dg,
        gallery=dg.get_gallery(folder, subfolder),
        menu='gallery',
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
