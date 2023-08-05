
import os
import puremagic.main

old_stream_details = puremagic.main._stream_details

def new_stream_details(stream):
    try:
        return old_stream_details(stream)
    except Exception: # file is too small
        stream.seek(0)
        max_head, max_foot = puremagic.main._max_lengths()
        head = stream.read(max_head)
        try:
            stream.seek(-max_foot, os.SEEK_END)
        except IOError:
            stream.seek(0)
        foot = stream.read()
        return head, foot

puremagic.main._stream_details = new_stream_details
