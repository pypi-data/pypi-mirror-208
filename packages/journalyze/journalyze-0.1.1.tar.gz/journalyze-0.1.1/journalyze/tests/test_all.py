from journalyze import *
from unittest.mock import patch
import unittest
import csv
from io import StringIO
from unittest.mock import patch


class TestDailyPrompt(unittest.TestCase):
    def setUp(self):
        self.prompts_file = 'test_prompts.csv'
        self.prompts = [
            'What was your favorite part of today?',
            'What are you grateful for today?',
            'What is your favorite book?',
            'Write about a time when you overcame a fear.',
            'Write about a time when you felt proud of yourself.',
        ]
        with open(self.prompts_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for prompt in self.prompts:
                writer.writerow([prompt])
        self.dp = DailyPrompt(self.prompts_file)

    """def test_init(self):
        self.assertEqual(self.dp.prompts, self.prompts)
    """

    def test_get_prompt(self):
        prompt = self.dp.get_prompt()
        self.assertIn(prompt, self.prompts)

    def test_get_prompt_easy(self):
        prompt = self.dp.get_prompt_easy()
        assert isinstance(prompt, str)
        assert len(prompt.split()) < 11

    def test_add_prompt(self):
        new_prompt = 'What is something you learned today?'
        self.dp.add_prompt(new_prompt)
        self.assertIn(new_prompt, self.dp.prompts)

    def test_remove_prompt(self):
        prompt_to_remove = 'What was your favorite part of today?'
        self.dp.remove_prompt(prompt_to_remove)
        self.assertNotIn(prompt_to_remove, self.dp.prompts)

    def test_search_prompt(self):
        prompts_file = "test_prompts.csv"
        daily_prompt = DailyPrompt(prompts_file)

        # Test search for "time"
        expected_result = [
            'Write about a time when you overcame a fear.',
            'Write about a time when you felt proud of yourself.',
        ]
        self.assertEqual(daily_prompt.search_prompt("time"), expected_result)

        # Test search for "favorite"
        expected_result = ['What was your favorite part of today?', 'What is your favorite book?']
        self.assertEqual(daily_prompt.search_prompt("favorite"), expected_result)

        # Test search for "dog" (not present in prompts)
        expected_result = []
        self.assertEqual(daily_prompt.search_prompt("dog"), expected_result)


class TestDailyPromptIntegration(unittest.TestCase):
    def setUp(self):
        self.prompts_file = 'test_prompts.csv'
        self.prompts = ['What was your favorite part of today?', 'What are you grateful for today?']
        with open(self.prompts_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for prompt in self.prompts:
                writer.writerow([prompt])
        self.dp = DailyPrompt(self.prompts_file)

    def test_integration(self):
        # Check that the initial prompts are in the list
        self.assertEqual(self.dp.prompts, self.prompts)

        # Check that a prompt can be retrieved
        prompt = self.dp.get_prompt()
        self.assertIn(prompt, self.prompts)

        # Check that a new prompt can be added
        new_prompt = 'What is something you learned today?'
        self.dp.add_prompt(new_prompt)
        self.assertIn(new_prompt, self.dp.prompts)

        # Check that a prompt can be removed
        prompt_to_remove = 'What was your favorite part of today?'
        self.dp.remove_prompt(prompt_to_remove)
        self.assertNotIn(prompt_to_remove, self.dp.prompts)


if __name__ == '__main__':
    unittest.main()
