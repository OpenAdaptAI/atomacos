import re
from collections import namedtuple

from ApplicationServices import (
    AXUIElementGetTypeID,
    AXValueGetType,
    NSPointFromString,
    NSRangeFromString,
    NSRectFromString,
    NSSizeFromString,
    kAXValueCFRangeType,
    kAXValueCGPointType,
    kAXValueCGRectType,
    kAXValueCGSizeType,
)
from CoreFoundation import CFArrayGetTypeID, CFGetTypeID, CFStringGetTypeID


CGRect = namedtuple("CGRect", ["x", "y", "width", "height"])
CFRange = namedtuple("CFRange", ["location", "length"])
CGPoint = namedtuple("CGPoint", ["x", "y"])
CGSize = namedtuple("CGSize", ["width", "height"])


class Converter:
    def __init__(self, axuielementclass=None):
        self.app_ref_class = axuielementclass

    def convert_value(self, value):
        if CFGetTypeID(value) == CFStringGetTypeID():
            try:
                return str(value)
            except UnicodeEncodeError:
                return str(value.encode("utf-8"))
        if CFGetTypeID(value) == AXUIElementGetTypeID():
            return self.convert_app_ref(value)
        if CFGetTypeID(value) == CFArrayGetTypeID():
            return self.convert_list(value)
        if AXValueGetType(value) == kAXValueCGSizeType:
            return self.convert_size(value)
        if AXValueGetType(value) == kAXValueCGPointType:
            return self.convert_point(value)
        if AXValueGetType(value) == kAXValueCFRangeType:
            return self.convert_range(value)
        if AXValueGetType(value) == kAXValueCGRectType:
            return self.convert_rect(value)
        else:
            return value

    def convert_list(self, value):
        return [self.convert_value(item) for item in value]

    def convert_app_ref(self, value):
        return self.app_ref_class(ref=value)

    def convert_size(self, value):
        repr_searched = re.search("{.*}", str(value)).group()
        size = NSSizeFromString(repr_searched)

        return CGSize(size.width, size.height)

    def convert_point(self, value):
        repr_searched = re.search("{.*}", str(value)).group()
        point = NSPointFromString(repr_searched)

        return CGPoint(point.x, point.y)

    def convert_range(self, value):
        repr_searched = re.search("{.*}", str(value)).group()
        range = NSRangeFromString(repr_searched)

        return CFRange(range.location, range.length)

    def convert_rect(self, value):
        repr_searched = re.search("{.*}", str(value)).group()
        rect = NSRectFromString(repr_searched)

        return CGRect(rect.origin.x, rect.origin.y, rect.size.width, rect.size.height)
