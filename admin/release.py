#!/usr/bin/env python

# $Id: release.py 1704 2004-12-13 05:56:25Z quarl $

PROJ_NAME = 'quickypix'
REPO_TRUNK = 'http://svn.quarl.org/repos/quickypix/trunk/quickypix'
REPO_TAG_DIR = 'http://svn.quarl.org/repos/quickypix/tags'
RELEASES_DIR = '/home/quarl/proj/quickypix/www/releases'

EXPORT_TARBALL = '/home/quarl/bin/export-tarball'

import os, sys, commands

argv0 = sys.argv[0]

def get_tag_name(version):
    if not version.startswith('v'):
        raise SystemExit('invalid tag "%s"'%version)
    return os.path.join(REPO_TAG_DIR,version)

def commit_message(version):
    return "tag "+version

def get_existing_tags():
    return [os.path.dirname(d) for d in
            commands.getoutput('svn list %s'%REPO_TAG_DIR).split()]

def tag_release(args):
    if len(args) != 1:
        try:
            sys.path.insert(0, '../src/quickypix')
            from version import version
        except:
            version = '1.2.3'
        raise SystemExit("Syntax: %s v%s" %(argv0,version))

    version = args[0]

    if version in get_existing_tags():
        raise SystemExit("Tag %s already exists" %version)

    os.system('svn cp -m "%s" %s %s' %(commit_message(version),
                                       REPO_TRUNK, get_tag_name(version)))

def strip_slash(str):
    if str.endswith('/'):
        return str[:-1]

def get_tags():
    return [strip_slash(d) for d in
            commands.getoutput('svn ls %s' %REPO_TAG_DIR).split()]

def strip_v(str):
    if str.startswith('v'):
        return str[1:]

def each_exists(*paths):
    for path in paths:
        if not os.path.exists(path):
            return False
    return True

def make_releases(args):
    versions = args or get_tags()

    os.chdir(RELEASES_DIR)
    for version in versions:
        v = strip_v(version)
        basename = '%s-%s' %(PROJ_NAME, v)
        tgz_name = '%s.tar.gz' % basename
        tbz_name = '%s.tar.bz2' % basename
        zip_name = '%s.zip' % basename

        if not each_exists(tgz_name, tbz_name, zip_name):
            print
            print '------------------------------------------------------------'
            print 'Making release %s'%version
            print '------------------------------------------------------------'

            d = dict(os.environ,
                     CHECKOUT = ('svn export %s %s' %(
                        get_tag_name(version), basename)),
                     DIR = basename,
                     FILENAME_TGZ = tgz_name,
                     FILENAME_TBZ = tbz_name,
                     FILENAME_ZIP = zip_name,
                     DESTINATION = RELEASES_DIR)

            os.spawnvpe(os.P_WAIT, EXPORT_TARBALL, [EXPORT_TARBALL], d)



