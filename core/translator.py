from core.cache import Cache
from core.mc_dictionary import MCDictionary
from core.user_dictionary import UserDictionary
from core.cloud_dictionary import CloudDictionary
from core.ai_engine import AIEngine


class Translator:

    def __init__(self):
        self.cache = Cache()
        self.mc_dict = MCDictionary()
        self.user_dict = UserDictionary()
        self.cloud_dict = CloudDictionary()
        self.ai = AIEngine()

        self.history = []

    def translate(self, text: str):

        result = self.translate_batch_fast([text])

        return result[0] if result else text

    def translate_batch_fast(self, texts):

        if not texts:
            return []

        results = [None] * len(texts)

        ai_targets = []
        ai_indexes = []

        for i, text in enumerate(texts):

            if not text:
                results[i] = ""
                continue

            # ------------------------
            # USER DICTIONARY
            # ------------------------

            user_result = self.user_dict.get(text)

            if user_result:

                results[i] = user_result

                self._add_history(
                    text,
                    user_result,
                    "user_dictionary"
                )

                continue

            # ------------------------
            # CLOUD DICTIONARY
            # ------------------------

            cloud_result = self.cloud_dict.translate(text)

            if cloud_result:

                results[i] = cloud_result

                self._add_history(
                    text,
                    cloud_result,
                    "cloud_dictionary"
                )

                continue

            # ------------------------
            # CACHE
            # ------------------------

            cached = self.cache.get(text)

            if cached and not self._is_bad_result(cached):

                results[i] = cached

                self._add_history(
                    text,
                    cached,
                    "cache"
                )

                continue

            # ------------------------
            # MINECRAFT DICTIONARY
            # ------------------------

            mc_result = self.mc_translate(text)

            if mc_result:

                results[i] = mc_result

                self.cache.set(
                    text,
                    mc_result
                )

                self._add_history(
                    text,
                    mc_result,
                    "minecraft_dictionary"
                )

                continue

            ai_targets.append(text)
            ai_indexes.append(i)

        # AIエンジン再生成
        self.ai = AIEngine()

        chunk_size = 20

        for start in range(
            0,
            len(ai_targets),
            chunk_size
        ):

            chunk = ai_targets[
                start:start + chunk_size
            ]

            chunk_indexes = ai_indexes[
                start:start + chunk_size
            ]

            translated = self.ai.translate_batch(chunk)

            for index, source, result in zip(
                chunk_indexes,
                chunk,
                translated
            ):

                if self._is_bad_result(result):

                    results[index] = source

                    self._add_history(
                        source,
                        result,
                        "error"
                    )

                else:

                    results[index] = result

                    self.cache.set(
                        source,
                        result
                    )

                    # クラウド辞書へ保存
                    self.cloud_dict.add(
                        source,
                        result
                    )

                    self._add_history(
                        source,
                        result,
                        "ai"
                    )

        return [
            r if r is not None else texts[i]
            for i, r in enumerate(results)
        ]

    def mc_translate(self, text: str):

        words = text.split()

        translated = []

        found = False

        for word in words:

            user_word = self.user_dict.get(word)

            if user_word:

                translated.append(user_word)

                found = True

                continue

            mc_word = self.mc_dict.get(word)

            if mc_word:

                translated.append(mc_word)

                found = True

            else:

                translated.append(word)

        return " ".join(translated) if found else None

    def _is_bad_result(self, text):

        if not isinstance(text, str):
            return True

        return (
            text.startswith("[ERROR]")
            or text.startswith("[OFFLINE]")
        )

    def add_user_word(
        self,
        source,
        result
    ):
        return self.user_dict.set(
            source,
            result
        )

    def delete_user_word(
        self,
        source
    ):
        return self.user_dict.delete(source)

    def get_user_dictionary(self):
        return self.user_dict.all()

    def search_user_dictionary(
        self,
        keyword
    ):
        return self.user_dict.search(keyword)

    def _add_history(
        self,
        source,
        result,
        engine
    ):

        self.history.append({
            "source": source,
            "result": result,
            "engine": engine
        })

    def get_history(self):
        return self.history

    def clear_history(self):
        self.history.clear()

    def retranslate(self, text: str):

        result = self.ai.translate(text)

        if not self._is_bad_result(result):

            self.cache.set(
                text,
                result
            )

            self.cloud_dict.add(
                text,
                result
            )

        self._add_history(
            text,
            result,
            "retranslate"
        )

        return result

    def stats(self):

        cache_count = 0
        ai_count = 0
        dict_count = 0
        cloud_count = 0
        error_count = 0
        retranslate_count = 0

        for item in self.history:

            engine = item.get(
                "engine",
                ""
            )

            result = item.get(
                "result",
                ""
            )

            if (
                self._is_bad_result(result)
                or engine == "error"
            ):
                error_count += 1

            if engine == "cache":
                cache_count += 1

            elif engine == "ai":
                ai_count += 1

            elif engine == "cloud_dictionary":
                cloud_count += 1

            elif engine in [
                "minecraft_dictionary",
                "user_dictionary"
            ]:
                dict_count += 1

            elif engine == "retranslate":

                retranslate_count += 1
                ai_count += 1

        return {
            "total": len(self.history),
            "cache": cache_count,
            "ai": ai_count,
            "cloud": cloud_count,
            "dictionary": dict_count,
            "error": error_count,
            "retranslate": retranslate_count
        }