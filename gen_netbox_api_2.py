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

W, H = 820, 400

dwg = svgwrite.Drawing("/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/netbox/netbox-api-2.svg", size=(W, H))
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(id="inh", markerWidth=12, markerHeight=10, refX=1, refY=5, orient="auto")
marker.add(dwg.polygon([(0,0),(12,5),(0,10)], fill=BG, stroke=ARROW, stroke_width=1.5))
dwg.defs.add(marker)

dwg.add(dwg.text("ViewSet 繼承鏈", insert=(W/2, 30), text_anchor="middle",
                  font_family=FONT, font_size=15, font_weight="700", fill=TEXT_PRIMARY))

def cls_box(x, y, w, h, name, methods=None, stereotypes=None, fill=BOX_FILL, stroke=BOX_STROKE):
    dwg.add(dwg.rect((x, y), (w, h), rx=6, ry=6, fill=fill, stroke=stroke, stroke_width=1.5))
    dwg.add(dwg.text(name, insert=(x+w/2, y+20), text_anchor="middle", font_family=FONT, font_size=12, font_weight="700", fill=TEXT_PRIMARY))
    ly = y + 36
    if stereotypes:
        for s in stereotypes:
            dwg.add(dwg.text(f"<<{s}>>", insert=(x+w/2, ly), text_anchor="middle", font_family=FONT, font_size=9, fill="#7c3aed"))
            ly += 14
    if methods:
        dwg.add(dwg.line((x+10, ly-4), (x+w-10, ly-4), stroke=BOX_STROKE, stroke_width=0.8))
        for m in methods:
            dwg.add(dwg.text(m, insert=(x+10, ly+10), font_family=FONT, font_size=9, fill=TEXT_SECONDARY))
            ly += 14

def inh_arrow(x1, y1, x2, y2):
    dwg.add(dwg.line((x1, y1), (x2, y2), stroke=ARROW, stroke_width=1.5, marker_end="url(#inh)"))

# GenericViewSet (top)
bw = 240
cls_box(W/2-bw/2, 55, bw, 70, "GenericViewSet",
        methods=["get_queryset()", "get_serializer_class()"], fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# BaseViewSet
cls_box(W/2-bw/2, 180, bw, 85, "BaseViewSet",
        methods=["brief: bool", "initial(request)", "initialize_request(request)", "get_queryset()"])

# Two subclasses
cls_box(120, 335, bw+10, 55, "NetBoxReadOnlyModelViewSet",
        stereotypes=["RetrieveModelMixin","ListModelMixin"])

cls_box(460, 335, bw+30, 90, "NetBoxModelViewSet",
        stereotypes=["BulkUpdateModelMixin","CreateModelMixin","UpdateModelMixin","DestroyModelMixin"])

# Arrows
inh_arrow(W/2, 125, W/2, 178)
inh_arrow(200+20, 265, 220, 333)
inh_arrow(W/2+10, 265, 500, 333)

dwg.save()
print("saved api-2.svg")
