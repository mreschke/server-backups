# Old Pipenv Notes

I was using Pipenv to build and eploy with twice.  Here are some notes about it



# Build and Deploy

* Make code changes
* Edit `setup.py` and change the version number
* Build with `./bin/build.sh` which creates a new tar.gs file with proper version in ./dist folder
* Commit code to develop branch
* Merge code into master branch
* Merge code into 1.0 branch
* Tag code with new version
* Deploy to PyPi by running `./bin/upload-pypi.sh`



