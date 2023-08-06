from aleksis.core.util.apps import AppConfig


class UntisConfig(AppConfig):
    name = "aleksis.apps.untis"
    verbose_name = "AlekSIS — Untis interface"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official/AlekSIS-App-Untis/",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        ([2018, 2019, 2020, 2021, 2022], "Jonathan Weth", "dev@jonathanweth.de"),
        ([2018, 2019], "Frank Poetzsch-Heffter", "p-h@katharineum.de"),
        ([2019, 2020, 2021, 2022], "Dominik George", "dominik.george@teckids.org"),
        ([2019, 2020], "Tom Teichler", "tom.teichler@teckids.org"),
        ([2019], "Julian Leucker", "leuckeju@katharineum.de"),
        ([2019], "mirabilos", "thorsten.glaser@teckids.org"),
    )
