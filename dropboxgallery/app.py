#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import pickle
import logging
import logging.config
import flask
import dropbox
import dropboxgallery.gallery
import dropboxgallery.log

DROPBOX_TOKEN_PATH = '/opt/token'
DROPBOX_GALLERY_ROOT = ''
PICKLE_PATH = '/opt/dg_pickle'

logger = logging.getLogger('app')

dropboxgallery.log.set_logging(log_level=logging.INFO)

class DropboxGallery(object):
    DBX_TOKEN = ''
    pickle_sync = None
    g = None

    def load_folder(self, folder_path, folder):
        index_g = []
        for entry in self.dbx.files_list_folder(folder_path).entries:
            if isinstance(entry, dropbox.files.FolderMetadata):
                gf = dropboxgallery.gallery.GalleryFolder(entry, folder.path)
                folder.subfolders.append(gf)
                self.load_folder(entry.path_display, gf)
            elif isinstance(entry, dropbox.files.FileMetadata) and entry.name.split('.')[-1].lower() in ('jpg', 'jpeg', 'png', 'webp'):
                gi = dropboxgallery.gallery.GalleryImage(entry, self)
                folder.images.append(gi)
            elif isinstance(entry, dropbox.files.FileMetadata) and entry.name == 'title':
                index_g.append(folder)
        folder.index_g = index_g # TODO + subfolders index_g
        folder.subfolders = sorted(folder.subfolders, key=lambda x: x.name)
        folder.images = sorted(folder.images, key=lambda x: x.name)
        for subfolder in folder.subfolders:
            folder.index_g += subfolder.index_g
        logger.debug('{0.name} index_g: {0.index_g}'.format(folder))

    def sync_dropbox_to_pickle(self):
        with open(DROPBOX_TOKEN_PATH, 'r') as dbx_token_file:
            self.DBX_TOKEN = dbx_token_file.read().strip()
            self.dbx = dropbox.Dropbox(self.DBX_TOKEN)
        g = dropboxgallery.gallery.GalleryFolder(None)
        self.load_folder(DROPBOX_GALLERY_ROOT, g)
        with open(PICKLE_PATH, 'wb') as pickle_file:
            pickle.dump(g, pickle_file, pickle.HIGHEST_PROTOCOL)

    def get_pickle_mod(self):
        return os.path.getmtime(PICKLE_PATH)

    def sync_content_from_pickle(self):
        if not os.path.exists(PICKLE_PATH):
            logger.warning('No pickle file')
            return

        last_pickle_mod = self.get_pickle_mod()
        logger.debug('pickle file mod: {0}'.format(last_pickle_mod))
        if self.pickle_sync is not None and last_pickle_mod <= self.pickle_sync:
            logger.debug('content up-to-date ...')
            return

        logger.info('content outdated, reload from pickle ...')
        self.load_content_from_pickle()

    def load_content_from_pickle(self):
        with open(PICKLE_PATH, 'rb') as pickle_file:
            self.g = pickle.load(pickle_file)
        self.pickle_sync = self.get_pickle_mod()

    def get_gallery(self, folder, subfolder=None):
        gallery = next(filter(lambda g: g.name == folder, self.g.subfolders), None)
        if subfolder and gallery:
            gallery = next(filter(lambda g: g.name == subfolder, gallery.subfolders), None)
        return gallery


dg = DropboxGallery()
app = flask.Flask(__name__)


@app.route('/')
def gallery_index():
    dg.sync_content_from_pickle()
    return flask.render_template(
        'index.html',
        dg=dg,
        menu='index',
    )

@app.route('/about')
def gallery_about():
    dg.sync_content_from_pickle()
    return flask.render_template(
        'about.html',
        dg=dg,
        menu='about',
    )

@app.route('/contact')
def gallery_contact():
    dg.sync_content_from_pickle()
    return flask.render_template(
        'contact.html',
        dg=dg,
        menu='contact',
    )

@app.route('/gallery/<folder>')
def gallery_view(folder):
    dg.sync_content_from_pickle()
    return flask.render_template(
        'gallery.html',
        dg=dg,
        gallery=dg.get_gallery(folder),
        menu='gallery',
    )

@app.route('/gallery/<folder>/<subfolder>')
def gallery_view_sub(folder, subfolder):
    dg.sync_content_from_pickle()
    return flask.render_template(
        'gallery.html',
        dg=dg,
        gallery=dg.get_gallery(folder, subfolder),
        menu='gallery',
    )

@app.route('/request/gallery/sync')
def gallery_sync():
    dg.sync_dropbox_to_pickle()
    return flask.render_template(
        'contact.html',
        dg=dg,
        menu='contact',
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
