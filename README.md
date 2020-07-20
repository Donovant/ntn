# ntn

## Setting Up Service
This assumes a user has Docker and Git installed.

Starting in your projects folder, clone the git repo
```sh
git clone https://github.com/Donovant/ntn.git
```

Open the ntn folder
```sh
cd ntn/
```

Build the docker image
```sh
docker-compose build
```

Start the docker container
```sh
docker-compose up
```
   
## Verifying Functionality Via HTTP Requests

Open the browser of your choosing and navigate to each of the following websites (You can also click the links below and they will open in your default browser).:
  - http://127.0.0.1:17177/v1.0/ntn/site/info/?site_id=AK01  
  - http://127.0.0.1:17177/v1.0/ntn/site/info/by_radius/?location=(65.1550,-147.4910)&radius=0.0  
  - http://127.0.0.1:17177/v1.0/ntn/samples/get/by_id/?site_id=AK01&start_date=1472688000&end_date=1475193600  

## Verifying Functionality Via Pytest
In a different terminal window from the one running docker above, shell into the ntn container
```sh
docker exec -it ntn bash
```

Run pytest
```sh
pytest test.py
```
After this completes, you should see 67 tests passed.

## Cleanup
To cleanup your system, stop the docker-compose service in the terminal window used above. To do this, hit Ctrl+C in that window.

Remove the ntn container
```sh
docker rm ntn
```

Remove the ntn image
```sh
docker rmi ntn_challenge
```

Remove the ntn directory from your projects
```sh
rm -rf ntn/
```

## Future Improvements and Considerations
These are my thoughts and considerations on future improvements and design thought process. They are in no particular order.
- For the purposes of this example, I have downloaded the NTN-All-w.csv file and inclided it in the repo. (This takes way to long to download on the fly during a request.)
- I would store the results from both ntn weekly endpoint calls in a database for faster retrieval. We could also automate the call to these files and update the database on a regular schedule. (I thought about implementing this using sqllite but didn't due to time constraints).
- It would be beneficial to perform a check against the database, mentioned in the previous bullet, when validating a site_id that it is valid.
- Move the common folder over to its own repo so it can be pulled in as a module where needed.
- Functionalize the error_messages portion of the webargs schemas to adhere with DRY principles and clean the code up.
- It could be beneficial to implement inheritance to the schemas to reduce duplicate code, the site_id arg and validation for example.
- I would freeze dependencies as store them in a tar file within the repo. This would facilitate faster docker build times and help protect against unversioned upgrades or other issues with external dependencies.
- Look into adding some kind of access control to the endpoints.
- Allow for radius in kilometers. (And potentially unit conversion of the values in samples, if that is even relevant)
- If the sites list will only ever include sites within the US and Canada, we could limit the maximum radius value further.
- We could possibly use a fields.list type for the location argument. This could allow us to return more specific error messages pertaining to latitude or longitude. Another possibility here would be to make latitude and longitude into completely separate variables.
- Depending on use cases etc we may want to return an error in the event that no sites are located within the radius provided for the ntn/site/info/by_radius endpoint.
- Again, depending on use cases/current usage, we may want to change the timestamp input for start_date and end_date to match what is used by the ntn sites. I just used timestamps as that's what I'm comfortable with.
- It may be beneficial to combine ntn/site/info/ and ntn/site/info/by_radius endpoints into the same function to again adhere with DRY principles and clean up code. I left these separate as I developed each endpoint individually.
- I would add more/better markers for the test suite to make it easier to run tests for a specific case, parameter, or url.
- I would change the file/folder structure of the test suite. The way this was implemented, the test.py file would get large and cumbersome quickly. It would be more beneficial to break this up (make separate files for each endpoint class or example.)
- The logging done in this repo is a bit archaic, given time its assumed this would be moved to an elk implementation or the like.
- Add tests for lower and camelcase site_id's for the ntn/site/info and ntn/samples/get/by_id endpoints.
