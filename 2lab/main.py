import math
import itertools as it
import functools as ft
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon


def polygon(points):
    return tuple(map(tuple, points))


def vector(a, b):
    return b[0] - a[0], b[1] - a[1]


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def compose(*funcs):
    return lambda x: ft.reduce(lambda v, f: f(v), funcs, x)


def apply_point(func):
    return lambda p: tuple(map(func, p))


def regular_polygon(n, r=1, center=(0, 0)):
    cx, cy = center
    return polygon(
        (cx + r * math.cos(2 * math.pi * i / n),
         cy + r * math.sin(2 * math.pi * i / n))
        for i in range(n)
    )


def gen_rectangle(width=1, height=0.8, gap=0.35, start_x=0, y=0):
    step = width + gap
    return map(
        lambda i: (
            (start_x + i * step, y),
            (start_x + i * step + width, y),
            (start_x + i * step + width, y + height),
            (start_x + i * step, y + height)
        ),
        it.count()
    )


def gen_triangle(side=1, gap=0.35, start_x=0, y=0):
    h = side * math.sqrt(3) / 2
    step = side + gap
    return map(
        lambda i: (
            (start_x + i * step, y),
            (start_x + i * step + side / 2, y + h),
            (start_x + i * step + side, y)
        ),
        it.count()
    )


def gen_reversed_triangle(side=1, gap=0.35, start_x=0, y=0):
    h = side * math.sqrt(3) / 2
    step = side + gap
    return map(
        lambda i: (
            (start_x + i * step + side, y),
            (start_x + i * step + side / 2, y - h),
            (start_x + i * step, y)
        ),
        it.count()
    )


def gen_hexagon(side=0.55, gap=0.35, start_x=0, y=0):
    h = math.sqrt(3) * side
    step = 2 * side + gap
    return map(
        lambda i: (
            (start_x + i * step + side / 2, y),
            (start_x + i * step + 3 * side / 2, y),
            (start_x + i * step + 2 * side, y + h / 2),
            (start_x + i * step + 3 * side / 2, y + h),
            (start_x + i * step + side / 2, y + h),
            (start_x + i * step, y + h / 2)
        ),
        it.count()
    )


def tr_translate(dx, dy):
    return apply_point(lambda p: (p[0] + dx, p[1] + dy))


def tr_rotate(angle, center=(0, 0)):
    cx, cy = center
    c, s = math.cos(angle), math.sin(angle)

    def rotate(p):
        x, y = p[0] - cx, p[1] - cy
        return x * c - y * s + cx, x * s + y * c + cy

    return apply_point(rotate)


def tr_symmetry(axis="x"):
    variants = {
        "x": lambda p: (p[0], -p[1]),
        "y": lambda p: (-p[0], p[1]),
        "origin": lambda p: (-p[0], -p[1])
    }
    return apply_point(variants[axis])


def tr_homothety(k, center=(0, 0)):
    cx, cy = center
    return apply_point(lambda p: (cx + k * (p[0] - cx), cy + k * (p[1] - cy)))


def transform_sequence(polygons, *transforms):
    return map(compose(*transforms), polygons)


def visualize(polygons, title="", limit=None, figsize=(9, 4), xlim=None, ylim=None):
    fig, ax = plt.subplots(figsize=figsize)

    if limit is not None:
        polygons = it.islice(polygons, limit)

    for p in polygons:
        ax.add_patch(MplPolygon(
            p,
            closed=True,
            fill=True,
            alpha=0.15,
            edgecolor="black",
            linewidth=1.5
        ))

    ax.axhline(0, color="gray", linewidth=1)
    ax.axvline(0, color="gray", linewidth=1)
    ax.set_aspect("equal")
    ax.grid(True)

    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    if not xlim and not ylim:
        ax.autoscale_view()

    ax.set_title(title)
    plt.show()


def area(p):
    pairs = zip(p, p[1:] + p[:1])
    s = ft.reduce(
        lambda acc, pair: acc + pair[0][0] * pair[1][1] - pair[1][0] * pair[0][1],
        pairs,
        0
    )
    return abs(s) / 2


def side_lengths(p):
    return tuple(map(lambda pair: math.dist(pair[0], pair[1]), zip(p, p[1:] + p[:1])))


def perimeter(p):
    return ft.reduce(lambda s, x: s + x, side_lengths(p), 0)


def min_side(p):
    return min(side_lengths(p))


def is_convex(p):
    triples = zip(p, p[1:] + p[:1], p[2:] + p[:2])
    crosses = tuple(map(lambda t: cross(vector(t[0], t[1]), vector(t[1], t[2])), triples))
    return not (tuple(filter(lambda x: x > 0, crosses)) and tuple(filter(lambda x: x < 0, crosses)))


def point_inside_convex(point, p):
    pairs = zip(p, p[1:] + p[:1])
    crosses = tuple(map(lambda pair: cross(vector(pair[0], pair[1]), vector(pair[0], point)), pairs))
    return not (tuple(filter(lambda x: x > 0, crosses)) and tuple(filter(lambda x: x < 0, crosses)))


def flt_convex_polygon():
    return is_convex


def flt_angle_point(point):
    return lambda p: point in p


def flt_square(max_square):
    return lambda p: area(p) < max_square


def flt_short_side(max_length):
    return lambda p: min_side(p) < max_length


def flt_point_inside(point):
    return lambda p: is_convex(p) and point_inside_convex(point, p)


def flt_polygon_angles_inside(inner_polygon):
    return lambda p: is_convex(p) and any(map(lambda point: point_inside_convex(point, p), inner_polygon))


def iterator_decorator(action):
    def decorator(func):
        @ft.wraps(func)
        def wrapper(*iterators, **kwargs):
            return func(*map(action, iterators), **kwargs)
        return wrapper
    return decorator


def tr_translate_decorator(dx, dy):
    return iterator_decorator(lambda iterator: map(tr_translate(dx, dy), iterator))


def tr_rotate_decorator(angle, center=(0, 0)):
    return iterator_decorator(lambda iterator: map(tr_rotate(angle, center), iterator))


def tr_symmetry_decorator(axis="x"):
    return iterator_decorator(lambda iterator: map(tr_symmetry(axis), iterator))


def tr_homothety_decorator(k, center=(0, 0)):
    return iterator_decorator(lambda iterator: map(tr_homothety(k, center), iterator))


def flt_short_side_decorator(max_length):
    return iterator_decorator(lambda iterator: filter(flt_short_side(max_length), iterator))


def dist0(point):
    return math.hypot(point[0], point[1])


def agr_origin_nearest(current, p):
    nearest = ft.reduce(lambda a, b: a if dist0(a) < dist0(b) else b, p)
    return nearest if current is None or dist0(nearest) < dist0(current) else current


def agr_max_side(current, p):
    value = ft.reduce(lambda a, b: a if a > b else b, side_lengths(p))
    return value if current is None or value > current else current


def agr_min_area(current, p):
    value = area(p)
    return value if current is None or value < current else current


def agr_perimeter(total, p):
    return total + perimeter(p)


def agr_area(total, p):
    return total + area(p)


def zip_tuple(*tuples):
    return ft.reduce(lambda a, b: a + b, tuples, tuple())


def zip_polygons(*iterators):
    return map(lambda polygons: zip_tuple(*polygons), zip(*iterators))


def count_2D(start_x=0, start_y=0, step_x=1, step_y=1):
    return map(lambda i: (start_x + i * step_x, start_y + i * step_y), it.count())


def show_lines_between_polygons():
    m1, m2 = 0.18, 0.65

    def quad(i):
        x1 = 1.0 + i * 0.9
        x2 = x1 + 0.55
        return (
            (x1, m1 * x1),
            (x2, m1 * x2),
            (x2, m2 * x2),
            (x1, m2 * x1)
        )

    fig, ax = plt.subplots(figsize=(9, 5))
    xs = (0, 7)
    ax.plot(xs, tuple(map(lambda x: m1 * x, xs)), linestyle="--", linewidth=1)
    ax.plot(xs, tuple(map(lambda x: m2 * x, xs)), linestyle="--", linewidth=1)

    for p in map(quad, range(6)):
        ax.add_patch(MplPolygon(p, closed=True, fill=True, alpha=0.15, edgecolor="black", linewidth=1.5))

    ax.axhline(0, color="gray", linewidth=1)
    ax.axvline(0, color="gray", linewidth=1)
    ax.set_xlim(-0.2, 7)
    ax.set_ylim(-0.2, 4.8)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_title("Четырёхугольники между двумя прямыми")
    plt.show()


def show_filter_angles_inside():
    polys = tuple(it.islice(gen_rectangle(width=1.2, height=1.2, gap=0.25, start_x=-3, y=-0.6), 7))
    inner = ((0.1, 0.1), (0.35, 0.1), (0.2, 0.35))
    filtered = tuple(filter(flt_polygon_angles_inside(inner), polys))

    fig, ax = plt.subplots(figsize=(9, 4))

    for p in polys:
        ax.add_patch(MplPolygon(p, closed=True, fill=True, alpha=0.08, edgecolor="gray", linewidth=1))

    for p in filtered:
        ax.add_patch(MplPolygon(p, closed=True, fill=True, alpha=0.2, edgecolor="black", linewidth=2))

    ax.add_patch(MplPolygon(inner, closed=True, fill=True, alpha=0.35, edgecolor="black", linewidth=1.5))
    ax.scatter(tuple(map(lambda p: p[0], inner)), tuple(map(lambda p: p[1], inner)), zorder=5)

    ax.axhline(0, color="gray", linewidth=1)
    ax.axvline(0, color="gray", linewidth=1)
    ax.set_xlim(-3.5, 5.8)
    ax.set_ylim(-1.0, 1.3)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_title("Фильтр: прямоугольник содержит угол заданного полигона")
    plt.show()

    print("Количество фигур после фильтра:", len(filtered))


@tr_rotate_decorator(math.pi / 6)
def show_rotated(polygons):
    visualize(polygons, "Поворот через декоратор")


@flt_short_side_decorator(0.5)
def show_filtered(polygons):
    visualize(polygons, "Фильтр через декоратор: короткая сторона < 0.5")


def run_all_demos():
    visualize(gen_rectangle(start_x=-4), "7 прямоугольников", limit=7)
    visualize(gen_triangle(start_x=-4), "7 треугольников", limit=7)
    visualize(gen_hexagon(start_x=-4), "7 шестиугольников", limit=7)

    angle = math.pi / 6
    bands = [
        transform_sequence(it.islice(gen_rectangle(width=1, height=0.35, gap=0.1, start_x=-4), 7),
                           tr_translate(0, y), tr_rotate(angle))
        for y in (-0.6, 0, 0.6)
    ]
    visualize(it.chain(*bands), "Три параллельные ленты")

    band1 = transform_sequence(
        it.islice(gen_rectangle(width=0.8, height=0.3, gap=0.15, start_x=-4), 9),
        tr_rotate(math.pi / 6),
        tr_translate(1.5, 0.5)
    )
    band2 = transform_sequence(
        it.islice(gen_rectangle(width=0.8, height=0.3, gap=0.15, start_x=-4), 9),
        tr_rotate(-math.pi / 6),
        tr_translate(1.5, 0.5)
    )
    visualize(it.chain(band1, band2), "Две пересекающиеся ленты")

    upper = it.islice(gen_triangle(side=0.8, gap=0.2, start_x=-4, y=0.4), 7)
    lower = map(tr_symmetry("x"), it.islice(gen_triangle(side=0.8, gap=0.2, start_x=-4, y=0.4), 7))
    visualize(it.chain(upper, lower), "Симметричные ленты треугольников")

    show_lines_between_polygons()

    base = ((0, 0), (1, 0), (1, 0.7), (0, 0.7))
    polys = map(lambda i: tr_translate(i * 1.4 - 5, 0)(tr_homothety(0.4 + i * 0.12)(base)), range(12))
    result = tuple(it.islice(filter(flt_square(1.2), polys), 6))
    visualize(result, "Фильтр по площади: выбрано 6 фигур", xlim=(-5.5, 4), ylim=(-0.2, 1.8))
    print("Количество отфильтрованных фигур:", len(result))

    polys = map(lambda k: tr_translate(k * 1.4, 0)(tr_homothety(k)(((0, 0), (1, 0), (1, 0.4), (0, 0.4)))),
                it.count(0.2, 0.15))
    visualize(it.islice(filter(flt_short_side(0.25), it.islice(polys, 15)), 4), "Фильтрация по кратчайшей стороне")

    show_filter_angles_inside()

    show_rotated(it.islice(gen_rectangle(width=1, height=0.4, gap=0.2, start_x=-4), 7))

    polys = map(lambda k: tr_translate(k * 1.4, 0)(tr_homothety(k)(((0, 0), (1, 0), (1, 0.4), (0, 0.4)))),
                it.count(0.2, 0.15))
    show_filtered(it.islice(polys, 15))

    sample = tuple(it.islice(gen_rectangle(width=1, height=0.5, gap=0.2, start_x=-2), 5))
    print("Ближайший угол к началу координат:", ft.reduce(agr_origin_nearest, sample, None))
    print("Самая длинная сторона:", ft.reduce(agr_max_side, sample, None))
    print("Минимальная площадь:", ft.reduce(agr_min_area, sample, None))
    print("Суммарный периметр:", ft.reduce(agr_perimeter, sample, 0))
    print("Суммарная площадь:", ft.reduce(agr_area, sample, 0))

    iterator1 = iter([((1, 1), (2, 2), (3, 1)), ((11, 11), (12, 12), (13, 11))])
    iterator2 = iter([((1, -1), (2, -2), (3, -1)), ((11, -11), (12, -12), (13, -11))])
    print(list(zip_polygons(iterator1, iterator2)))

    upper = it.islice(gen_triangle(side=1, gap=0.2, start_x=-4, y=0), 7)
    lower = it.islice(gen_reversed_triangle(side=1, gap=0.2, start_x=-4, y=0), 7)
    visualize(zip_polygons(upper, lower), "Склейка треугольников zip_polygons")

    print(tuple(it.islice(count_2D(start_x=0, start_y=0, step_x=2, step_y=3), 5)))


if __name__ == "__main__":
    run_all_demos()
