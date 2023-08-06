# Welcome to journalyze's documentation!

## Overview
`journalyze` is a python library that provides users with journaling prompts.
Current features are described below.
Some extra functionality in consideration includes sentiment classification.

## Installation
```
pip install journalyze
```

## How to Use
```python
from journalyze import *

# Randomly select and return a prompt from the list of prompts in csv file
getPrompt()

# Randomly select and return an easy/short prompt
get_prompt_easy()

# Randomly select and return a hard/long prompt
get_prompt_hard()

# Randomly select a given number of prompts and return
get_prompt_num()

# Adds a new given prompt to the list of prompts in csv file
add_prompt()

# Removes a given prompt from the list of prompts in csv file
remove_prompt()
```

## Example
1. Running the following code
   ```python
   import journalyze as dp
   dp = DailyPrompt('journalyze/prompts.csv')
   prompt = dp.get_prompt()
   print(prompt)
   ```
   Outputs something like this to the console
   ```
   Describe yourself using the first 10 words that come to mind. Then list 10 words that you’d like to use to describe yourself. List a few ways to transform those descriptions    into reality.
   ```
2. Running the following code
   ```python
   import journalyze as dp
   dp = DailyPrompt('journalyze/prompts.csv')
   prompt = dp.get_prompt()
   search_prompt(favorite)
   ```
   Outputs something like this to the console
   ```
   'What was your favorite part of today?', 'What is your favorite book?'
   ```


```eval_rst
.. toctree::
   :maxdepth: 2
   :caption: Contents:
```
