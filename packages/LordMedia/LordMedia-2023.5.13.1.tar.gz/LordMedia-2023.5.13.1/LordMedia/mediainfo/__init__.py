import os
import subprocess
from pathlib import Path

from pymediainfo import MediaInfo
import platform
from . import lib


# https://mediaarea.net/en/MediaInfo => DyLib

_lib_path = Path(lib.__path__[0])
media_info_lib_file = None

match platform.system():
    case 'Windows':
        media_info_lib_file = _lib_path / r'MediaInfoLib\win\MediaInfo.dll'
    case 'Darwin':     # Mac
        media_info_lib_file = _lib_path / 'MediaInfoLib/mac/libmediainfo.dylib'
    case _:
        media_info_lib_file = None


class MediaInfoClass:

    @staticmethod
    def get_lib_file():
        global media_info_lib_file
        return media_info_lib_file

    @staticmethod
    def generate_mediainfo_output(file, output_format='text'):
        file = Path(file)
        folder = str(file.parent)
        m = MediaInfo.parse(file, output=output_format, library_file=MediaInfoClass.get_lib_file(), full=False)
        m = m.replace(folder + '\\', '')  # TODO do this better xD
        m = m.replace(folder + '/', '')
        m = m.replace(folder, '')
        return m

    @staticmethod
    def __get_from_file_via_lib(file):
        m_i = MediaInfo.parse(file, library_file=MediaInfoClass.get_lib_file())
        return m_i

    @staticmethod
    def __get_from_file_via_subprocess(file):
        # mediainfo --output=OLDXML     # TODO untested
        media_info_xml = subprocess.Popen(['mediainfo', '--output=OLDXML', '-f', file], stdout=subprocess.PIPE)
        media_info_xml = str(media_info_xml.stdout.read().decode("utf-8"))
        m_i = MediaInfo(media_info_xml)
        return m_i

    # My MediaInfo Class

    def __init__(self, file, with_lib=True):
        self.file = file
        if with_lib:
            self.media_info = MediaInfoClass.__get_from_file_via_lib(file)
        else:
            self.media_info = MediaInfoClass.__get_from_file_via_subprocess(file)

    def to_json(self):
        return self.media_info.to_json()

    def to_data(self):
        return self.media_info.to_data()

    # Tracks-list

    def get_general(self):
        return self.media_info.general_tracks

    def get_menu(self):
        return self.media_info.menu_tracks

    def get_video(self):
        return self.media_info.video_tracks

    def get_audio(self):
        return self.media_info.audio_tracks

    def get_sub(self):
        return self.media_info.text_tracks

    def get_image(self):
        return self.media_info.image_tracks

    def generate_output(self, output_format='text'):
        return MediaInfoClass.generate_mediainfo_output(self.file, output_format=output_format)

    # Spezials

    def get_langs_audio(self, lang_type_id: int = 0):
        """
        :param lang_type_id: int
        Sample lang_type_id -> Returned Type
        0 = {str} 'Japanese (JP)'
        1 = {str} 'Japanese (JP)'
        2 = {str} 'ja'
        3 = {str} 'jpn'
        4 = {str} 'ja-JP'
        :return:
        """
        r = []
        for audio in self.get_audio():
            if audio.other_language is None:
                continue
            l = audio.other_language[lang_type_id]
            r.append(l)
        return r

    def get_langs_sub(self, lang_type_id: int = 0):
        """
        :param lang_type_id: int
        Sample lang_type_id -> Returned Type
        0 = {str} 'Japanese (JP)' or Japanese
        1 = {str} 'Japanese (JP)' or Japanese
        2 = {str} 'ja'
        3 = {str} 'jpn'
        4 = {str} 'ja-JP' or 'ja'
        :return:
        """
        r = []
        for sub in self.get_sub():
            if sub.other_language is None:
                continue
            l = sub.other_language[lang_type_id]
            r.append(l)
        return r

    def get_resolution(self):
        v = self.get_video()[0]
        return f"{v.width}x{v.height}"

    def get_size(self):
        return self.get_general()[0].other_file_size[0]


__all__ = ['MediaInfoClass']
