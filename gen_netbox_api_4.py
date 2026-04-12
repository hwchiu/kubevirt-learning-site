import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 860, 430

dwg = svgwrite.Drawing("/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/netbox/netbox-api-4.svg", size=(W, H))
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(id="inh", markerWidth=12, markerHeight=10, refX=1, refY=5, orient="auto")
marker.add(dwg.polygon([(0,0),(12,5),(0,10)], fill=BG, stroke=ARROW, stroke_width=1.5))
dwg.defs.add(marker)

dwg.add(dwg.text("FilterSet 繼承鏈", insert=(W/2, 30), text_anchor="middle",
                  font_family=FONT, font_size=15, font_weight="700", fill=TEXT_PRIMARY))

def cls_box(x, y, w, h, name, methods=None, fill=BOX_FILL, stroke=BOX_STROKE):
    dwg.add(dwg.rect((x, y), (w, h), rx=6, ry=6, fill=fill, stroke=stroke, stroke_width=1.5))
    dwg.add(dwg.text(name, insert=(x+w/2, y+20), text_anchor="middle", font_family=FONT, font_size=12, font_weight="700", fill=TEXT_PRIMARY))
    ly = y + 36
    if methods:
        dwg.add(dwg.line((x+8, ly-4), (x+w-8, ly-4), stroke=BOX_STROKE, stroke_width=0.8))
        for m in methods:
            dwg.add(dwg.text(m, insert=(x+10, ly+10), font_family=FONT, font_size=9, fill=TEXT_SECONDARY))
            ly += 13

def inh(x1, y1, x2, y2):
    dwg.add(dwg.line((x1, y1), (x2, y2), stroke=ARROW, stroke_width=1.5, marker_end="url(#inh)"))

bw = 240

# Linear chain: BaseFilterSet -> ChangeLoggedModelFilterSet -> NetBoxModelFilterSet
# Then two leaves
cls_box(W/2-bw/2, 50, bw, 62, "BaseFilterSet",
        methods=["FILTER_DEFAULTS: dict", "get_additional_lookups()"],
        fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

cls_box(W/2-bw/2, 170, bw, 70, "ChangeLoggedModelFilterSet",
        methods=["created: MultiValueDateTimeFilter","last_updated: MultiValueDateTimeFilter","filter_by_request()"])

cls_box(W/2-bw/2, 300, bw, 68, "NetBoxModelFilterSet",
        methods=["q: CharFilter", "tag: TagFilter", "tag_id: TagIDFilter", "search()"],
        fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# Two leaf classes
cls_box(90, 390, 200, 38, "PrimaryModelFilterSet", methods=["<<OwnerFilterMixin>>"])
cls_box(550, 390, 220, 38, "OrganizationalModelFilterSet", methods=["<<OwnerFilterMixin>>"])

inh(W/2, 112, W/2, 168)
inh(W/2, 240, W/2, 298)
inh(W/2, 368, 190, 388)
inh(W/2, 368, 660, 388)

dwg.save()
print("saved api-4.svg")
