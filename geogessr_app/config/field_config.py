# config/field_config.py

# 表示用の観点（画像 + ラベル）
field_options = {
    "Flag": ("flag.image_url", "flag.description"),
    "Language (text only)": ("#noimage", "language"),
    "Top-level Domain (text only)": ("#noimage", "tld"),
    "Landmark": ("landmark.image_url", "landmark.name"),
}

# フィルター対象の定義（型・説明）
FILTERABLE_FIELDS = {
    "language": ("list", "Languages spoken"),
    "tld": ("string", "Top-level domain"),
    "flag.description": ("string", "Flag description"),
    "landmark.name": ("string", "Landmark name"),
}
