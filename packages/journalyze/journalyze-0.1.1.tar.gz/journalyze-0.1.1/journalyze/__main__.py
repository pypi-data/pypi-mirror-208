from .journalyze import DailyPrompt

if __name__ == "__main__":
    dp = DailyPrompt('journalyze/prompts.csv')
    prompt = dp.get_prompt()
    print(prompt)

    dp.add_prompt('What was something you learned today?')
    dp.remove_prompt('What was your favorite memory from last year?')
