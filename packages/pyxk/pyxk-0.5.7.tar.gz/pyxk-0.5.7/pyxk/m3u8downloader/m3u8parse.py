"""m3u8资源解析器"""
from typing import Optional

import m3u8
from m3u8.model import M3U8



class M3U8Parae:
    """m3u8资源 解析器

    :params: *
    :params: content: m3u8 content
    :params: url: m3u8 url
    :params: instance: pyxk.m3u8downloader.main.M3U8
    """
    def __init__(
        self, *, content: str, url: Optional[str], instance: object,
    ):
        self.m3url: Optional[str] = url
        self.m3obj: object = instance
        self.m3par: M3U8 = m3u8.loads(content=content, uri=url)

    @classmethod
    def run(cls, **kwargs):
        self = cls(**kwargs)
        return self.startparse()

    def startparse(self):
        self.parse_playlist()
        m3u8keys = self.parse_m3u8keys()
        segments = self.parse_segments(m3u8keys)
        segments["m3u8keys"] = m3u8keys
        return segments

    def parse_playlist(self):
        """解析 m3u8 playlists"""
        if not self.m3par.is_variant:
            return None

        # 排序 playlists, 获取最大带宽 m3u8 链接
        def _sorted(playlist):
            playlist.uri = playlist.absolute_uri
            return playlist.stream_info.bandwidth
        playlists = sorted(self.m3par.playlists, key=_sorted)

        # 保存m3u8文件 - playlists
        self.m3obj.sava_m3u8_content(self.m3url, self.m3par.dumps())

        # 请求 playlists
        self.m3url = playlists[-1].uri
        self.m3par = m3u8.loads(
            uri=self.m3url,
            content=self.m3obj.get_m3u8_content(self.m3url),
        )
        return self.parse_playlist()

    def parse_m3u8keys(self):
        """解析 m3u8 keys"""
        m3u8keys = {}
        for key in self.m3par.keys:
            if not key:
                continue
            key.uri = key.absolute_uri
            secret = self.m3obj.get_m3u8_content(key.uri, is_m3u8key=True)
            segm_iv = key.iv.removeprefix("0x")[:16] if key.iv else secret[:16]
            # 保存密钥
            self.m3obj.sava_m3u8_content(key.uri, secret, is_m3u8key=True)
            m3u8keys[key.uri] = {"key": secret, "iv": segm_iv}
        return m3u8keys or None

    def parse_segments(self, m3u8keys=None):
        """解析 m3u8 segments

        :params: m3u8keys: m3u8密钥
        """
        segments_dict, duration = {}, 0
        for index, segment in enumerate(self.m3par.segments):
            segment.uri = segment.absolute_uri
            key, duration = None, segment.duration + duration
            # segment 加密 - 解析
            if segment.key and m3u8keys:
                if segment.key.uri in m3u8keys:
                    key = segment.key.uri
            # 保存segment
            segments_dict[index] = {"url": segment.uri, "key": key}
        # 保存 m3u8 文件
        if self.m3par.is_endlist:
            self.m3obj.sava_m3u8_content(self.m3url, self.m3par.dumps())
        return {"maximum": len(segments_dict), "duration": duration, "segments": segments_dict or None}
