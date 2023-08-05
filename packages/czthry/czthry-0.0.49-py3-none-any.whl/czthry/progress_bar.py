from progressbar import ProgressBar
from progressbar import Percentage
from progressbar import AnimatedMarker
from progressbar import Bar
from progressbar import Timer
from progressbar import Widget
from datetime import datetime
import time
import sys
import re


markers_moon = '🌑🌒🌓🌔🌕🌖🌗🌘'
markers_china = '富强明主文明和谐自由平等公正法治爱国敬业诚信友善'


class PBDateTime(Widget):
    """Widget which displays the date & time."""

    __slots__ = ('format_string',)
    TIME_SENSITIVE = True

    def __init__(self, format='%Y-%m-%d %H:%M:%S'):
        self.format_string = format

    def format_time(self):
        now = datetime.now()
        now = now.strftime(self.format_string)
        return now

    def update(self, pbar):
        """Updates the widget to show the date & time"""
        return self.format_time()


class MyFD(object):
    '''解决：
    中文或其他特殊符号，在终端下无法原地更新
    '''
    @staticmethod
    def write(msg):
        print('\r', end='')
        print(msg, end='')

    @staticmethod
    def flush():
        sys.stdout.flush()


def make_loading_indicator(marker=None, widget=None):
    if marker:
        widgets = [AnimatedMarker(markers=marker), ' ']
    else:
        widgets = [AnimatedMarker(), ' ']
    if not widget:
        widget = Timer()
    widgets.append(widget)
    return ProgressBar(widgets=widgets, poll=0.5, fd=MyFD).start()


def make_progress_bar(total, title=None, widgets=None, bar_char='.'):
    if not widgets:
        widgets = [Percentage(), ' ', Bar(bar_char), ' ', Timer()]
    if title:
        widgets = [title, ' '] + widgets
    return ProgressBar(widgets=widgets, maxval=total, fd=MyFD, poll=0.5).start()


if __name__ == '__main__':
    # pbar = make_progress_bar(total=100, title='更新进度', bar_char='•')
    pbar = make_loading_indicator(marker=markers_moon)
    while True:
        pbar.update()
        time.sleep(0.5)
    pass
