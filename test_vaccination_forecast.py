import unittest

from vaccination_forecast import need_second_vaccination_for


class VaccinationForecastTest(unittest.TestCase):

    def test_second_vaccionation_calculation(self):
        vaccinations = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.assertEqual(need_second_vaccination_for(3, vaccinations), 10)


if __name__ == '__main__':
    unittest.main()
