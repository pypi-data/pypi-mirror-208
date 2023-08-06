import csv
import random


class DailyPrompt:
    # initialize the object and load the prompts from a CSV file.
    def __init__(self, prompts_file):
        self.prompts_file = prompts_file
        self.prompts = []
        with open(prompts_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                self.prompts.append(row[0])

    def get_prompt(self):
        """
        This function randomly selects a prompt
        from the list of prompts and return it to the user.
        Args:
            self
        Returns:
            prompt (data)
        """
        prompt = random.choice(self.prompts)
        return str(prompt)

    def get_prompt_easy(self):
        """
        This function randomly selects an EASY/SHORT prompt
        from the list of prompts and return it to the user.
        Args:
            self
        Returns:
            prompt (data)
        Note: an easy prompt is defined here as
        a prompt with less than 11 words
        """
        easy_prompt = random.choice(self.prompts)
        if len(easy_prompt.split()) < 11:
            return str(easy_prompt)
        else:
            return None

    def add_prompt(self, prompt):
        """
        This function adds a new prompt to the list of prompts.
        Args:
            Prompt to be appended
        Returns:
            None: see note
        Note: appends the given prompt to the csv file of prompts
        """
        self.prompts.append(prompt)

    def remove_prompt(self, prompt):
        """
        This function removes a prompt from the list of prompts.
        Args:
            Prompt to be removed
        Returns:
            None: see note
        Note: removes the given prompt from the list of prompts
        """
        self.prompts.remove(prompt)

    def search_prompt(self, keyword):
        """
        This function searches the list of prompts for a keyword
        and returns a list of prompts that contain the keyword.
        Args:
            keyword: word to search for
        Returns:
            result: list of prompts containing the keyword
        """
        result = []
        for prompt in self.prompts:
            if keyword.lower() in prompt.lower():
                result.append(prompt)
        return result
