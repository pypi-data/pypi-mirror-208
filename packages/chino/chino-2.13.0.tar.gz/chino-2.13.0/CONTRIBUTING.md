# Contributing

If you have some suggestions, improvements or bug fixes, 
please follow these steps:

- fork the repository

- create a virtualenv and run `pip install requirements.txt`
  
- develop. If you are adding new logic, **write tests** for it.
  
- launch tests. - :warning: **be careful!**:
  
    > the tests will **delete EVERYTHING stored in the account** in order to
    preserve the correctness of the tests. Run them on a custom account and
    always against the test API `https://api.test.chino.io`.

- create a Merge Request to the original repository.
