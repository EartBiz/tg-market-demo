"""Автолінзи: Основна оптика / ПТФ → тип → виробник → марка → модель → рік → сторона."""

from __future__ import annotations

STOCK_NOTE = "Товар під замовлення (привеземо)"


def _sides(prefix: str, title: str, price_one: int, price_pair: int) -> list[dict]:
    return [
        {"id": f"{prefix}-l", "name": f"{title} — ліва", "price": price_one},
        {"id": f"{prefix}-r", "name": f"{title} — права", "price": price_one},
        {"id": f"{prefix}-pair", "name": f"{title} — пара", "price": price_pair},
    ]


# category → type → manufacturer → car brand → model → year → items
CATALOG: dict = {
    "Основна оптика": {
        "LED": {
            "Aozoom": {
                "Volkswagen": {
                    "Golf 7": {
                        "2013-2017": _sides(
                            "az-led-g7", "Лінза LED Aozoom Golf 7", 3200, 6000
                        ),
                    },
                    "Passat B8": {
                        "2015-2020": _sides(
                            "az-led-pb8", "Лінза LED Aozoom Passat B8", 3400, 6400
                        ),
                    },
                },
                "Toyota": {
                    "Camry 70": {
                        "2018-2023": _sides(
                            "az-led-cam70", "Лінза LED Aozoom Camry 70", 3500, 6600
                        ),
                    },
                },
            },
            "Sanvi": {
                "Volkswagen": {
                    "Golf 7": {
                        "2013-2017": _sides(
                            "sv-led-g7", "Лінза LED Sanvi Golf 7", 2900, 5500
                        ),
                    },
                },
                "Hyundai": {
                    "Tucson": {
                        "2015-2020": _sides(
                            "sv-led-tuc", "Лінза LED Sanvi Tucson", 3000, 5700
                        ),
                    },
                },
            },
        },
        "Bi-LED": {
            "Aozoom": {
                "Skoda": {
                    "Octavia A7": {
                        "2013-2017": _sides(
                            "az-biled-a7", "Bi-LED Aozoom Octavia A7", 3800, 7200
                        ),
                    },
                },
                "Toyota": {
                    "RAV4": {
                        "2019-2023": _sides(
                            "az-biled-rav4", "Bi-LED Aozoom RAV4", 4000, 7600
                        ),
                    },
                },
            },
            "Sanvi": {
                "Renault": {
                    "Megane 3": {
                        "2009-2014": _sides(
                            "sv-biled-m3", "Bi-LED Sanvi Megane 3", 3600, 6900
                        ),
                    },
                },
                "Kia": {
                    "Sportage": {
                        "2016-2021": _sides(
                            "sv-biled-sp", "Bi-LED Sanvi Sportage", 3700, 7000
                        ),
                    },
                },
            },
        },
        "Лазерні": {
            "Aozoom": {
                "BMW": {
                    "3 Series F30": {
                        "2012-2018": _sides(
                            "az-laser-f30", "Лазерна лінза Aozoom F30", 5200, 9900
                        ),
                    },
                },
                "Mercedes-Benz": {
                    "C-Class W205": {
                        "2014-2020": _sides(
                            "az-laser-w205", "Лазерна лінза Aozoom W205", 5400, 10300
                        ),
                    },
                },
            },
            "Sanvi": {
                "Audi": {
                    "A4 B9": {
                        "2016-2022": _sides(
                            "sv-laser-a4b9", "Лазерна лінза Sanvi A4 B9", 5000, 9500
                        ),
                    },
                },
            },
        },
        "Ксенон": {
            "Aozoom": {
                "Volkswagen": {
                    "Passat B7": {
                        "2011-2015": _sides(
                            "az-xen-pb7", "Ксенон Aozoom Passat B7", 2400, 4500
                        ),
                    },
                },
                "Toyota": {
                    "Corolla": {
                        "2013-2018": _sides(
                            "az-xen-cor", "Ксенон Aozoom Corolla", 2300, 4300
                        ),
                    },
                },
            },
            "Sanvi": {
                "Honda": {
                    "Civic": {
                        "2012-2016": _sides(
                            "sv-xen-civ", "Ксенон Sanvi Civic", 2200, 4100
                        ),
                    },
                },
                "Mazda": {
                    "CX-5": {
                        "2012-2016": _sides(
                            "sv-xen-cx5", "Ксенон Sanvi CX-5", 2350, 4400
                        ),
                    },
                },
            },
        },
    },
    "ПТФ": {
        "LED ПТФ": {
            "Aozoom": {
                "Volkswagen": {
                    "Golf 7": {
                        "2013-2017": _sides(
                            "az-ptf-g7", "ПТФ LED Aozoom Golf 7", 1800, 3400
                        ),
                    },
                    "Tiguan": {
                        "2016-2020": _sides(
                            "az-ptf-tig", "ПТФ LED Aozoom Tiguan", 1900, 3600
                        ),
                    },
                },
                "Toyota": {
                    "Camry 70": {
                        "2018-2023": _sides(
                            "az-ptf-cam70", "ПТФ LED Aozoom Camry 70", 1850, 3500
                        ),
                    },
                },
            },
            "Sanvi": {
                "Hyundai": {
                    "Tucson": {
                        "2015-2020": _sides(
                            "sv-ptf-tuc", "ПТФ LED Sanvi Tucson", 1700, 3200
                        ),
                    },
                },
                "Kia": {
                    "Sportage": {
                        "2016-2021": _sides(
                            "sv-ptf-sp", "ПТФ LED Sanvi Sportage", 1750, 3300
                        ),
                    },
                },
            },
        },
        "Ксенон ПТФ": {
            "Aozoom": {
                "BMW": {
                    "3 Series F30": {
                        "2012-2018": _sides(
                            "az-ptf-xen-f30", "ПТФ ксенон Aozoom F30", 2100, 4000
                        ),
                    },
                },
            },
            "Sanvi": {
                "Audi": {
                    "A4 B9": {
                        "2016-2022": _sides(
                            "sv-ptf-xen-a4", "ПТФ ксенон Sanvi A4 B9", 2000, 3800
                        ),
                    },
                },
            },
        },
    },
}