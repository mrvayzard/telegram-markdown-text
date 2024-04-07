from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="telegram-markdown-text",
    version="0.3",
    packages=find_packages(),
    description="Simple MarkdownV2 string builder for the Telegram API",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/mrvayzard/telegram-markdown-text",
    author="Denys Yablonskyi",
    keywords=["telegram", "tg", "markdown", "markdownV2", "text"],
)
