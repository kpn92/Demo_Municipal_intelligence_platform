from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode

import qrcode
from PIL import Image as PillowImage
from PIL import ImageDraw, ImageFont
from pyproj import Transformer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.config import settings
from app.models.cleaning_plan_assignment import CleaningPlanAssignment


FONT_NAME = "AssignmentFont"
BOLD_FONT_NAME = "AssignmentFontBold"
WGS84_TO_GREEK_GRID = Transformer.from_crs("EPSG:4326", "EPSG:2100", always_xy=True)


def build_cleaning_plan_assignment_pdf(assignment: CleaningPlanAssignment) -> bytes:
    register_pdf_fonts()
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=13 * mm,
        leftMargin=13 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title=f"Πλάνο καθαρισμού #{assignment.id}",
    )
    styles = build_styles()
    route_url = build_assignment_route_url(assignment.id)
    notes_block = build_notes_block(assignment, styles)
    story = [
        build_header_table(assignment, route_url, styles),
        Spacer(1, 6 * mm),
        build_summary_table(assignment, styles),
        Spacer(1, 5 * mm),
        Paragraph("Χάρτης ανάθεσης", styles["SectionTitle"]),
        build_assignment_map_block(assignment, styles),
        Spacer(1, 5 * mm),
        Paragraph("Δρόμοι καθαρισμού", styles["SectionTitle"]),
        build_roads_table(assignment, styles),
    ]
    if notes_block:
        story.extend([Spacer(1, 5 * mm), notes_block])
    document.build(story)
    return buffer.getvalue()


def build_assignment_route_url(assignment_id: int) -> str:
    query = urlencode({"assignment_id": assignment_id})
    return f"{settings.frontend_base_url.rstrip('/')}/assignment-route.html?{query}"


def register_pdf_fonts() -> None:
    if FONT_NAME in pdfmetrics.getRegisteredFontNames():
        return

    font_candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    bold_candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    font_path = next((path for path in font_candidates if path.exists()), None)
    bold_path = next((path for path in bold_candidates if path.exists()), font_path)
    if not font_path:
        return

    pdfmetrics.registerFont(TTFont(FONT_NAME, str(font_path)))
    if bold_path:
        pdfmetrics.registerFont(TTFont(BOLD_FONT_NAME, str(bold_path)))


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    normal_font = FONT_NAME if FONT_NAME in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    bold_font = BOLD_FONT_NAME if BOLD_FONT_NAME in pdfmetrics.getRegisteredFontNames() else normal_font
    return {
        "Title": ParagraphStyle(
            "AssignmentTitle",
            parent=base["Title"],
            fontName=bold_font,
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#172033"),
            spaceAfter=4,
        ),
        "Meta": ParagraphStyle(
            "AssignmentMeta",
            parent=base["Normal"],
            fontName=normal_font,
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#51617a"),
        ),
        "Normal": ParagraphStyle(
            "AssignmentNormal",
            parent=base["Normal"],
            fontName=normal_font,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#172033"),
        ),
        "Strong": ParagraphStyle(
            "AssignmentStrong",
            parent=base["Normal"],
            fontName=bold_font,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#172033"),
        ),
        "SectionTitle": ParagraphStyle(
            "AssignmentSectionTitle",
            parent=base["Heading2"],
            fontName=bold_font,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#172033"),
            spaceAfter=5,
        ),
        "TableHeader": ParagraphStyle(
            "AssignmentTableHeader",
            parent=base["Normal"],
            fontName=bold_font,
            fontSize=9,
            leading=12,
            textColor=colors.white,
        ),
        "Right": ParagraphStyle(
            "AssignmentRight",
            parent=base["Normal"],
            fontName=normal_font,
            fontSize=8,
            leading=10,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#51617a"),
        ),
        "QrCaption": ParagraphStyle(
            "AssignmentQrCaption",
            parent=base["Normal"],
            fontName=bold_font,
            fontSize=7.5,
            leading=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#172033"),
        ),
        "Checkbox": ParagraphStyle(
            "AssignmentCheckbox",
            parent=base["Normal"],
            fontName=normal_font,
            fontSize=12,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#172033"),
        ),
    }


def build_header_table(assignment: CleaningPlanAssignment, route_url: str, styles: dict[str, ParagraphStyle]) -> Table:
    qr = qrcode.make(route_url)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_image = Image(qr_buffer, width=29 * mm, height=29 * mm)
    title = [
        Paragraph("Πλάνο Ανάθεσης Καθαρισμού", styles["Title"]),
        Paragraph(f"Ανάθεση #{assignment.id} · {format_date(assignment.assignment_date)}", styles["Meta"]),
        Paragraph("Σαρώστε το QR για πλήρη χάρτη πλάνου και διαδρομές Google Maps ανά τμήμα.", styles["Meta"]),
    ]
    qr_cell = [qr_image, Paragraph("QR ψηφιακού πλάνου", styles["QrCaption"])]
    table = Table([[title, qr_cell]], colWidths=[136 * mm, 33 * mm])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def build_summary_table(assignment: CleaningPlanAssignment, styles: dict[str, ParagraphStyle]) -> Table:
    employees = ", ".join(
        f"{entry.employee.first_name} {entry.employee.last_name}"
        for entry in assignment.employees
        if entry.employee
    ) or "-"
    rows = [
        ["Περιοχή", assignment.area_name, "Κωδικός", assignment.area_code],
        ["Συνεργείο", assignment.crew_label, "Ημερομηνία", format_date(assignment.assignment_date)],
        ["Προσωπικό", employees, "Άτομα", str(assignment.required_personnel or len(assignment.employees) or "-")],
        ["Εκτίμηση", format_duration(assignment.estimated_duration_min), "Μήκος", format_km(assignment.estimated_length_km)],
        ["Κατάσταση", status_label(assignment.status), "Δρόμοι", str(len(assignment.road_segments))],
    ]
    data = [
        [Paragraph(str(value), styles["Strong" if index in (0, 2) else "Normal"]) for index, value in enumerate(row)]
        for row in rows
    ]
    table = Table(data, colWidths=[23 * mm, 74 * mm, 29 * mm, 43 * mm])
    table.setStyle(default_table_style())
    return table


def build_roads_table(assignment: CleaningPlanAssignment, styles: dict[str, ParagraphStyle]) -> Table:
    roads = sorted(assignment.road_segments, key=lambda road: (road.planned_order is None, road.planned_order or 0, road.id))
    data = [[
        Paragraph("#", styles["TableHeader"]),
        Paragraph("Δρόμος", styles["TableHeader"]),
        Paragraph("Προτεραιότητα", styles["TableHeader"]),
        Paragraph("Διάρκεια", styles["TableHeader"]),
        Paragraph("Κατάσταση", styles["TableHeader"]),
        Paragraph("Έλεγχος", styles["TableHeader"]),
    ]]
    for index, road in enumerate(roads, start=1):
        data.append([
            Paragraph(str(road.planned_order or index), styles["Normal"]),
            Paragraph(road.road_name or road.segment_code, styles["Normal"]),
            Paragraph(priority_label(road.priority), styles["Normal"]),
            Paragraph(format_duration(road.estimated_duration_min), styles["Normal"]),
            Paragraph(status_label(road.status), styles["Normal"]),
            Paragraph("□", styles["Checkbox"]),
        ])

    table = Table(data, colWidths=[10 * mm, 64 * mm, 27 * mm, 22 * mm, 25 * mm, 21 * mm], repeatRows=1)
    table.setStyle(default_table_style(header=True))
    return table


def build_assignment_map_block(assignment: CleaningPlanAssignment, styles: dict[str, ParagraphStyle]) -> Image | Table:
    image_content = build_local_assignment_map_image(assignment)
    if not image_content:
        return build_map_placeholder(
            "Δεν ήταν δυνατή η δημιουργία χάρτη για αυτή την ανάθεση.",
            styles,
        )

    image_buffer = BytesIO(image_content)
    map_image = Image(image_buffer, width=169 * mm, height=82 * mm)
    table = Table([[map_image], [build_map_legend_table(styles)]], colWidths=[169 * mm])
    table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (0, 0), 0),
        ("BOTTOMPADDING", (0, 0), (0, 0), 2),
        ("TOPPADDING", (0, 1), (0, 1), 2),
        ("BOTTOMPADDING", (0, 1), (0, 1), 0),
    ]))
    return table


def build_map_legend_table(styles: dict[str, ParagraphStyle]) -> Table:
    area_symbol = Table([[""]], colWidths=[10 * mm], rowHeights=[3.5 * mm])
    area_symbol.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff3c4")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#fbbc04")),
    ]))
    road_symbol = Table([[""]], colWidths=[10 * mm], rowHeights=[3.5 * mm])
    road_symbol.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, -1), 2, colors.HexColor("#137333")),
    ]))
    data = [[
        area_symbol,
        Paragraph("Περιοχή ανάθεσης", styles["Meta"]),
        road_symbol,
        Paragraph("Ανατεθειμένοι δρόμοι", styles["Meta"]),
    ]]
    table = Table(data, colWidths=[12 * mm, 44 * mm, 12 * mm, 46 * mm])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def build_map_placeholder(message: str, styles: dict[str, ParagraphStyle]) -> Table:
    table = Table([[Paragraph(message, styles["Normal"])]], colWidths=[168 * mm], rowHeights=[38 * mm])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def build_local_assignment_map_image(assignment: CleaningPlanAssignment) -> bytes | None:
    area_feature, road_features = get_assignment_map_features(assignment)
    geotiff_context = load_assignment_geotiff_context(assignment)
    if geotiff_context:
        return build_geotiff_assignment_map_image(area_feature, road_features, geotiff_context)

    features = [feature for feature in [area_feature, *road_features] if feature]
    coordinates = [
        coordinate
        for feature in features
        for coordinate in collect_lng_lat_coordinates(feature)
    ]
    if not coordinates:
        return None

    width = 1280
    height = 660
    padding = 54
    min_lng = min(point[0] for point in coordinates)
    max_lng = max(point[0] for point in coordinates)
    min_lat = min(point[1] for point in coordinates)
    max_lat = max(point[1] for point in coordinates)
    if min_lng == max_lng:
        min_lng -= 0.001
        max_lng += 0.001
    if min_lat == max_lat:
        min_lat -= 0.001
        max_lat += 0.001

    def project(point: list[float]) -> tuple[float, float]:
        lng, lat = point
        x = padding + ((lng - min_lng) / (max_lng - min_lng)) * (width - padding * 2)
        y = height - padding - ((lat - min_lat) / (max_lat - min_lat)) * (height - padding * 2)
        return x, y

    image = PillowImage.new("RGB", (width, height), "#f5f7fb")
    draw = ImageDraw.Draw(image)
    draw_grid(draw, width, height, padding)
    draw_base_road_network(draw, project, (min_lng, min_lat, max_lng, max_lat))

    area_points: list[tuple[float, float]] = []
    if area_feature:
        area_points = [project(point) for point in simplify_points(collect_lng_lat_coordinates(area_feature), 140)]
        if len(area_points) >= 3:
            draw.polygon(area_points, fill="#fff3c4", outline="#fbbc04")

    for feature in road_features:
        road_points = [project(point) for point in simplify_points(collect_lng_lat_coordinates(feature), 24)]
        if len(road_points) < 2:
            continue
        draw.line(road_points, fill="#09261f", width=13, joint="curve")
        draw.line(road_points, fill="#00a878", width=8, joint="curve")

    if len(area_points) >= 3:
        draw.line(area_points + [area_points[0]], fill="#ffffff", width=9)
        draw.line(area_points + [area_points[0]], fill="#fbbc04", width=6)
        draw.line(area_points + [area_points[0]], fill="#8a5a00", width=2)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def build_geotiff_assignment_map_image(
    area_feature: dict | None,
    road_features: list[dict],
    context: dict,
) -> bytes | None:
    source_image = context["image"].convert("RGB")
    source_width, source_height = source_image.size
    target_width = 1280
    target_height = 660
    scale = min(target_width / source_width, target_height / source_height)
    rendered_width = int(source_width * scale)
    rendered_height = int(source_height * scale)
    offset_x = int((target_width - rendered_width) / 2)
    offset_y = int((target_height - rendered_height) / 2)
    image = PillowImage.new("RGB", (target_width, target_height), "#f5f7fb")
    image.paste(source_image.resize((rendered_width, rendered_height), PillowImage.Resampling.LANCZOS), (offset_x, offset_y))
    draw = ImageDraw.Draw(image)

    def project(point: list[float]) -> tuple[float, float]:
        lng, lat = point
        x_2100, y_2100 = WGS84_TO_GREEK_GRID.transform(lng, lat)
        pixel_x = (x_2100 - context["origin_x"]) / context["pixel_scale_x"]
        pixel_y = (context["origin_y"] - y_2100) / context["pixel_scale_y"]
        return offset_x + pixel_x * scale, offset_y + pixel_y * scale

    area_points: list[tuple[float, float]] = []
    if area_feature:
        area_points = [project(point) for point in simplify_points(collect_lng_lat_coordinates(area_feature), 160)]
        area_points = [point for point in area_points if point_is_near_canvas(point, target_width, target_height)]
        if len(area_points) >= 3:
            overlay = PillowImage.new("RGBA", image.size, (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.polygon(area_points, fill=(251, 188, 4, 34))
            image = PillowImage.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
            draw = ImageDraw.Draw(image)

    for feature in road_features:
        road_points = [project(point) for point in simplify_points(collect_lng_lat_coordinates(feature), 28)]
        road_points = [point for point in road_points if point_is_near_canvas(point, target_width, target_height)]
        if len(road_points) < 2:
            continue
        draw.line(road_points, fill="#ffffff", width=8, joint="curve")
        draw.line(road_points, fill="#137333", width=5, joint="curve")

    if len(area_points) >= 3:
        draw.line(area_points + [area_points[0]], fill="#ffffff", width=10)
        draw.line(area_points + [area_points[0]], fill="#fbbc04", width=7)
        draw.line(area_points + [area_points[0]], fill="#8a5a00", width=2)

    draw_road_labels(draw, road_features, project, target_width, target_height)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def load_assignment_geotiff_context(assignment: CleaningPlanAssignment) -> dict | None:
    path = find_assignment_geotiff_path(assignment)
    if not path:
        return None
    image = PillowImage.open(path)
    tags = image.tag_v2
    pixel_scale = tags.get(33550)
    tiepoint = tags.get(33922)
    if not pixel_scale or not tiepoint:
        return None
    return {
        "image": image,
        "origin_x": float(tiepoint[3]),
        "origin_y": float(tiepoint[4]),
        "pixel_scale_x": float(pixel_scale[0]),
        "pixel_scale_y": float(pixel_scale[1]),
    }


def find_assignment_geotiff_path(assignment: CleaningPlanAssignment) -> Path | None:
    geotiff_dirs = [
        Path(__file__).resolve().parents[3] / "frontend" / "mapping" / "backrounds" / "georeference",
    ]
    candidates = build_assignment_background_name_candidates(assignment)
    for directory in geotiff_dirs:
        if not directory.exists():
            continue
        for candidate in candidates:
            for suffix in (".tif", ".tiff"):
                plain_path = directory / f"{candidate}{suffix}"
                if plain_path.exists():
                    return plain_path
                approx_path = directory / f"{candidate}_codex_approx{suffix}"
                if approx_path.exists():
                    return approx_path
                exact_path = directory / f"{candidate}_georeference{suffix}"
                if exact_path.exists():
                    return exact_path
    return None


def build_assignment_background_name_candidates(assignment: CleaningPlanAssignment) -> list[str]:
    area_name = str(assignment.area_name or "").strip().upper()
    area_code = str(assignment.area_code or "").strip()
    candidates: list[str] = []
    if area_name.startswith("Δ"):
        candidates.append(f"D{area_name[1:]}")
    candidates.extend([area_name.replace(" ", "_"), area_code, f"D{area_code}" if area_code.isdigit() else area_code])
    aliases = {
        "ΧΑΡΑΥΓΗ": "Xaraugi",
        "ΑΓ. ΑΝΤΩΝΙΟΣ": "Agios_Antonios",
        "ΑΓ. ΓΙΩΡΓΗΣ": "Ag_Giorgis",
        "ΑΓ. ΜΗΝΑΣ": "Ag_Minas",
        "ΑΝΑΛΗΨΗ": "Analipsi",
        "ΑΣΤΡΟ ΑΜΦΙΑΛΗΣ": "Astro_Amfialis",
        "ΕΥΓΕΝΕΙΑ": "Eugenia",
        "ΚΟΚΚΙΝΟΒΡΑΧΟΣ": "Kokkinovrahos",
        "ΠΑΝ. ΒΛΑΧΕΡΝΩΝ": "Pan_vlaxernwn",
        "ΤΑΜΠΟΥΡΙΑ": "Tampouria",
    }
    if area_name in aliases:
        candidates.append(aliases[area_name])
    deduped: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in deduped:
            deduped.append(candidate)
    return deduped


def point_is_near_canvas(point: tuple[float, float], width: int, height: int) -> bool:
    x, y = point
    margin = 80
    return -margin <= x <= width + margin and -margin <= y <= height + margin


def draw_road_labels(
    draw: ImageDraw.ImageDraw,
    road_features: list[dict],
    project,
    width: int,
    height: int,
) -> None:
    font = load_pillow_font(16)
    used_boxes: list[tuple[float, float, float, float]] = []
    labeled_names: set[str] = set()
    label_candidates: list[tuple[float, dict, list[tuple[float, float]]]] = []
    for feature in road_features:
        name = str((feature.get("properties") or {}).get("name") or (feature.get("properties") or {}).get("road_name") or "").strip()
        if not name or name in labeled_names:
            continue
        road_points = [project(point) for point in simplify_points(collect_lng_lat_coordinates(feature), 12)]
        road_points = [point for point in road_points if point_is_near_canvas(point, width, height)]
        if len(road_points) < 2:
            continue
        length = polyline_screen_length(road_points)
        if length < 70:
            continue
        label_candidates.append((length, feature, road_points))

    for _length, feature, road_points in sorted(label_candidates, key=lambda item: item[0], reverse=True):
        name = str((feature.get("properties") or {}).get("name") or (feature.get("properties") or {}).get("road_name") or "").strip()
        if name in labeled_names:
            continue
        label_point = road_points[len(road_points) // 2]
        text = name[:24]
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = label_point[0] - text_width / 2
        y = label_point[1] - text_height - 9
        label_box = (x - 6, y - 4, x + text_width + 6, y + text_height + 5)
        if x < 8 or y < 8 or x + text_width > width - 8 or y + text_height > height - 8:
            continue
        if any(boxes_overlap(label_box, used_box) for used_box in used_boxes):
            continue
        draw.rounded_rectangle(label_box, radius=5, fill="#ffffffe6", outline="#9aa0a6", width=1)
        draw.text((x, y), text, fill="#174c35", font=font)
        used_boxes.append(label_box)
        labeled_names.add(name)
        if len(used_boxes) >= 10:
            break


def polyline_screen_length(points: list[tuple[float, float]]) -> float:
    return sum(
        ((points[index][0] - points[index - 1][0]) ** 2 + (points[index][1] - points[index - 1][1]) ** 2) ** 0.5
        for index in range(1, len(points))
    )


def boxes_overlap(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> bool:
    return not (first[2] < second[0] or second[2] < first[0] or first[3] < second[1] or second[3] < first[1])


def get_assignment_map_features(assignment: CleaningPlanAssignment) -> tuple[dict | None, list[dict]]:
    roads_layer = load_geojson_context("line_roads.geojson")
    areas_layer = load_geojson_context("urban_units.geojson")
    feature_by_code = {
        get_feature_road_code(feature, index): feature
        for index, feature in enumerate(roads_layer.get("features", []))
    }
    road_features = [
        feature_by_code.get(str(road.segment_code))
        for road in sorted(assignment.road_segments, key=lambda road: (road.planned_order is None, road.planned_order or 0, road.id))
    ]
    road_features = [feature for feature in road_features if feature]

    area_feature = find_assignment_area_feature(areas_layer.get("features", []), assignment)
    return area_feature, road_features


def find_assignment_area_feature(features: list[dict], assignment: CleaningPlanAssignment) -> dict | None:
    assignment_name = normalize_area_value(assignment.area_name)
    assignment_code = normalize_area_value(assignment.area_code)
    name_match = next(
        (
            feature
            for feature in features
            if assignment_name and assignment_name in get_feature_area_values(feature)
        ),
        None,
    )
    if name_match:
        return name_match
    return next(
        (
            feature
            for feature in features
            if assignment_code and assignment_code in get_feature_area_values(feature)
        ),
        None,
    )


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int, padding: int) -> None:
    for index in range(8):
        x = padding + index * ((width - padding * 2) / 7)
        draw.line([(x, padding), (x, height - padding)], fill="#e8edf4", width=1)
    for index in range(5):
        y = padding + index * ((height - padding * 2) / 4)
        draw.line([(padding, y), (width - padding, y)], fill="#e8edf4", width=1)


def draw_base_road_network(draw: ImageDraw.ImageDraw, project, bounds: tuple[float, float, float, float]) -> None:
    roads_layer = load_geojson_context("line_roads.geojson")
    expanded_bounds = expand_bounds(bounds, 0.22)
    for feature in roads_layer.get("features", []):
        points = collect_lng_lat_coordinates(feature)
        if len(points) < 2 or not points_intersect_bounds(points, expanded_bounds):
            continue
        projected_points = [project(point) for point in simplify_points(points, 16)]
        if len(projected_points) < 2:
            continue
        draw.line(projected_points, fill="#d0dae7", width=5, joint="curve")
        draw.line(projected_points, fill="#ffffff", width=2, joint="curve")


def expand_bounds(bounds: tuple[float, float, float, float], ratio: float) -> tuple[float, float, float, float]:
    min_lng, min_lat, max_lng, max_lat = bounds
    lng_padding = (max_lng - min_lng) * ratio
    lat_padding = (max_lat - min_lat) * ratio
    return (
        min_lng - lng_padding,
        min_lat - lat_padding,
        max_lng + lng_padding,
        max_lat + lat_padding,
    )


def points_intersect_bounds(points: list[list[float]], bounds: tuple[float, float, float, float]) -> bool:
    min_lng, min_lat, max_lng, max_lat = bounds
    return any(min_lng <= lng <= max_lng and min_lat <= lat <= max_lat for lng, lat in points)


def draw_map_legend(draw: ImageDraw.ImageDraw, width: int, height: int, include_base: bool = True) -> None:
    font = load_pillow_font(24)
    box_x = 34
    box_height = 94 if include_base else 72
    box_y = height - box_height - 34
    draw.rounded_rectangle([box_x, box_y, box_x + 420, box_y + box_height], radius=16, fill="#ffffff", outline="#cbd5e1", width=2)
    draw.rectangle([box_x + 24, box_y + 19, box_x + 70, box_y + 42], fill="#fbbc0433", outline="#fbbc04", width=3)
    draw.text((box_x + 84, box_y + 17), "Περιοχή ανάθεσης", fill="#1f2937", font=font)
    draw.line([(box_x + 24, box_y + 56), (box_x + 70, box_y + 56)], fill="#137333", width=5)
    draw.text((box_x + 84, box_y + 45), "Ανατεθειμένοι δρόμοι", fill="#1f2937", font=font)
    if include_base:
        draw.line([(box_x + 24, box_y + 78), (box_x + 70, box_y + 78)], fill="#d0dae7", width=5)
        draw.text((box_x + 84, box_y + 67), "Υπόβαθρο οδικού δικτύου", fill="#1f2937", font=font)


def load_pillow_font(size: int):
    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    font_path = next((path for path in candidates if path.exists()), None)
    if font_path:
        return ImageFont.truetype(str(font_path), size)
    return ImageFont.load_default()


def load_geojson_context(filename: str) -> dict:
    path = Path(__file__).resolve().parents[3] / "frontend" / "mapping" / "data" / "context" / filename
    if not path.exists():
        return {"type": "FeatureCollection", "features": []}
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def get_feature_road_code(feature: dict, index: int) -> str:
    properties = feature.get("properties") or {}
    return str(
        properties.get("segment_code")
        or properties.get("osm_id")
        or properties.get("code")
        or properties.get("id")
        or f"road-{index + 1}"
    )


def get_feature_area_code(feature: dict) -> str:
    properties = feature.get("properties") or {}
    return str(
        properties.get("area_code")
        or properties.get("code")
        or properties.get("id")
        or properties.get("name")
        or ""
    )


def get_feature_area_values(feature: dict) -> set[str]:
    properties = feature.get("properties") or {}
    values = {
        properties.get("area_code"),
        properties.get("code"),
        properties.get("id"),
        properties.get("gid"),
        properties.get("name"),
        properties.get("onoma"),
        properties.get("perigrafi"),
    }
    normalized = {normalize_area_value(value) for value in values}
    return {value for value in normalized if value}


def normalize_area_value(value) -> str:
    text = str(value or "").strip().upper()
    if not text:
        return ""
    return " ".join(text.replace("_", " ").split())


def collect_lng_lat_coordinates(feature: dict) -> list[list[float]]:
    coordinates: list[list[float]] = []

    def walk(value):
        if not isinstance(value, list):
            return
        if len(value) >= 2 and isinstance(value[0], (int, float)) and isinstance(value[1], (int, float)):
            coordinates.append([float(value[0]), float(value[1])])
            return
        for entry in value:
            walk(entry)

    walk((feature.get("geometry") or {}).get("coordinates"))
    return coordinates


def simplify_points(points: list[list[float]], max_points: int) -> list[list[float]]:
    if len(points) <= max_points:
        return points
    if max_points <= 2:
        return [points[0], points[-1]]
    step = (len(points) - 1) / (max_points - 1)
    return [points[round(index * step)] for index in range(max_points)]


def build_notes_block(assignment: CleaningPlanAssignment, styles: dict[str, ParagraphStyle]) -> Table | None:
    notes = clean_print_notes(assignment.notes)
    if not notes:
        return None
    data = [
        [Paragraph("Παρατηρήσεις", styles["Strong"])],
        [Paragraph(notes, styles["Normal"])],
    ]
    table = Table(data, colWidths=[169 * mm])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f7")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def clean_print_notes(notes: str | None) -> str:
    if not notes:
        return ""
    hidden_keys = (
        "target_type",
        "priority",
        "mode",
        "carry_over",
        "carryover",
        "source_assignment",
        "assignment_id",
    )
    visible_parts: list[str] = []
    for part in notes.replace("\n", ";").split(";"):
        value = part.strip()
        normalized = value.lower()
        if not value:
            continue
        if "=" in value and any(key in normalized for key in hidden_keys):
            continue
        visible_parts.append(value)
    return "; ".join(visible_parts)


def default_table_style(header: bool = False) -> TableStyle:
    commands = [
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d8dee9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172033")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ])
    return TableStyle(commands)


def format_date(value: date) -> str:
    return value.strftime("%d/%m/%Y")


def format_duration(minutes: int | None) -> str:
    if not minutes:
        return "-"
    if minutes < 60:
        return f"{minutes} λ."
    hours, rest = divmod(minutes, 60)
    return f"{hours} ω. {rest} λ." if rest else f"{hours} ω."


def format_km(value: Decimal | None) -> str:
    if value is None:
        return "-"
    return f"{float(value):.2f} km"


def priority_label(priority: int | None) -> str:
    labels = {
        0: "Άμεση",
        1: "Υψηλή",
        2: "Κανονική",
        3: "Χαμηλή",
    }
    return labels.get(priority if priority is not None else 2, "Κανονική")


def status_label(status: str | None) -> str:
    labels = {
        "draft": "Πρόχειρη",
        "assigned": "Σε πλάνο",
        "in_progress": "Σε εξέλιξη",
        "completed": "Ολοκληρωμένη",
        "partially_completed": "Μερικώς ολοκληρωμένη",
        "incomplete": "Μη ολοκληρωμένη",
        "pending": "Εκκρεμής",
        "overdue": "Εκπρόθεσμη",
        "failed": "Απέτυχε",
    }
    return labels.get(str(status or ""), str(status or "-"))
