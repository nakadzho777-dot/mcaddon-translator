# app/menu_config.py
# GUIのメニューをここに集約します。
# 新機能を追加するときは、基本的にこのファイルへ1行追加します。

PRO_MENU = [
    ("翻訳開始", "run", "accent"),
    ("最後の翻訳を開く", "open_last_output", "dark"),
    ("プレビュー", "preview_window", "dark"),
    ("翻訳履歴", "translation_history", "dark"),
    ("辞書編集", "dictionary_editor", "dark"),
    ("翻訳漏れ検出", "translation_checker", "dark"),
    ("アドオン診断", "addon_diagnostics", "dark"),
    ("AIレビュー", "ai_review", "dark"),
    ("品質チェック", "quality_check", "dark"),
    ("品質スコア", "quality_score", "dark"),
    ("JSON修復", "json_repair", "dark"),
    ("翻訳率表示", "translation_rate", "dark"),
    ("クラウド辞書", "cloud_dictionary", "dark"),
    ("翻訳レポート", "translation_report", "dark"),
    ("アップデート確認", "update_check", "dark"),
    ("設定", "settings", "dark"),
    ("統計", "stats", "dark"),
    ("ライセンス", "license_settings", "dark"),
]

FREE_MENU = [
    ("翻訳開始", "run", "accent"),
    ("最後の翻訳を開く", "open_last_output", "dark"),
    ("簡易プレビュー", "preview_limited", "dark"),
    ("アップデート確認", "update_check", "dark"),
    ("翻訳履歴 🔒PRO", "locked:翻訳履歴", "dark"),
    ("辞書編集 🔒PRO", "locked:辞書編集", "dark"),
    ("翻訳漏れ検出 🔒PRO", "locked:翻訳漏れ検出", "dark"),
    ("アドオン診断 🔒PRO", "locked:アドオン診断", "dark"),
    ("AIレビュー 🔒PRO", "locked:AIレビュー", "dark"),
    ("品質チェック 🔒PRO", "locked:品質チェック", "dark"),
    ("品質スコア 🔒PRO", "locked:品質スコア", "dark"),
    ("JSON修復 🔒PRO", "locked:JSON修復", "dark"),
    ("クラウド辞書 🔒PRO", "locked:クラウド辞書", "dark"),
    ("翻訳レポート 🔒PRO", "locked:翻訳レポート", "dark"),
    ("翻訳率表示", "translation_rate", "dark"),
    ("統計 🔒PRO", "locked:統計画面", "dark"),
    ("Pro版を見る", "locked:Pro版機能", "dark"),
    ("使い方", "show_help", "dark"),
]
