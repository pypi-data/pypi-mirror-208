from setuptools import setup
from io import open

with open('README.md', encoding='utf-8') as f:
      long_description = f.read()

setup(name='sqliteplus',
      version='1.1.0',
      long_description=long_description,
      long_description_content_type='text/markdown',
      description='Прога для преобразования данных полученных из БД в словарь,'
                  ' где ключами выступают названия полей.',
      url='https://github.com/prok0l/sqliteplus',
      packages=['sqliteplus'],
      author_email='egor.kuzovkin.zr@gmail.com',
      zip_safe=False)