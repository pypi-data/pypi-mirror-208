from typing import Optional, Dict, Tuple

import xml.etree.ElementTree as ET


def getTag(root: ET.Element, tag: str) -> Optional[str]:
    element = root.find(tag)
    if element is None:
        return None

    return element.text


def toFloat(rootEl: ET.Element, firstEl: str, secondEl: str) -> Tuple[Optional[float], Optional[float]]:
    firstVal = getTag(rootEl, firstEl)
    secondVal = getTag(rootEl, secondEl)

    if firstVal is None or secondVal is None:
        return (None, None)

    return (float(firstVal), float(secondVal))


def getBoxes(bndbox: ET.Element) -> Optional[Dict[str, float]]:
    xmin, ymin = toFloat(bndbox, "xmin", "ymin")
    xmax, ymax = toFloat(bndbox, "xmax", "ymax")

    if xmax is None: return None
    if xmin is None: return None
    if ymax is None: return None
    if ymin is None: return None

    return {
        "top_left_x": xmin,
        "top_left_y": ymin,
        "width": xmax - xmin,
        "height": ymax - ymin,
    }