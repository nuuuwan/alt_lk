import unittest

from alt_lk import Alt, LatLng

TEST_DATA_LIST = [
    {
        "name": "Lipton Circus, Colombo",
        "latlng": LatLng(6.917283145461265, 79.8647928104344),
        "expected_alt": Alt(13),
    },
    {
        "name": "Pidurutalagala",
        "latlng": LatLng(7.000925069638563, 80.77341850688242),
        "expected_alt": Alt(2523),
    },
    {
        "name": "Sri Paada",
        "latlng": LatLng(6.809498226498262, 80.49925188865949),
        "expected_alt": Alt(2193),
    },
    {
        "name": "Kandy Clock Tower, Kandy",
        "latlng": LatLng(7.2931324033205325, 80.63502748186357),
        "expected_alt": Alt(505),
    },
    {
        "name": "Grand Roundabout, Nuwara Eliya",
        "latlng": LatLng(6.967671358450489, 80.76758495578306),
        "expected_alt": Alt(1885),
    },
    {
        "name": "War Memorial, Galle",
        "latlng": LatLng(6.030583497505944, 80.21599402784966),
        "expected_alt": Alt(11),
    },
    {
        "name": "Thiruvalluvar Statue, Jaffna",
        "latlng": LatLng(9.665119015313726, 80.00934379594969),
        "expected_alt": Alt(3),
    },
    {
        "name": "Railway Station, Trincomalee",
        "latlng": LatLng(8.584698672875373, 81.22584654491557),
        "expected_alt": Alt(8),
    },
    {
        "name": "Clock Tower, Batticaloa",
        "latlng": LatLng(7.714131775076944, 81.69771058017439),
        "expected_alt": Alt(10),
    },
    {
        "name": "Thuparamaya, Anuradhapura",
        "latlng": LatLng(8.355336201802075, 80.39648276371774),
        "expected_alt": Alt(90),
    },
    {
        "name": "Kirigalpotta",
        "latlng": LatLng(6.798998326979714, 80.7666713506962),
        "expected_alt": Alt(2368),
    },
    {
        "name": "Totapola",
        "latlng": LatLng(6.833308152755971, 80.81967069953289),
        "expected_alt": Alt(2357),
    },
    {
        "name": "Gongala",
        "latlng": LatLng(6.38585242759519, 80.65383469745277),
        "expected_alt": Alt(1344),
    },
]


class TestCase(unittest.TestCase):
    def test_alt(self):
        for d in TEST_DATA_LIST:
            name = d["name"]
            latlng = d["latlng"]
            expected_alt = d["expected_alt"]
            computed_alt = Alt.from_latlng(latlng)
            s = f"{name} ({latlng}): {computed_alt}"
            self.assertEqual(
                expected_alt,
                computed_alt,
                f"{s} != {expected_alt}",
            )
