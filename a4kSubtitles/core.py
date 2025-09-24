# -*- coding: utf-8 -*-

import json
import os
import sys
import threading
import copy
import shutil
import gzip
import difflib
import time
import hashlib
import re
import zipfile
from datetime import datetime, timedelta
from base64 import b64encode
from xml.etree import ElementTree
from io import BytesIO

from .lib import (
    cache,
    kodi,
    logger,
    num2ordinal,
    request,
    utils,
    video,
)

core = sys.modules[__name__]
utils.core = core

api_mode_enabled = True
handle = None
last_meta = None

progress_dialog = None
progress_text = ''

from .services import services
from .search import search
from .download import download
from .data import data

def main(handle, paramstring):  # pragma: no cover
    core.api_mode_enabled = False
    core.handle = handle

    params = dict(utils.parse_qsl(paramstring))
    if params['action'] == 'manualsearch':
        # Use the provided search string if available
        searchstring = params.get('searchstring', '')
        if searchstring:
            # Parse the search string to extract title, year, etc.
            # Simple parsing: assume format like "Title (Year)" or "Title S01E01"
            title = searchstring
            year = ''
            season = ''
            episode = ''
            is_tvshow = False

            # Extract year if present
            year_match = re.search(r'\((\d{4})\)', searchstring)
            if year_match:
                year = year_match.group(1)
                title = re.sub(r'\s*\(\d{4}\)', '', title)

            # Check for TV show format
            tv_match = re.search(r'S(\d+)E(\d+)', searchstring, re.IGNORECASE)
            if tv_match:
                season = tv_match.group(1)
                episode = tv_match.group(2)
                is_tvshow = True
                # Remove season/episode from title
                title = re.sub(r'\s*S\d+E\d+', '', title, flags=re.IGNORECASE)

            # Create manual metadata
            manual_meta = utils.DictAsObject({
                'title': title.strip(),
                'year': year,
                'tvshow': title.strip() if is_tvshow else '',
                'season': season,
                'episode': episode,
                'imdb_id': '',
                'is_tvshow': is_tvshow,
                'is_movie': not is_tvshow,
                'languages': ['en'],  # Default to English, can be customized
                'preferredlanguage': 'en'
            })
        else:
            # Fallback to prompts if no search string
            dialog = core.kodi.xbmcgui.Dialog()
            title = dialog.input('Enter movie/TV show title', type=core.kodi.xbmcgui.INPUT_ALPHANUM)
            if not title:
                return
            year = dialog.input('Enter year (optional)', type=core.kodi.xbmcgui.INPUT_NUMERIC)
            media_type = dialog.select('Select type', ['Movie', 'TV Show'])
            if media_type == -1:
                return
            is_tvshow = media_type == 1
            season = ''
            episode = ''
            if is_tvshow:
                season = dialog.input('Enter season number', type=core.kodi.xbmcgui.INPUT_NUMERIC)
                episode = dialog.input('Enter episode number', type=core.kodi.xbmcgui.INPUT_NUMERIC)
                if not season or not episode:
                    return

            # Create manual metadata
            manual_meta = utils.DictAsObject({
                'title': title,
                'year': year,
                'tvshow': title if is_tvshow else '',
                'season': season,
                'episode': episode,
                'imdb_id': '',
                'is_tvshow': is_tvshow,
                'is_movie': not is_tvshow,
                'languages': ['en'],  # Default to English, can be customized
                'preferredlanguage': 'en'
            })

        # Set manual search params
        params['manual_meta'] = manual_meta
        params['languages'] = 'en'  # Set default language
        params['preferredlanguage'] = 'en'  # Set default preferred language
        params['action'] = 'search'  # Route to search
        core.progress_text = ''
        core.progress_dialog = kodi.get_progress_dialog()

        try:
            search(core, params)
        finally:
            core.progress_dialog.close()
            core.progress_dialog = None
    elif params['action'] == 'search':
        core.progress_text = ''
        core.progress_dialog = kodi.get_progress_dialog()

        try:
            search(core, params)
        finally:
            core.progress_dialog.close()
            core.progress_dialog = None

    elif params['action'] == 'download':
        params['action_args'] = json.loads(params['action_args'])
        download(core, params)

    kodi.xbmcplugin.endOfDirectory(handle)
