#!/usr/bin/python
# -*- coding: utf-8 -*-


class GalleryImage(object):
    name = ''

    def __init__(self, d, gallery):
        ##self.d = d
        self.name = d.name
        print('processing... ', d.name.encode('utf-8'), d.is_downloadable, d.sharing_info, d.path_display.encode('utf-8'))
        existing_link = gallery.dbx.sharing_list_shared_links(d.path_display, direct_only=True)
        if existing_link and existing_link.links:
            self.link = existing_link.links[0].url
        else:
            self.link = gallery.dbx.sharing_create_shared_link_with_settings(d.path_display).url


class GalleryFolder(object):
    name = '.'
    path = '/'
    images = []
    subfolders = []

    def __init__(self, d, path_prefix='/gallery'):
        ##self.d = d
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
