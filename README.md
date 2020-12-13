# jumpcloud

Hi Jumpcloud!
Please clone my project and place the broken-hashserve file at its root directory.

I've decided to use Behave for this assignment, which leverages BDD in an attempt to point out any bugs found in a more 'English' way. TBH it was my first time using Behave, and it was fun!  I believe I still have much to learn, however.

Scenarios are as listed in the features file.

Feature: Handle Hash Creation/Retrieval/Stats/Shutdown
	
	Scenario: Creating a HASH from a PASSWORD
	Scenario: Attempting to access /hash from bad port	
	Scenario: Retrieve a HASH for a valid ID
	Scenario: Attempt to retrieve hash for INVALID ID
	Scenario: Verify /STATS at "0" requests
	Scenario: Verify /STATS at "10" requests
	Scenario: Hash concurrently with /shutdown
		
I tested each endpoint sequentially, as well as the POST /hash concurrently using threads

I don't know a bunch about SHA512 but based on my research, I did not think I could verify that a hash used a particular hashing algorithm.
Verifying Base64 didn't make much sense either.  I suppose I could have verified non-alphanumerics in the string but it seems a little useless.

Based on the failures in the test at the following lines in my features file:
features/hasher.feature:3  Creating a HASH from a PASSWORD
features/hasher.feature:31  Verify /STATS at "10" requests

I can point out a few issues.

Issue #1: 
Expected Behavior: From Requirements, 'A POST to /hash should accept a password. It should return a job identifier
immediately.  
Current behavior: a POST to /hash returns a job identifier after the hash is complete (>5 seconds)

Issue #2: 
Expected Behavior: A GET to /stats should accept no data. It should return a JSON data structure for the total hash requests since the server started and the average time of a hash request in milliseconds.
Current behavior: a GET to /stats does return total requests, but average time returned does not make sense - One of my results equated to 266866 seconds, while a running average of requests that my test calculated is often somewhere slightly above 5 seconds.

Issue #3 (Minor): text returned when a hash is not found needs to be trimmed of spaces- 'hash not found' should be returned but there is a large amount of space padding on either side of the string

