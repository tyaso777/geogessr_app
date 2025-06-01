# config/street_config.py

# 言語別の道路表記辞書
LANGUAGE_STREET_TERMS = {
    "English": {
        "street": [
            "Street",
            "Road",
            "Avenue",
            "Lane",
            "Drive",
            "Way",
            "Place",
            "Court",
        ],
        "abbreviations": ["St", "Rd", "Ave", "Ln", "Dr", "Way", "Pl", "Ct"],
    },
    "French": {
        "street": ["Rue", "Avenue", "Boulevard", "Place", "Chemin", "Route", "Impasse"],
        "abbreviations": ["R.", "Ave", "Bd", "Pl", "Ch.", "Rte", "Imp."],
    },
    "Spanish": {
        "street": ["Calle", "Avenida", "Plaza", "Carrera", "Paseo", "Camino"],
        "abbreviations": ["C/", "Av.", "Pza.", "Cra.", "P°", "Cam."],
    },
    "Portuguese": {
        "street": ["Rua", "Avenida", "Praça", "Largo", "Travessa", "Estrada"],
        "abbreviations": ["R.", "Av.", "Pça.", "Lgo.", "Tv.", "Est."],
    },
    "Italian": {
        "street": ["Via", "Strada", "Piazza", "Corso", "Viale", "Largo"],
        "abbreviations": ["V.", "Str.", "P.za", "C.so", "V.le", "Lgo."],
    },
    "German": {
        "street": ["Straße", "Gasse", "Platz", "Weg", "Allee", "Ring"],
        "abbreviations": ["Str.", "G.", "Pl.", "Weg", "All.", "Ring"],
    },
    "Dutch": {
        "street": ["Straat", "Laan", "Plein", "Weg", "Gracht", "Kade"],
        "abbreviations": ["Str.", "Ln.", "Pl.", "Weg", "Gr.", "Kade"],
    },
    "Polish": {
        "street": ["Ulica", "Aleja", "Plac", "Droga", "Osiedle"],
        "abbreviations": ["ul.", "al.", "pl.", "dr.", "os."],
    },
    "Czech": {
        "street": ["Ulice", "Náměstí", "Třída", "Cesta", "Nábřeží"],
        "abbreviations": ["ul.", "nám.", "tř.", "cesta", "nábř."],
    },
    "Hungarian": {
        "street": ["Utca", "Út", "Tér", "Körút", "Sétány"],
        "abbreviations": ["u.", "út", "tér", "krt.", "sét."],
    },
    "Croatian": {
        "street": ["Ulica", "Cesta", "Trg", "Avenija", "Put"],
        "abbreviations": ["ul.", "c.", "trg", "av.", "put"],
    },
    "Romanian": {
        "street": ["Strada", "Bulevardul", "Piața", "Calea", "Aleea"],
        "abbreviations": ["Str.", "Bd.", "Pța.", "Cal.", "Al."],
    },
    "Russian": {
        "street": ["Улица", "Проспект", "Площадь", "Переулок", "Бульвар"],
        "abbreviations": ["ул.", "пр-т", "пл.", "пер.", "б-р"],
    },
    "Ukrainian": {
        "street": ["Вулиця", "Проспект", "Площа", "Провулок", "Бульвар"],
        "abbreviations": ["вул.", "просп.", "пл.", "пров.", "бульв."],
    },
    "Bulgarian": {
        "street": ["Улица", "Булевард", "Площад", "Път"],
        "abbreviations": ["ул.", "бул.", "пл.", "път"],
    },
    "Greek": {
        "street": ["Οδός", "Λεωφόρος", "Πλατεία", "Δρόμος"],
        "abbreviations": ["Οδ.", "Λεωφ.", "Πλ.", "Δρ."],
    },
    "Turkish": {
        "street": ["Sokak", "Cadde", "Bulvar", "Meydan", "Yol"],
        "abbreviations": ["Sk.", "Cd.", "Blv.", "Myd.", "Yolu"],
    },
    "Swedish": {
        "street": ["Gata", "Väg", "Torg", "Gränd", "Allé"],
        "abbreviations": ["g.", "väg", "torg", "gr.", "allé"],
    },
    "Norwegian": {
        "street": ["Gate", "Vei", "Plass", "Torg", "Allé"],
        "abbreviations": ["gt.", "vei", "pl.", "torg", "allé"],
    },
    "Danish": {
        "street": ["Gade", "Vej", "Plads", "Torv", "Allé"],
        "abbreviations": ["gade", "vej", "pl.", "torv", "allé"],
    },
    "Finnish": {
        "street": ["Katu", "Tie", "Tori", "Kuja", "Puistotie"],
        "abbreviations": ["k.", "tie", "tori", "kj.", "pt."],
    },
    "Icelandic": {
        "street": ["Gata", "Vegur", "Torg", "Stræti"],
        "abbreviations": ["g.", "veg.", "torg", "str."],
    },
    "Estonian": {
        "street": ["Tänav", "Tee", "Väljak", "Puiestee"],
        "abbreviations": ["tn", "tee", "välj.", "pst"],
    },
    "Latvian": {
        "street": ["Iela", "Ceļš", "Laukums", "Bulvāris"],
        "abbreviations": ["iela", "ceļš", "laukums", "bulv."],
    },
    "Lithuanian": {
        "street": ["Gatvė", "Kelias", "Aikštė", "Bulvaras"],
        "abbreviations": ["g.", "kel.", "a.", "bulv."],
    },
    "Slovenian": {
        "street": ["Ulica", "Cesta", "Trg", "Pot"],
        "abbreviations": ["ul.", "c.", "trg", "pot"],
    },
    "Slovak": {
        "street": ["Ulica", "Cesta", "Námestie", "Trieda"],
        "abbreviations": ["ul.", "c.", "nám.", "tr."],
    },
    "Serbian": {
        "street": ["Улица", "Булевар", "Трг", "Пут"],
        "abbreviations": ["ул.", "бул.", "трг", "пут"],
    },
    "Albanian": {
        "street": ["Rruga", "Bulevardi", "Sheshi", "Lagjja"],
        "abbreviations": ["Rr.", "Blv.", "Sh.", "Lagj."],
    },
    "Macedonian": {
        "street": ["Улица", "Булевар", "Плоштад"],
        "abbreviations": ["ул.", "бул.", "пл."],
    },
    "Montenegrin": {
        "street": ["Улица", "Булевар", "Трг"],
        "abbreviations": ["ул.", "бул.", "трг"],
    },
    "Arabic": {
        "street": ["شارع", "طريق", "ميدان", "زقاق"],
        "abbreviations": ["ش.", "ط.", "م.", "ز."],
    },
    "Hebrew": {
        "street": ["רחוב", "שדרות", "כיכר", "מעלה"],
        "abbreviations": ["רח'", "שד'", "כיכר", "מעלה"],
    },
    "Japanese": {
        "street": ["通り", "街道", "大通り", "小路"],
        "abbreviations": ["通", "街道", "大通", "小路"],
    },
    "Korean": {
        "street": ["길", "대로", "로", "거리"],
        "abbreviations": ["길", "대로", "로", "거리"],
    },
    "Chinese": {
        "street": ["路", "街", "大道", "巷"],
        "abbreviations": ["路", "街", "大道", "巷"],
    },
    "Hindi": {
        "street": ["सड़क", "मार्ग", "गली", "चौक"],
        "abbreviations": ["सड़क", "मार्ग", "गली", "चौक"],
    },
    "Bengali": {
        "street": ["রাস্তা", "সড়ক", "পথ", "গলি"],
        "abbreviations": ["রাস্তা", "সড়ক", "পথ", "গলি"],
    },
    "Vietnamese": {
        "street": ["Đường", "Phố", "Quảng trường", "Hẻm"],
        "abbreviations": ["Đ.", "P.", "QT.", "Hẻm"],
    },
    "Thai": {
        "street": ["ถนน", "ซอย", "ตรอก", "ย่าน"],
        "abbreviations": ["ถ.", "ซ.", "ตรอก", "ย่าน"],
    },
    "Indonesian": {
        "street": ["Jalan", "Gang", "Lorong", "Komplek"],
        "abbreviations": ["Jl.", "Gg.", "Lr.", "Komp."],
    },
    "Malay": {
        "street": ["Jalan", "Lorong", "Lebuh", "Persiaran"],
        "abbreviations": ["Jln", "Lg", "Lbh", "Psrn"],
    },
    "Urdu": {
        "street": ["سڑک", "راہ", "گلی", "چوک"],
        "abbreviations": ["سڑک", "راہ", "گلی", "چوک"],
    },
}


def get_street_terms_for_languages(languages: list[str]) -> dict:
    """指定された言語リストに対応する道路表記を取得"""
    result = {}
    for lang in languages:
        if lang in LANGUAGE_STREET_TERMS:
            result[lang] = LANGUAGE_STREET_TERMS[lang]
    return result


def format_street_display(street_terms: dict) -> str:
    """道路表記を表示用にフォーマット"""
    if not street_terms:
        return "No street terms available"

    display_parts = []
    for lang, terms in street_terms.items():
        streets = ", ".join(terms["street"][:3])  # 最初の3つを表示
        abbrevs = ", ".join(terms["abbreviations"][:3])  # 最初の3つを表示
        display_parts.append(f"{lang}: {streets} ({abbrevs})")

    return " | ".join(display_parts)
