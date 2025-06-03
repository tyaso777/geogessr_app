# config/data_processor.py

from config.number_plate_config import (
    get_combined_plate_data_url,
    has_number_plate_config,
)
from config.street_config import format_street_display, get_street_terms_for_languages


class DataProcessor:
    """データの動的処理を担当するクラス"""

    @staticmethod
    def process_field(field_path: str, country_info: dict):
        """フィールドパスに基づいてデータを動的に処理"""

        # 静的フィールドの場合はそのまま返す
        if not field_path.startswith("#dynamic_") and not field_path.startswith("#"):
            return DataProcessor._get_nested_value(country_info, field_path)

        # 動的フィールドの処理
        if field_path == "#dynamic_street_terms":
            languages = country_info.get("language", [])
            street_terms = get_street_terms_for_languages(languages)
            return format_street_display(street_terms)

        elif field_path == "#number_plate_visual":
            # ナンバープレート画像が利用可能かチェック
            return "Available" if country_info.get("number_plate_config") else None

        elif field_path == "#geoguessr_tips":
            # GeoGuessrのTipsが利用可能かチェック（short版またはlong版）
            tips = country_info.get("geoguessr_tips", {})
            return "Available" if (tips.get("short") or tips.get("long")) else None

        # 他の動的フィールドもここで処理可能
        # elif field_path == "#dynamic_currency":
        #     return DataProcessor._get_currency_info(country_info)

        return None

    @staticmethod
    def create_special_html(
        country: str,
        info: dict,
        field_path: str,
        show_flag: bool,
        show_country_name: bool,
        bg_color: str = "white",
    ) -> str:
        """特別な表示が必要なフィールドのHTMLを生成"""

        if field_path == "#number_plate_visual":
            return DataProcessor._create_number_plate_html(
                country, info, show_flag, show_country_name, bg_color
            )

        elif field_path == "#geoguessr_tips":
            return DataProcessor._create_tips_html(
                country, info, show_flag, show_country_name, bg_color
            )

        # 他の特別フィールドもここで処理
        # elif field_path == "#dynamic_currency_visual":
        #     return DataProcessor._create_currency_html(...)

        return None

    @staticmethod
    def _create_number_plate_html(
        country: str,
        info: dict,
        show_flag: bool,
        show_country_name: bool,
        bg_color: str,
    ) -> str:
        """ナンバープレート表示用HTMLを生成"""
        if not has_number_plate_config(info):
            return None

        # 国名を引数として渡す
        plate_data_url = get_combined_plate_data_url(info, country)

        # フラグと国名の表示
        flag_html = ""
        if show_flag:
            flag_url = info.get("flag", {}).get("image_url", "")
            if flag_url:
                flag_html = f'<img src="{flag_url}" style="width: 30px; height: auto; display: block; margin: 0 auto 5px auto;" />'

        country_text = ""
        if show_country_name:
            country_text = f'<div style="font-size: 10px; margin-bottom: 5px; color: #000;">{country}</div>'

        html = f"""
        <div style="text-align: center; font-size: 10px;">
            {flag_html}
            {country_text}
            <img src="{plate_data_url}" style="width: 120px; height: auto; display: block; margin: 0 auto;" />
        </div>
        """
        return html

    @staticmethod
    def _create_tips_html(
        country: str,
        info: dict,
        show_flag: bool,
        show_country_name: bool,
        bg_color: str,
    ) -> str:
        """GeoGuessrのTips表示用HTMLを生成"""
        tips_data = info.get("geoguessr_tips", {})
        tips = tips_data.get("short", [])
        if not tips:
            return None

        # フラグと国名の表示
        flag_html = ""
        if show_flag:
            flag_url = info.get("flag", {}).get("image_url", "")
            if flag_url:
                flag_html = f'<img src="{flag_url}" style="width: 25px; height: auto; display: block; margin: 0 auto 3px auto;" />'

        country_text = ""
        if show_country_name:
            country_text = f'<div style="font-size: 9px; margin-bottom: 3px; color: #000; font-weight: bold;">{country}</div>'

        # Tips内容を動的に構築（コンパクト版）
        tips_content = ""
        for i, tip in enumerate(tips):
            if tip.get("type") == "text":
                # テキストを短縮して表示
                text = tip["content"]
                if len(text) > 25:  # 25文字以上は省略
                    text = text[:22] + "..."
                tips_content += f'<div style="margin: 2px 0; font-size: 8px; line-height: 1.2; color: #333;">{text}</div>'
            elif tip.get("type") == "image":
                image_path = tip.get("path", "")
                caption = tip.get("caption", "")

                # 画像パスの処理
                if image_path.startswith("data:"):
                    image_src = image_path
                elif image_path.startswith("http"):
                    image_src = image_path
                else:
                    image_src = f"assets/tips/{image_path}"

                # 画像サイズを大幅に縮小
                tips_content += f"""
                <div style="margin: 3px 0; text-align: center;">
                    <img src="{image_src}" style="width: 30%; max-width: 30px; height: auto; display: block; margin: 0 auto;" />
                    {f'<div style="font-size: 7px; text-align: center; color: #666; margin-top: 1px; line-height: 1.1;">{caption[:20]}{"..." if len(caption) > 20 else ""}</div>' if caption else ""}
                </div>
                """

        html = f"""
        <div style="text-align: center; font-size: 10px; background: {bg_color}; padding: 4px; border-radius: 4px; border: 1px solid #666; max-width: 120px;">
            {flag_html}
            {country_text}
            <div style="text-align: left; max-width: 110px;">
                {tips_content}
            </div>
        </div>
        """
        return html

    @staticmethod
    def is_special_field(field_path: str) -> bool:
        """特別な表示処理が必要なフィールドかどうか"""
        special_fields = {
            "#number_plate_visual",
            "#geoguessr_tips",
            # 他の特別フィールドもここに追加
        }
        return field_path in special_fields

    @staticmethod
    def _get_nested_value(obj: dict, dotted_key: str):
        """ネストされたキーの値を取得"""
        try:
            if not isinstance(dotted_key, str):
                return dotted_key
            for key in dotted_key.split("."):
                if isinstance(obj, dict) and key in obj:
                    obj = obj[key]
                else:
                    return None
            return obj
        except Exception:
            return None

    @staticmethod
    def supports_filtering(field_path: str) -> bool:
        """指定されたフィールドがフィルタリング可能かどうか"""
        return (
            field_path.startswith("#dynamic_")
            or "." in field_path
            or field_path in ["language", "tld"]
        )

    @staticmethod
    def filter_matches(
        field_path: str, country_info: dict, match_type: str, filter_value: str
    ) -> bool:
        """フィルタリング条件に一致するかチェック"""
        value = DataProcessor.process_field(field_path, country_info)

        if value is None:
            return False

        if isinstance(value, list):
            if match_type == "contains":
                return any(filter_value.lower() in str(v).lower() for v in value)
            elif match_type == "equals":
                return filter_value.lower() in [str(v).lower() for v in value]
        else:
            value_str = str(value).lower()
            filter_str = filter_value.lower()

            if match_type == "contains":
                return filter_str in value_str
            elif match_type == "equals":
                return filter_str == value_str

        return False
