# config/field_config.py

# 表示用のフィールド（コンテンツのみ）
field_options = {
    "Top-level Domain": "tld",
    "GeoGuessr Tips": "#geoguessr_tips",
    "Number Plate (Visual; Front, Rear)": "#number_plate_visual",
    "Language": "language",
    "Street Terms": "#dynamic_street_terms",
    "Crosswalk Stripes": "crosswalk_stripes",
    "Crosswalk Features": "crosswalk_features",
    "Sign Back": "sign_back",
    "Camera": "camera",
    "GDP per capita": "gdp_per_capita",
    "Flag Description": "flag.description",
}

# アイコン/プレフィックスのオプション（チェックボックス用）
icon_options = {
    "show_flag": "Show Flag Icon",
    "show_country_name": "Show Country Name",
}

# フィルター対象の定義（型・説明）
FILTERABLE_FIELDS = {
    "language": ("list", "Languages spoken"),
    "#dynamic_street_terms": ("string", "Street terms"),
    "tld": ("string", "Top-level domain"),
    "gdp_per_capita": ("number", "GDP per capita (USD)"),
    "number_plate": ("string", "Number plate description"),
    "flag.description": ("string", "Flag description"),
    "crosswalk_stripes": ("number", "Number of crosswalk stripes"),
    "crosswalk_features": ("string", "Crosswalk features description"),
    "sign_back": ("string", "Sign back description"),
    "camera": ("string", "Camera description"),
}

DISPLAY_OPTIONS = {
    "prepend_country_name": {
        "flag.description": True,
        "language": True,
        "#dynamic_street_terms": True,
        "tld": True,
        "gdp_per_capita": True,
        "number_plate": True,
        "crosswalk_stripes": True,
        "crosswalk_features": True,
        "sign_back": True,
        "frame_color_back": True,
        "camera": True,
    }
}
