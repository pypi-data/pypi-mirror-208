# Setup
* Use Python 3.10
* Install requirements from requirements.txt

# Run validation
```

```

# Running tests:
```
# All tests
python -m pytest
# For one file
python -m pytest test/test_file.py
```

# Packaging:
* Remove the old versions from `dist` folder.
* Change the version in setup.py and run:
```
python setup.py sdist
```

# Laeme uue versiooni üles:
python -m twine upload dist/* 

# PyPi repo asukoht:
https://pypi.org/project/tiivad/



# Anname talle -t käsuga uue nime.
cd docker
docker build --progress plain --no-cache -f  tiivad-base -t emuuli/local .

# Buildime teise image koos accessment koodiga:
cd docker
docker build --progress plain --no-cache -f dockerfile-evaluate .

# Get docker images
docker images

docker run -it 00f2ca8134b9 /bin/bash
docker logs container_ID