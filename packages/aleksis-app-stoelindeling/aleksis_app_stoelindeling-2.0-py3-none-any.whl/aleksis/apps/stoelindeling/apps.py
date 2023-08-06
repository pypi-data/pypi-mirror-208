from aleksis.core.util.apps import AppConfig


class DefaultConfig(AppConfig):
    name = "aleksis.apps.stoelindeling"
    verbose_name = "AlekSIS — Stoelindeling"
    dist_name = "AlekSIS-App-Stoelindeling"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official//AlekSIS-App-Stoelindeling",
    }
    licence = "EUPL-1.2+"
    copyright_info = (([2022], "Jonathan Weth", "dev@jonathanweth.de"),)
