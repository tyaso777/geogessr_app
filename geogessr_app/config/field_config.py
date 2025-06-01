# config/field_config.py

# 表示用の観点（画像 + ラベル）
field_options = {
    "Flag (image only)": ("flag.image_url", "#country"),
    "Flag": ("flag.image_url", "flag.description"),
    "Language (text only)": ("#noimage", "language"),
    "Top-level Domain (text only)": ("#noimage", "tld"),
}


# フィルター対象の定義（型・説明）
FILTERABLE_FIELDS = {
    "language": ("list", "Languages spoken"),
    "tld": ("string", "Top-level domain"),
    "flag.description": ("string", "Flag description"),
}

CHAR_TO_LANGUAGES = {
    # 北欧・西ヨーロッパ
    "å": ["Swedish", "Norwegian", "Danish"],
    "ø": ["Norwegian", "Danish"],
    "æ": ["Norwegian", "Danish", "Icelandic"],
    "ä": ["Swedish", "German", "Finnish", "Estonian"],
    "ö": ["German", "Swedish", "Finnish", "Turkish", "Estonian"],
    "ü": ["German", "Turkish", "Azerbaijani", "Estonian"],
    "ß": ["German"],
    # 南ヨーロッパ・ロマンス語系
    "é": ["French", "Portuguese", "Spanish"],
    "è": ["French", "Italian"],
    "ê": ["French"],
    "ç": ["French", "Portuguese", "Turkish"],
    "á": ["Portuguese", "Spanish", "Hungarian"],
    "í": ["Spanish", "Hungarian"],
    "ñ": ["Spanish"],
    "ó": ["Spanish", "Portuguese", "Hungarian", "Polish"],
    "ú": ["Spanish", "Hungarian", "Portuguese"],
    # 東ヨーロッパ・スラブ語系
    "č": ["Czech", "Slovak", "Slovenian", "Croatian", "Bosnian", "Serbian"],
    "ć": ["Croatian", "Bosnian", "Serbian", "Polish"],
    "ž": [
        "Czech",
        "Slovak",
        "Slovenian",
        "Bosnian",
        "Serbian",
        "Latvian",
        "Lithuanian",
    ],
    "š": [
        "Czech",
        "Slovak",
        "Slovenian",
        "Bosnian",
        "Serbian",
        "Latvian",
        "Lithuanian",
    ],
    "ř": ["Czech"],
    "đ": ["Croatian", "Serbian"],
    # 中東欧・ハンガリーなど
    "ő": ["Hungarian"],
    "ű": ["Hungarian"],
    "ł": ["Polish"],
    "ń": ["Polish"],
    "ą": ["Polish", "Lithuanian"],
    "ę": ["Polish"],
    # バルト語
    "ė": ["Lithuanian"],
    "į": ["Lithuanian"],
    "ų": ["Lithuanian"],
    "ļ": ["Latvian"],
    "ņ": ["Latvian"],
    "ģ": ["Latvian"],
    "ķ": ["Latvian"],
    # トルコ語・アゼルバイジャン語
    "ğ": ["Turkish", "Azerbaijani"],
    "ş": ["Turkish", "Azerbaijani"],
    # キリル文字（ロシア語・ウクライナ語など）
    "ё": ["Russian"],
    "и": ["Russian", "Ukrainian", "Bulgarian"],
    "ї": ["Ukrainian"],
    "є": ["Ukrainian"],
}
