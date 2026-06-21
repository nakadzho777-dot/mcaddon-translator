from app.views.preview_view import PreviewView
from app.views.history_view import HistoryView
from app.views.dictionary_view import DictionaryView
from app.views.settings_view import SettingsView
from app.views.stats_view import StatsView
from app.views.checker_view import CheckerView
from app.views.diagnostics_view import DiagnosticsView
from app.views.review_view import ReviewView
from app.views.json_repair_view import JsonRepairView
from app.views.translation_rate_view import TranslationRateView
from app.views.quality_view import QualityView
from app.views.cloud_dictionary_view import CloudDictionaryView
from app.views.translation_report_view import TranslationReportView
from app.views.quality_score_view import QualityScoreView
from app.views.update_view import UpdateView


class ProFeatureController:
    """
    Pro版の追加機能をまとめて管理するクラス。
    gui_pro.py を巨大化させないため、各Viewの生成とopen処理をここに集約します。
    """

    def __init__(
        self,
        root,
        translator,
        processor,
        on_log=None,
        on_stats_update=None,
        style_prefix="Launcher"
    ):
        self.root = root
        self.translator = translator
        self.processor = processor
        self.on_log = on_log
        self.on_stats_update = on_stats_update
        self.style_prefix = style_prefix

        self.preview_view = PreviewView(
            root,
            translator,
            on_log=on_log,
            on_stats_update=on_stats_update,
            style_prefix=style_prefix
        )

        self.history_view = HistoryView(
            root,
            translator,
            preview_view=self.preview_view,
            on_log=on_log,
            on_stats_update=on_stats_update,
            style_prefix=style_prefix
        )

        self.dictionary_view = DictionaryView(
            root,
            translator,
            on_log=on_log,
            on_stats_update=on_stats_update,
            style_prefix=style_prefix
        )

        self.settings_view = SettingsView(
            root,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.stats_view = StatsView(
            root,
            translator,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.checker_view = CheckerView(
            root,
            processor=processor,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.diagnostics_view = DiagnosticsView(
            root,
            processor=processor,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.review_view = ReviewView(
            root,
            translator,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.json_repair_view = JsonRepairView(
            root,
            processor=processor,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.translation_rate_view = TranslationRateView(
            root,
            processor=processor,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.quality_view = QualityView(
            root,
            processor=processor,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.cloud_dictionary_view = CloudDictionaryView(
            root,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.translation_report_view = TranslationReportView(
            root,
            translator=translator,
            processor=processor,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.quality_score_view = QualityScoreView(
            root,
            processor=processor,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.update_view = UpdateView(
            root,
            on_log=on_log,
            style_prefix=style_prefix
        )

    def latest_history(self):
        try:
            history = self.translator.get_history()
            if not history:
                return None
            return history[-1]
        except Exception:
            return None

    def preview_window(self):
        self.preview_view.open(self.latest_history())

    def translation_history(self):
        self.history_view.open()

    def dictionary_editor(self):
        self.dictionary_view.open()

    def translation_checker(self):
        self.checker_view.open()

    def addon_diagnostics(self):
        self.diagnostics_view.open()

    def ai_review(self):
        self.review_view.open()

    def json_repair(self):
        self.json_repair_view.open()

    def translation_rate(self):
        self.translation_rate_view.open()

    def quality_check(self):
        self.quality_view.open()

    def cloud_dictionary(self):
        self.cloud_dictionary_view.open()

    def translation_report(self):
        self.translation_report_view.open()

    def quality_score(self):
        self.quality_score_view.open()

    def update_check(self):
        self.update_view.open()

    def settings(self):
        self.settings_view.open()

    def stats(self):
        self.stats_view.open()
