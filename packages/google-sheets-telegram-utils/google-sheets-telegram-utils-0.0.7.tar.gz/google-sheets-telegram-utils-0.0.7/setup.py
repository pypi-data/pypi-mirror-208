from setuptools import setup, find_packages

setup(
    name='google-sheets-telegram-utils',
    version='0.0.7',
    description='A package with utils to work with google spreadsheet and telegram bots',
    url='https://github.com/alexVarkalov/google_sheets_telegram_utils',
    author='Alexander Varkalov',
    author_email='alex.varkalov@gmail.com',
    license='BSD 2-clause',
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot==20.3',
        'python-dotenv==1.0.0',
        'google-api-python-client==2.86.0',
        'google-auth-httplib2==0.1.0',
        'google-auth-oauthlib==1.0.0',
        'gspread==5.9.0',
    ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Other Environment',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.10',
    ],
)
