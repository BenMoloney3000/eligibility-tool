Save your Parity dataset as .csv file and upload it to the root of the Retrofit Eligibility Web Tool project, then run the command:

.. code-block:: bash

    python3 manage.py data_upload --file=my_file.csv

Name .csv as you like, "my_file" above is just an example.

This will delete any Parity data already existing in the database and replace it with data from your file.
