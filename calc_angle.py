import cv2
import glob

def is_edge(img, r, c):
    EDGE_THRESHOLD = 128
    return img.item(r, c) >= EDGE_THRESHOLD


def is_edge_start(img, r, c):
    return is_edge(img, r, c) and (
        is_edge(img, r - 1, c) or
        (c > 0 and is_edge(img, r - 1, c - 1)) or
        (c < img.shape[1] - 1 and is_edge(img, r - 1, c + 1)))


def bfs_up(img, r0, c0):
    assert r0 > 0
    curr = [c0]
    r = r0
    while r > 0:
        next = []
        for c in curr:
            if c > 0 and is_edge(img, r - 1, c - 1):
                if c - 1 not in next[-2:]:
                    next.append(c - 1)
            if is_edge(img, r - 1, c):
                if c not in next[-1:]:
                    next.append(c)
            if c < img.shape[1] - 1 and is_edge(img, r - 1, c + 1):
                next.append(c + 1)
        if len(next) == 0:
            break
        curr = next
        r -= 1
    return r, curr


def left_edge(img):
    """ If the edge doesn't cross the bottom row, returns None.
    Otherwise finds the beginning of the edge at the bottom and traverses connected white pixels (breadth-first search) upwards. Assumes the leftmost pixel on the uppermost row reached to be the other endpoint. """
    r = img.shape[0] - 1
    for c in range(0, img.shape[1]):
        if is_edge_start(img, r, c):
            r1, c1s = bfs_up(img, r, c)
            return (r, c), (r1, c1s[0])


def right_edge(img):
    r = img.shape[0] - 1
    for c in range(img.shape[1] - 1, -1, -1):
        if is_edge_start(img, r, c):
            r1, c1s = bfs_up(img, r, c)
            return (r, c), (r1, c1s[-1])


def find_line(f, img):
    # infer the equations for left and right edge of the line
    l = left_edge(img)
    r = right_edge(img)
    print f, l, r

    # assume their bisector to be our desired trajectory

    img_large = enlarged(cv2.cvtColor(img, cv2.COLOR_GRAY2RGB))
    img_overlay = img_large.copy()
    if l:
        cv2.line(img_overlay, (l[0][1] * 10 + 5, l[0][0] * 10 + 5), (l[1][1] * 10 + 5, l[1][0] * 10 + 5), (0, 0, 255))
    if r:
        cv2.line(img_overlay, (r[0][1] * 10 + 5, r[0][0] * 10 + 5), (r[1][1] * 10 + 5, r[1][0] * 10 + 5), (0, 0, 255))
    cv2.imshow(f, cv2.addWeighted(img_large, 0.25, img_overlay, 0.75, 0))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def enlarged(img):
    return cv2.resize(img, (img.shape[1] * 10, img.shape[0] * 10), interpolation=cv2.INTER_NEAREST)


def show_pair(name, img1, img2):
    cv2.imshow(name + '1', enlarged(img1))
    cv2.imshow(name + '2', enlarged(img2))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_overlaid(name, img, overlay):
    img1 = enlarged(img)
    img2 = enlarged(overlay)
    cv2.imshow(name, cv2.addWeighted(img1, 0.75, img2, 0.25, 0))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


for f in sorted(glob.glob('????-*.jpg')):
    img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
    if 'edges' in f:
        find_line(f, img)