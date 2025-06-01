# config/data_processor.py

from config.street_config import format_street_display, get_street_terms_for_languages


class DataProcessor:
    """データの動的処理を担当するクラス"""

    @staticmethod
    def process_field(field_path: str, country_info: dict):
        """フィールドパスに基づいてデータを動的に処理"""

        # 静的フィールドの場合はそのまま返す
        if not field_path.startswith("#dynamic_"):
            return DataProcessor._get_nested_value(country_info, field_path)

        # 動的フィールドの処理
        if field_path == "#dynamic_street_terms":
            languages = country_info.get("language", [])
            street_terms = get_street_terms_for_languages(languages)
            return format_street_display(street_terms)

        # 他の動的フィールドもここで処理可能
        # elif field_path == "#dynamic_currency":
        #     return DataProcessor._get_currency_info(country_info)

        return None

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
