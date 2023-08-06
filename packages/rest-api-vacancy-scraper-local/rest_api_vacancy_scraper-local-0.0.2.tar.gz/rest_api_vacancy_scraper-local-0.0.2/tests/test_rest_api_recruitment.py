import json
import os
import unittest
from unittest.mock import patch
from scraper_REST_API import app


class TestAPI(unittest.TestCase):
    def setUp(self) -> None:
        # Change current working directory to the directory containing the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

    @patch('monster_com_scraper.MonsterComScraper.page_scraping')
    def test_api_with_valid_params(self, mock_page_scraping):
        mock_page_scraping.return_value = None
        with app.test_client() as client:
            response = client.post('/api', json={
                "position": "Software Engineer",
                "location": "San Francisco",
                "num of jobs": 5,
                "source": "monster"
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.data), {'Message': 'Done Scraping!'})
            mock_page_scraping.assert_called_with(5)

    def test_api_with_missing_params(self):
        with app.test_client() as client:
            response = client.post('/api', json={
                "source": "monster"
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.data), {'Error': 'Invalid parameters'})

    def test_api_with_invalid_source(self):
        with app.test_client() as client:
            response = client.post('/api', json={
                "position": "Software Engineer",
                "location": "San Francisco",
                "num of jobs": 2,
                "source": "invalid"
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.data), {'Error': 'Invalid source'})

    @patch('indeed_com_scraper.IndeedComScraper.page_scraping')
    def test_api_with_indeed_source(self, mock_page_scraping):
        with app.test_client() as client:
            response = client.post('/api', json={
                "position": "Software Engineer",
                "location": "San Francisco",
                "num of jobs": 1,
                "source": "indeed"
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.data), {'Message': 'Done Scraping!'})
            mock_page_scraping.assert_called_with(1)


if __name__ == '__main__':
    with unittest.mock.patch('builtins.open', unittest.mock.mock_open()) as m:
        unittest.main()