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

W, H = 900, 460

dwg = svgwrite.Drawing("/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/netbox/netbox-api-3.svg", size=(W, H))
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(id="inh", markerWidth=12, markerHeight=10, refX=1, refY=5, orient="auto")
marker.add(dwg.polygon([(0,0),(12,5),(0,10)], fill=BG, stroke=ARROW, stroke_width=1.5))
dwg.defs.add(marker)

dwg.add(dwg.text("Serializer 繼承體系", insert=(W/2, 30), text_anchor="middle",
                  font_family=FONT, font_size=15, font_weight="700", fill=TEXT_PRIMARY))

bw, bh = 220, 60

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

# BaseModelSerializer (top)
cls_box(W/2-bw/2, 50, bw, 82, "BaseModelSerializer",
        methods=["url: HyperlinkedIdentityField","display: SerializerMethodField","__init__(nested, fields, omit)", "fields: property"],
        fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# ValidatedModelSerializer
cls_box(W/2-bw/2, 190, bw, 52, "ValidatedModelSerializer",
        methods=["validate(data)", "full_clean()"])

# Mixins on left
mixin_x = 40
mixin_items = [
    ("CustomFieldModel\nSerializer", ["custom_fields"], 230),
    ("TaggableModel\nSerializer", ["tags","create()","update()"], 310),
    ("ChangeLogMessage\nSerializer", ["changelog_message: str"], 385),
]
for i, (name, ms, my) in enumerate(mixin_items):
    cls_box(mixin_x, my, 180, 55, name, methods=ms)
    inh(mixin_x+180, my+27, W/2-bw/2-2, 330)

# NetBoxModelSerializer
cls_box(W/2-bw/2, 300, bw, 46, "NetBoxModelSerializer", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# PrimaryModelSerializer
cls_box(W/2-bw/2, 400, bw, 46, "PrimaryModelSerializer", methods=["<<OwnerMixin>>"])

# Inheritance arrows
inh(W/2, 132, W/2, 188)
inh(W/2, 242, W/2, 298)
inh(W/2, 346, W/2, 398)

dwg.save()
print("saved api-3.svg")
