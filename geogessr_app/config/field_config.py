# config/field_config.py

# 表示用の観点（画像 + ラベル）
field_options = {
    "Flag (image only)": ("flag.image_url", "#country"),
    "Flag": ("flag.image_url", "flag.description"),
    "Language (text only)": ("#noimage", "language"),
    "Street Terms (text only)": ("#noimage", "#dynamic_street_terms"),
    "Top-level Domain (text only)": ("#noimage", "tld"),
    "GDP per capita (text only)": ("#noimage", "gdp_per_capita"),
    "Number Plate (text only)": ("#noimage", "number_plate"),
    "Crosswalk Stripes (text only)": ("#noimage", "crosswalk_stripes"),
    "Crosswalk Features (text only)": ("#noimage", "crosswalk_features"),
    "Sign Back (text only)": ("#noimage", "sign_back"),
    "Camera (text only)": ("#noimage", "camera"),
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
