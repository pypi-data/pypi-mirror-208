"""builder: static site builder for dirt SSG
This is used by the library, CLI, and file monitoring in the server.
TODO code to ignore emacs temporary files needs generalizing
TODO page.metadata keys beginning underscore is a tricky but handy property bag
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.common import INDEX_FILE, canonical_rel, ignore_file, boolean_string
from dirt.config import site_config, collection_config
from dirt.feeds import make_feeds
from dirt.generate import LOCK_FILENAME, TIMESTAMP_FILENAME, soft_copyfile
from dirt.generate import load_page, make_page, generate_start, generate_done
from dirt.pageinfo import DirInfo

import os


STAGED_PREFIX = "_STAGED_"


def regenerate(cxt, verbose=False):
    """Regenerate the static site from source content files into the site
    directory. Returns an error message for failures, or None if successful.
    """
    timestamp = generate_start(cxt.public_path)
    if (timestamp):
        cxt.timestamp = timestamp
    else:
        return "Locked directory: %s" % cxt.public_path
    if (verbose):
        print("regenerate: cxt.timestamp=" + cxt.timestamp)
    try:
        process(cxt, verbose=verbose)
    finally:
        if (not generate_done(cxt.public_path)):
            return "Failed unloking directory: %s" % cxt.public_path
    return None


def process(cxt, verbose=False):
    """Process source content, generating public website directory
    and then optionally also generate a staged website.
    TODO: staged website generation (interferes with cleanup operation)
    """
    rootpath = cxt.content_path
    targetpath = cxt.public_path
    staged = build_site(cxt, rootpath, targetpath, STAGED_PREFIX,
                        verbose=verbose)
    if (staged):
        stagedpath = os.path.join(targetpath, STAGED_PREFIX)
        build_site(cxt, rootpath, stagedpath, None, verbose=verbose)
        cxt.snippets['_staged_dir'] = STAGED_PREFIX


def build_site(cxt, rootpath, targetpath, stage_id, verbose=False):
    """Build the public website directory from the source content directory
    and then removing unneeded residual files and directories.
    1. first we copy (unless already up to date) the framework's static files
    2. walk source content: mirroring static files into public, queueing pages
    3. arrange pages into ordered structure (basis for site map and menus)
    4. generate pages into public directory
    5. create feeds (depends on pages arranged into order)
    6. delete leftovers in target directory from earlier build
    This last step is done by saving (file_map) dictionary keyed by full path
    of each target directory (under the public_path tree) with
    a list of all filenames copies or generated into that directory.
    Then walking the target directory (a) first, remove all other files found
    that were not generated; then (b) check directories (ordered from the
    directory tree leaves working upward) removing empty directories.
    This routine is called once for the main site with stage_id set to
    STAGED_PREFIX meaning to leave that directory alone. Then if there is
    staged content it's called again with stage_id=None to include staged
    content in its subdirectory (named STAGED_PREFIX).
    Returns the number of staged markdown pages skipped in the main pass.
    """
    realtargetpath = os.path.realpath(targetpath)
    already_processed = site_config(cxt)
    fx = cxt.site['framework']
    file_map = fx.add_files(realtargetpath)
    file_map_add(file_map, realtargetpath, [LOCK_FILENAME, TIMESTAMP_FILENAME])
    drafts_skipped = 0
    staged_skipped = 0
    for dirpath, subdirs, filenames in os.walk(rootpath):
        reldir = canonical_rel(os.path.relpath(dirpath, rootpath))
        parentdir = os.path.dirname(reldir)
        generated_filenames = list()
        for subdir in subdirs:
            targetdir = os.path.join(targetpath, reldir, subdir)
            os.makedirs(targetdir, exist_ok=True)
        pages = list()
        statics = list()
        index_page = None
        config, processed = collection_config(cxt, dirpath)
        already_processed += processed
        destinationdir = os.path.realpath(os.path.join(targetpath, reldir))
        for filename in filenames:
            if (filename in already_processed or ignore_file(filename)):
                continue
            splitfilename = os.path.splitext(filename)
            ext = splitfilename[1][1:]
            basename = splitfilename[0]
            filepath = os.path.join(dirpath, filename)
            if (ext in cxt.static_types):
                statics.append(filename)
                relpath = os.path.join(reldir, filename)
                destinationpath = os.path.join(destinationdir, relpath)
                soft_copyfile(filepath, destinationpath)
                generated_filenames.append(filename)
            elif (ext in cxt.page_types):
                page = load_page(ext, filepath, destinationdir,
                                 reldir, basename, verbose=verbose)
                page.metadata['_dir'] = reldir
                if (boolean_string(page.metadata.get('draft', '0'))):
                    drafts_skipped += 1
                    continue
                if (boolean_string(page.metadata.get('staged', '0'))):
                    if (stage_id):  # Include in the staged version
                        staged_skipped += 1
                        continue
                if (basename == INDEX_FILE):
                    page.metadata['_index'] = True
                    index_page = page
                else:
                    page.metadata['_index'] = False
                pages.append(page)
                generated_filenames.append(os.path.basename(page.filepath))
            elif stage_id is not None:
                print("Unsupported file type: %s (ignored)" % filepath)
        file_map_add(file_map, destinationdir, generated_filenames)
        arrange_pages(config, pages)
        cxt.dirs[reldir] = DirInfo(url=reldir, filepath=dirpath,
                                   parent=parentdir, pages=pages,
                                   collection=config, statics=statics)
        if (index_page):
            make_page(cxt, index_page, verbose=verbose)
        for page in pages:
            make_page(cxt, page, verbose=verbose)
    feed_files = make_feeds(cxt)
    file_map_add(file_map, realtargetpath, feed_files)
    if (staged_skipped == 0):
        stage_id = None   # Go ahead and remove staged directory if present
    removed = remove_leftovers(realtargetpath, file_map,
                               skip_prefix=stage_id)
    if (verbose):
        if (removed):
            print("Extra files removed: %s" % repr(removed))
        if (drafts_skipped):
            print("Ignoring %d draft markdown pages." % drafts_skipped)
        if (staged_skipped):
            print("Staging %d markdown pages in %s."
                  % (staged_skipped, stage_id))
    return staged_skipped


def file_map_add(file_map, base_dir, add_files):
    """Register or add filenames to the {file_map}, either create a new
    {base_dir} entry with the {add_files} list, or extend existing list.
    """
    if (base_dir in file_map):
        file_map[base_dir].extend(add_files)
    else:
        file_map[base_dir] = add_files


def remove_leftovers(rootdir, file_map, skip_prefix=None):
    """Remove leftover files and directories residual from previous generation.
    A compendium of all generated files that should be in the target directory
    is provided by {file_map} keyed by directory path with a list of filenames.
    Removing files is the first step, followed by removing empty directories.
    First we walk the target directory to remove all other files there
    that were not generated. Finally, we check each directory (starting from
    the directory tree leaves and working upward) removing empty directories.
    Reverse sorting the directory path keys ensures that lower directories are
    checked and deleted if empty before their parents for smooth cleanup.
    Working on the public/ directory, skip_prefix=STAGED_PREFIX to leave the
    stages directory alone.
    """
    removed = list()
    dirs = set()
    for dirpath, subdirs, filenames in os.walk(rootdir, followlinks=False):
        reldir = canonical_rel(os.path.relpath(dirpath, rootdir))
        if (skip_prefix and reldir.startswith("./" + skip_prefix)):
            continue  # Ignore all of the staged subdirectory
        for subdir in subdirs:
            if (skip_prefix and subdir.startswith(skip_prefix)):
                continue  # Ignore all of the staged subdirectory
            dirs.add(os.path.join(dirpath, subdir))
        generated_filenames = file_map[dirpath] if (
            dirpath in file_map) else []
        for filename in filenames:
            if (filename not in generated_filenames):
                fullpath = os.path.join(dirpath, filename)
                os.remove(fullpath)
                removed.append(fullpath)
    for dirpath in sorted(dirs, reverse=True):
        if (0 == len(os.listdir(dirpath))):
            os.rmdir(os.path.join(dirpath))
            removed.append(dirpath + os.sep)
    return removed


def arrange_pages(collection_config, pages):
    """Arrange pages collected from the source content directory in order.
    The collected page objects are sorted per the collection configuration.
    The index page is special and is removed before sorting and tagging.
    """
    navigation = collection_config.get('navigation', 'none')
    orderby = collection_config.get('orderby', 'filename')
    ordering_literal = collection_config.get('ordering', 'ascending')
    order_descending = ordering_literal == 'descending'
    contentpages = [page for page in pages if not page.metadata.get('_index')]
    contentpages.sort(key=lambda page: str(page.metadata.get(orderby, 0)),
                      reverse=order_descending)
    for seq in range(len(contentpages)):
        page = contentpages[seq]
        page.metadata['_seq'] = str(seq + 1)
        page.metadata['_count'] = len(contentpages)
        page.metadata['_prev'] = None if seq == 0 else contentpages[seq-1]
        page.metadata['_next'] = None if (seq >= len(contentpages)-1
                                          ) else contentpages[seq+1]
        if (navigation in ['top', 'bottom']):
            page.metadata['_nav'] = navigation
