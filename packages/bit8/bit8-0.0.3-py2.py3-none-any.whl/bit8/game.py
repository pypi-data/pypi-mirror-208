def overlapping_area(p1, d1, p2, d2):
    y1, x1 = p1
    y12, x12 = y1 + d1[0], x1 + d1[1]
    y2, x2 = p2
    y22, x22 = y2 + d2[0], x2 + d2[1]
    x_overlap = x12 - x2 if x1 < x2 else x22 - x1
    y_overlap = y12 - y2 if y1 < y2 else y22 - y1
    m = -1 if x_overlap < 0 > y_overlap else 1
    return m * x_overlap * y_overlap
