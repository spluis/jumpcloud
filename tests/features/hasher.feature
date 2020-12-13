Feature: Handle Hash Creation/Retrieval/Stats/Shutdown
	
	Scenario: Creating a HASH from a PASSWORD
		Given the hashing server is running
		And the PORT is set to "8088"
		When I call POST to /hash with password "Pa$$w0rd1" password on port "8088"
		Then I should receive an ID right away
		And 5 seconds later a 200 response
		
	Scenario: Attempting to access /hash from bad port
		Given the PORT is set to "8088"
		When I call POST to /hash with password "B0bsB3rg3rs." on port "9011"
		Then I should receive a ConnectionRefused Error
		
	Scenario: Retrieve a HASH for a valid ID
		Given a hash is already created
		When I call GET to /hash/ID
		Then I should receive a base64 password hash
	
	Scenario: Attempt to retrieve hash for INVALID ID
		Given an INVALID HASH ID
		When I call GET to /hash/ID
		Then I should receive an error
		
	Scenario: Verify /STATS at "0" requests
		Given a reset of server
		When I call GET /STATS
		Then I should receive JSON with "0" TotalRequests
		And "0" AverageTime
		
	Scenario: Verify /STATS at "1" requests
		Given I generate "1" total requests since server boot
		When I call GET /STATS
		Then I should receive JSON with "1" TotalRequests
		And "Reasonable" AverageTime
		
	Scenario: Hash concurrently with /shutdown
		Given I queue up "5" threads for "5" passwords and a shutdown
		When I trigger them to POST /HASH
		Then I should receive "5" OK responses
		And Shutdown should occur with 200 Response
		