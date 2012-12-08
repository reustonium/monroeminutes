<?php

	require_once("debug.php");
	require_once("SearchTool.class.php");

	// this is the search api file where you can present it with POST data and
	// it will return back a json object with an array of minutes in it

	//dprint("Running search and returning json with results ...");

	// get our POST information
	$searchstring = $_GET['searchstring'];
	$address = $_GET['address'];
	$startdate = $_GET['startdate'];
	$enddate = $_GET['enddate'];
	$organizations = $_GET['organizations'];
	
	// create an instance of our search tool
	$searchTool = new SearchTool();
	
	// record start time
	$mtime = microtime(); 
	$mtime = explode(" ",$mtime); 
	$mtime = $mtime[1] + $mtime[0];
	$starttime = $mtime; 
	
	// perform our search based on the two flows (address or no address)
	if( $address == "" )
	{
		dprint("Getting minutes list ...");
	
		if( $searchstring == "" )
		{
			dprint("Search string was empty, returning empty array.");
			$results = array();
		}
		else
		{
			dprint("Performing search using POST data.");
			$results = $searchTool->SearchWithoutAddress($startdate, $enddate, $organizations, $searchstring);
		}

	}
	else
	{
		// TODO: do this.  need to incorporate John Farnach's code for using the address
		$results = array();
	}
				
	// calculate time taken
	$mtime = microtime(); 
	$mtime = explode(" ",$mtime); 
	$mtime = $mtime[1] + $mtime[0]; 
	$endtime = $mtime; 
	$totaltime = ($endtime - $starttime); 
	
	//
	// Now that we have our results from the search, we need to place them into our return
	// json object which looks like this:
	//
	// {
	// 		"status":"0",
	//		"errorText":"None",
	//		"queryTime":"8",
	//		"resultCount":4,
	//		"results":...
	// }
	//
		
	dprint("converting to json and printing ...");
	
	// convery array to json
	$jsonResults = json_encode($results);
	
	$resultsCount = count($results);
	
	$retVal = '{ "error":"0", "errorText":"None", "queryTime":"' . $totaltime . '", "resultsCount":"' . $resultsCount . '", "results":' . $jsonResults . '}';
	
	// print to the page
	echo $retVal;
	
?>