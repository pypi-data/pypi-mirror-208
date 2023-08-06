from robertcommonbasic.basic.re.utils import format_name, find_match
from robertcommonbasic.basic.dt.utils import parse_time


def test():
    name = 'Bldg3_Area1_hourly_SiteId_08-14-2021-23_00_00_PM_EDT.zip'
    time = format_name(name, r'[^0-9]+', '')
    tm = parse_time(time)
    print(tm)


def get_expression_points(expression: str, pattern: str = r'<%(.*?)%>') -> list:
    return find_match(expression, pattern)


points = get_expression_points('if <%Bucket Brigade.Real4%> and <%Bucket@Brigade_Real5%>')
#points = get_expression_points('<%Bucket Brigade.Real4%>')
print(points)
