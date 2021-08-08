'''
basic util functions for helping translate swift to python
'''

from typing import List, Optional
from hashlib import md5
import struct

def nil_guard(opt, other):
    '''
    This captures the semantics of `opt ?? other`
    '''
    return opt if opt is not None else other

def first(l:List[object]):
    '''
    This captures the semantics of Swift's list.first
    '''
    return l[0] if l else None

def last(l:List[object]):
    '''
    This captures the semantics of Swift's list.last
    '''
    return l[-1] if l else None

def hash_str_as_id(s: str) -> int:
    '''
    This implements the hashing algorithm from the original codebase
    '''
    hand_id_hex = md5(s.encode()).digest()[:16]
    hex_int = 0
    for x in struct.unpack("<LLLL", hand_id_hex):
        hex_int = (hex_int << 4) + x
    return hex_int


def slice(content: str, start:str, end: str) -> Optional[str]:
    '''
    Return a slice of content between `start` and `end` if possible, otherwise return
    the original content string
    '''

    try:
        idx_start = content.index(start)
        idx_end = content[start:].index(end) + idx_start
        return content[idx_start:idx_end]
    except:
        return None