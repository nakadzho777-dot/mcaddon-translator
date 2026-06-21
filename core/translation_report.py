import json
import os
from datetime import datetime


class TranslationReportGenerator:
    """
    翻訳レポート生成クラス。

    translator.stats() と processor 情報をもとに、
    reports/ に JSON と TXT を保存します。
    """

    def __init__(self, translator=None, processor=None):
        self.translator = translator
        self.processor = processor

    def generate(self, elapsed_seconds=None):
        os.makedirs("reports", exist_ok=True)

        now = datetime.now()
        stamp = now.strftime("%Y-%m-%d_%H-%M-%S")

        stats = {}
        if self.translator:
            try:
                stats = self.translator.stats()
            except Exception:
                stats = {}

        output_path = None
        source_path = None

        if self.processor:
            output_path = getattr(self.processor, "output_path", None)
            source_path = (
                getattr(self.processor, "source_path", None)
                or getattr(self.processor, "scan_root", None)
            )

        report = {
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "source_path": source_path,
            "output_path": output_path,
            "elapsed_seconds": elapsed_seconds,
            "stats": {
                "total": stats.get("total", 0),
                "ai": stats.get("ai", 0),
                "cache": stats.get("cache", 0),
                "dictionary": stats.get("dictionary", 0),
                "cloud": stats.get("cloud", 0),
                "error": stats.get("error", 0),
                "retranslate": stats.get("retranslate", 0),
            }
        }

        json_path = os.path.join("reports", f"{stamp}_report.json")
        txt_path = os.path.join("reports", f"{stamp}_report.txt")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(self._to_text(report))

        return {
            "json": json_path,
            "txt": txt_path,
            "report": report
        }

    def _to_text(self, report):
        stats = report.get("stats", {})

        lines = []
        lines.append("MCAddon Translator 翻訳レポート")
        lines.append("=" * 40)
        lines.append(f"作成日時: {report.get('created_at')}")
        lines.append(f"入力: {report.get('source_path')}")
        lines.append(f"出力: {report.get('output_path')}")
        lines.append("")

        elapsed = report.get("elapsed_seconds")
        if elapsed is not None:
            lines.append(f"処理時間: {elapsed:.2f} 秒")
        else:
            lines.append("処理時間: -")

        lines.append("")
        lines.append("[翻訳統計]")
        lines.append(f"総処理数: {stats.get('total', 0)}")
        lines.append(f"AI翻訳: {stats.get('ai', 0)}")
        lines.append(f"キャッシュ: {stats.get('cache', 0)}")
        lines.append(f"辞書ヒット: {stats.get('dictionary', 0)}")
        lines.append(f"クラウド辞書: {stats.get('cloud', 0)}")
        lines.append(f"再翻訳: {stats.get('retranslate', 0)}")
        lines.append(f"エラー: {stats.get('error', 0)}")
        lines.append("")

        total = stats.get("total", 0)
        error = stats.get("error", 0)

        if total:
            success_rate = round(((total - error) / total) * 100, 1)
        else:
            success_rate = 0

        lines.append(f"成功率: {success_rate}%")
        lines.append("")
        lines.append("※ このレポートは翻訳ログに基づく自動生成です。")
        lines.append("※ 翻訳漏れ検出・品質チェック・JSON修復と併用してください。")

        return "\n".join(lines)
