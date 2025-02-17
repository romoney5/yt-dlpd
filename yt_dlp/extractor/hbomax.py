from .turner import TurnerBaseIE
from ..utils import int_or_none


class HBOMaxIE(TurnerBaseIE):
    _VALID_URL = r'https?://(?:www\.|play\.)?hbomax\.com/(?P<anything>.+)'
    _TEST = {
        'url': 'https://www.hbomax.com/collections/watch-free/barry-s1-e1',
        'info_dict': {
            'id': '6e3375097f63874ebccec7ef677c1c3845fa850e',
            'ext': 'mp4',
            'title': 'Chapter One: Make Your Mark',
            # 'description': 'md5:2061d83776db7e8be4879684eefe8c0f',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
    }

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        def find_field(global_re, name, content_re=None, value_re='[^"]+', fatal=False):
            metadata_re = ''
            if content_re:
                metadata_re = r'|video_metadata\.content_' + content_re
            return self._search_regex(
                r'(?:_cnglobal\.currentVideo\.%s%s)\s*=\s*"(%s)";' % (global_re, metadata_re, value_re),
                webpage, name, fatal=fatal)

        media_id = find_field('mediaId', 'media id', 'id', '[0-9a-f]{40}', True)
        title = find_field('episodeTitle', 'title', '(?:episodeName|name)', fatal=True)

        info = self._extract_ngtv_info(
            media_id, {'networkId': 'hbomax'}, {
                'url': url,
                'site_name': 'HBOmax',
                'auth_required': find_field('authType', 'auth type') != 'unauth',
            })

        series = find_field(
            'propertyName', 'series', 'showName') or self._html_search_meta('partOfSeries', webpage)
        info.update({
            'id': media_id,
            'display_id': display_id,
            'title': title,
            'description': self._html_search_meta('description', webpage),
            'series': series,
            'episode': title,
        })

        for field in ('season', 'episode'):
            field_name = field + 'Number'
            info[field + '_number'] = int_or_none(find_field(
                field_name, field + ' number', value_re=r'\d+') or self._html_search_meta(field_name, webpage))

        return info
