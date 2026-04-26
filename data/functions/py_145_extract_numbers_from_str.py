import re
from typing import List


def extract_numbers_from_str(s: str) -> List[float]:
    matches = re.findall(r'-?\d+(?:\.\d+)?', s)
    return [float(m) for m in matches]
