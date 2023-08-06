
import os
from os import path as ospath
import platform
import glob

# https://mediaarea.net/en/MediaInfo => DyLib
# https://mkvtoolnix.download/

script_path = ospath.realpath(__file__)
script_dir_path = ospath.dirname(script_path)
# usr_lib_path = os.path.expanduser('~/lib')

media_info_lib_file = None
mkv_tool_path = None


def load_windows_paths():
    global media_info_lib_file
    # mediainfo
    media_info_lib_file = os.path.join(script_dir_path, r'MediaInfoLib\win\MediaInfo.dll')


def load_mac_paths():
    global media_info_lib_file
    global mkv_tool_path
    # mediainfo
    media_info_lib_file = os.path.join(script_dir_path, 'MediaInfoLib/mac/libmediainfo.dylib')
    # mkv tool nix
    _temp = glob.glob('/Applications/MKVToolNix-*.app/Contents/MacOS/')
    if _temp:
        mkv_tool_path = _temp[0]


match platform.system():
    case 'Windows':
        load_windows_paths()
    case 'Darwin':     # Mac
        load_mac_paths()
