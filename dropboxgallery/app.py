#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import flask
import dropbox
import dropboxgallery.gallery

DROPBOX_TOKEN_PATH = '/opt/token'
DROPBOX_GALLERY_ROOT = ''


index_g = []


class DropboxGallery(object):
    DBX_TOKEN = ''
    g = None

    def __init__(self):
        with open(DROPBOX_TOKEN_PATH, 'r') as dbx_token_file:
            self.DBX_TOKEN = dbx_token_file.read().strip()
            self.dbx = dropbox.Dropbox(self.DBX_TOKEN)
        self.sync()

    def load_folder(self, folder_path, parent):
        for entry in self.dbx.files_list_folder(folder_path).entries:
            if isinstance(entry, dropbox.files.FolderMetadata):
                gf = dropboxgallery.gallery.GalleryFolder(entry, parent.path)
                parent.subfolders.append(gf)
                self.load_folder(entry.path_display, gf)
            elif isinstance(entry, dropbox.files.FileMetadata) and entry.name.split('.')[-1].lower() in ('jpg', 'jpeg', 'png', 'webp'):
                gi = dropboxgallery.gallery.GalleryImage(entry, self)
                parent.images.append(gi)
            elif isinstance(entry, dropbox.files.FileMetadata) and entry.name == 'title':
                index_g.append(parent)
        parent.subfolders = sorted(parent.subfolders, key=lambda x: x.name)
        parent.images = sorted(parent.images, key=lambda x: x.name)

    def sync(self):
        self.g = dropboxgallery.gallery.GalleryFolder(None)
        self.load_folder(DROPBOX_GALLERY_ROOT, self.g)

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
