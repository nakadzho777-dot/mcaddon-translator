from app.views.pro_upgrade_view import ProUpgradeView
from app.views.translation_rate_view import TranslationRateView
from app.views.update_view import UpdateView


class FreeFeatureController:
    """
    Free版の追加機能をまとめて管理するクラス。
    """

    def __init__(
        self,
        root,
        translator,
        processor,
        on_log=None,
        style_prefix="Free"
    ):
        self.root = root
        self.translator = translator
        self.processor = processor
        self.on_log = on_log
        self.style_prefix = style_prefix

        self.pro_upgrade_view = ProUpgradeView(
            root,
            on_log=on_log,
            style_prefix=style_prefix
        )

        self.translation_rate_view = TranslationRateView(
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

    def locked_feature(self, feature_name):
        self.pro_upgrade_view.open(feature_name)

    def translation_rate(self):
        self.translation_rate_view.open()

    def update_check(self):
        self.update_view.open()
