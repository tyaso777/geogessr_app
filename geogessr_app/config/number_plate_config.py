# config/number_plate_config.py

import urllib.parse

# デフォルト設定
DEFAULT_WIDTH = 400  # 520から400に変更（約23%縮小）
DEFAULT_ASPECT_RATIO = 1 / 2.3


def create_number_plate_svg(
    country_data: dict, plate_type: str = "front", country_name: str = ""
) -> str:
    """国別ナンバープレートのSVGを生成"""
    plate_config = country_data.get("number_plate_config", {})
    if not plate_config:
        return ""

    config = plate_config.get(plate_type, {})
    if not config:
        return ""

    width = DEFAULT_WIDTH
    aspect_ratio = config.get("aspect_ratio", DEFAULT_ASPECT_RATIO)
    height = int(width * aspect_ratio)

    bg_color = config.get("bg_color", "white")
    text_color = config.get("text_color", "black")
    border_color = config.get("border_color", "gray")
    top_band = config.get("top_band_color")
    left_band = config.get("left_band_color")
    right_band = config.get("right_band_color")

    band_width = int(width * 0.1)
    band_height = int(height / 3)

    top_band_svg = (
        f'<rect x="2" y="2" width="{width - 4}" height="{band_height}" fill="{top_band}" />'
        if top_band
        else ""
    )
    left_band_svg = (
        f'<rect x="2" y="2" width="{band_width}" height="{height - 4}" fill="{left_band}" />'
        if left_band
        else ""
    )
    right_band_svg = (
        f'<rect x="{width - band_width - 2}" y="2" width="{band_width}" height="{height - 4}" fill="{right_band}" />'
        if right_band
        else ""
    )

    # 国名を表示テキストとして使用（なければデフォルト）
    display_text = country_name if country_name else "ABC 123"

    # 文字サイズを動的に調整（国名の長さに応じて）- より大きなサイズに変更
    text_length = len(display_text)
    if text_length <= 6:
        font_size = "64"
    elif text_length <= 10:
        font_size = "52"
    elif text_length <= 15:
        font_size = "40"
    else:
        font_size = "32"

    svg = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="{width - 4}" height="{height - 4}" fill="{bg_color}" stroke="{border_color}" stroke-width="2" rx="6"/>
        {top_band_svg}
        {left_band_svg}
        {right_band_svg}
        <text x="{width // 2}" y="{height // 2 + 5}" text-anchor="middle" fill="{text_color}" font-family="Arial, sans-serif" font-size="{font_size}" font-weight="bold">{display_text}</text>
    </svg>"""
    return svg


def get_number_plate_data_url(
    country_data: dict, plate_type: str = "front", country_name: str = ""
) -> str:
    svg = create_number_plate_svg(country_data, plate_type, country_name)
    if not svg:
        return ""
    return f"data:image/svg+xml,{urllib.parse.quote(svg)}"


def has_number_plate_config(country_data: dict) -> bool:
    """国データにナンバープレート設定があるかチェック"""
    return "number_plate_config" in country_data and bool(
        country_data["number_plate_config"]
    )


def create_combined_plate_svg(country_data: dict, country_name: str = "") -> str:
    """front/rear両方のナンバープレートを並べて表示するSVGを生成"""
    if not has_number_plate_config(country_data):
        return ""

    front_svg = create_number_plate_svg(country_data, "front", country_name)
    rear_svg = create_number_plate_svg(country_data, "rear", country_name)

    plate_config = country_data.get("number_plate_config", {})
    front_width = DEFAULT_WIDTH
    rear_width = DEFAULT_WIDTH
    front_height = int(
        front_width
        * plate_config.get("front", {}).get("aspect_ratio", DEFAULT_ASPECT_RATIO)
    )
    rear_height = int(
        rear_width
        * plate_config.get("rear", {}).get("aspect_ratio", DEFAULT_ASPECT_RATIO)
    )

    front_x = 0
    rear_x = front_width + 10
    total_width = rear_x + rear_width
    height = max(front_height, rear_height)

    def strip_svg(svg: str) -> str:
        return (
            svg.replace('<?xml version="1.0" encoding="UTF-8"?>', "")
            .split("<svg", 1)[-1]
            .split(">", 1)[-1]
            .rsplit("</svg>", 1)[0]
        )

    svg = f"""<svg width="{total_width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <g transform="translate({front_x},0)">
            {strip_svg(front_svg)}
        </g>
        <g transform="translate({rear_x},0)">
            {strip_svg(rear_svg)}
        </g>
    </svg>"""
    return svg


def get_combined_plate_data_url(country_data: dict, country_name: str = "") -> str:
    svg = create_combined_plate_svg(country_data, country_name)
    if not svg:
        return ""
    return f"data:image/svg+xml,{urllib.parse.quote(svg)}"
