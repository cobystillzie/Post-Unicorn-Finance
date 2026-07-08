# Generate compact SVG path data for the atlas choropleth ("Where in the world").
# One-time build step: reads a local copy of Natural Earth 110m admin-0 countries
# (public domain, https://www.naturalearthdata.com/) -> writes scripts/world_map_paths.json
# consumed by build_atlas_artifact.py. Re-run only if the source geojson changes.
#
# Usage: python scripts/gen_world_map_paths.py <path-to-ne_110m_admin_0_countries.geojson>
import json
import math
import os
import sys

W = 1000.0  # target viewBox width; height derived from projection aspect

# Natural Earth projection (Savric et al. 2011) - pleasing compromise projection,
# trivial polynomial, no external library needed.
def project(lon_deg: float, lat_deg: float) -> tuple[float, float]:
    lam = math.radians(lon_deg)
    phi = math.radians(lat_deg)
    p2, p4 = phi * phi, phi ** 4
    x = lam * (0.8707 - 0.131979 * p2 - 0.013791 * p4
               + p4 * p4 * p2 * (0.003971 - 0.001529 * p4))
    y = phi * (1.007226 + p2 * (0.015085 + p4 * (-0.044475 + 0.028874 * p2 - 0.005916 * p4)))
    return x, y


def ring_area(ring: list[tuple[float, float]]) -> float:
    a = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def main() -> None:
    src = sys.argv[1]
    with open(src, encoding='utf-8') as f:
        geo = json.load(f)

    # First pass: project everything to find global bounds (Antarctica excluded).
    feats = []
    for feat in geo['features']:
        name = feat['properties'].get('ADMIN') or feat['properties'].get('NAME')
        if name == 'Antarctica':
            continue
        geom = feat['geometry']
        polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
        projected = [[[project(lon, lat) for lon, lat in ring] for ring in poly] for poly in polys]
        feats.append((name, projected))

    all_pts = [pt for _, polys in feats for poly in polys for ring in poly for pt in ring]
    min_x = min(p[0] for p in all_pts)
    max_x = max(p[0] for p in all_pts)
    min_y = min(p[1] for p in all_pts)
    max_y = max(p[1] for p in all_pts)
    scale = W / (max_x - min_x)
    H = (max_y - min_y) * scale

    def to_px(pt: tuple[float, float]) -> tuple[float, float]:
        # y flipped: projection y grows north, SVG y grows down
        return ((pt[0] - min_x) * scale, (max_y - pt[1]) * scale)

    MIN_RING_PX2 = 9.0  # drop specks < ~3x3 px unless they are all a country has

    countries = {}
    for name, polys in feats:
        rings_px = []
        for poly in polys:
            for ring in poly:  # exterior + holes; rendered with fill-rule evenodd
                rings_px.append([to_px(p) for p in ring])
        kept = [r for r in rings_px if ring_area(r) >= MIN_RING_PX2]
        if not kept:  # microstates: keep the largest speck rather than vanish
            kept = [max(rings_px, key=ring_area)]
        d_parts = []
        for r in kept:
            pts = ['%g %g' % (round(x, 1), round(y, 1)) for x, y in r]
            d_parts.append('M' + 'L'.join(pts) + 'Z')
        big = max(kept, key=ring_area)
        cx = sum(p[0] for p in big) / len(big)
        cy = sum(p[1] for p in big) / len(big)
        countries[name] = {'d': ''.join(d_parts), 'cx': round(cx, 1), 'cy': round(cy, 1)}

    # Countries absent from 110m data but present in the atlas -> centroid dots.
    extra_centroids = {'Singapore': (103.82, 1.35)}
    for name, (lon, lat) in extra_centroids.items():
        if name not in countries:
            cx, cy = to_px(project(lon, lat))
            countries[name] = {'d': '', 'cx': round(cx, 1), 'cy': round(cy, 1)}

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'world_map_paths.json')
    payload = {'viewBox': [0, 0, round(W), round(H, 1)], 'countries': countries}
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, separators=(',', ':'))
    print('WROTE', out_path, os.path.getsize(out_path), 'bytes,', len(countries), 'countries, H=%.1f' % H)


if __name__ == '__main__':
    main()
