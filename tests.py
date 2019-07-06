import unittest
from unittest.mock import patch
from get_school_data import CollegeFinder
from bs4 import BeautifulSoup as bs
from test_data import population_div


class CollegeFinderTest(unittest.TestCase):

    def setUp(self):
        self.c = CollegeFinder('TEST')

    def tearDown(self):
        self.c = None

    def test_initialize_calls_bs(self):
        with patch(f'{CollegeFinder.__module__}.requests') as mock_requests, \
            patch(f'{CollegeFinder.__module__}.bs') as mock_bs:
            self.c.initialize()
            mock_bs.assert_called_once()

    def test_init(self):
        self.assertEqual('test', self.c.state)
        self.assertEqual(10, self.c.log.getLogger().level)
        self.assertFalse(self.c.schools == dict())
        self.assertEqual('None acquired yet.', self.c.schools)

    def test_get_population(self):
        divs = bs(population_div).find_all(class_='card-title')
        population = self.c.get_population(divs)
        self.assertEqual(130, population)


if __name__ == '__main__':
    unittest.main()
