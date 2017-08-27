# moodle Shibboleth Downloader

The `moodle.py` script downloads all the files posted in the course page of all the courses in your moodle page. Files with the same name in a course are not downloaded and are ignored.

Set the following in the file `config.ini` before running the script

- `username` : your_Username
- `password` : your_Password
- `root_dir` : The root directory for where the files are to be stored
- `moodle_url` : URL for moodle authentication / Where you type in your credentials


All the files are stored in their respective directories inside the `root_dir` with the names as in moodle.


#### REQUIREMENTS

- Python 2.7
- mechanize - `sudo apt-get install mechanize`

### EXTRAS

This code is the modified version of the downloader created by vinaychandra (https://github.com/vinaychandra/Moodle-Downloader)
