<?php
echo "Start create CSV File ... \n";
//API's URL 
$host = 'https://www.mylittlesalesman.com/api/v1/listings';

//username.
$user_name = '';

//password.
$password = '';

//Initiate cURL request
$ch = curl_init($host);

// Set the header by creating the basic authentication
$headers = array(
'Content-Type: application/json',
'Authorization: Basic '. base64_encode("$user_name:$password")
);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
$response = curl_exec($ch);

//Check if any errors occured.
if(curl_errno($ch)){
throw new Exception(curl_error($ch));
}

curl_close($ch);
//save the response a json file
// $output_filename = "/home/www/production/feeds/51283/51283.json";
$output_filename = "./data.json";
$fp = fopen($output_filename, 'w');
fwrite($fp, $response);
fclose($fp);

// START THE CONVERT from JSON to Array
$response   = (file_get_contents($output_filename));
$data       = (json_decode($response,true));

// Make header ============================================
$dynamicHeaderFromData = [];
$parentObjects         = [];
foreach($data['Listings'] as $dataKey => $ListingObject) {

    foreach($ListingObject as $listingObjectKey => $listingObjectValue) {
        if(is_array($listingObjectValue)) {
            if(!in_array($listingObjectKey, $parentObjects) && $listingObjectKey != "Images" && $listingObjectKey != "Videos") {
                array_push($parentObjects, $listingObjectKey);
            }
            foreach($listingObjectValue as $listingObjectValueKey => $listingObjectValueObj) {
                if (!in_array($listingObjectValueKey, $dynamicHeaderFromData)) {
                    array_push($dynamicHeaderFromData, $listingObjectValueKey);
                }
            }
        } else {
            if (!in_array($listingObjectKey, $dynamicHeaderFromData)) {
                array_push($dynamicHeaderFromData, $listingObjectKey);
            }
        }
    }
}
// ========================================================

// Specify the CSV file path
$csvFilePath = 'output.csv';

// Open the CSV file for writing
$csvFile = fopen($csvFilePath, 'w');
fputcsv($csvFile, $dynamicHeaderFromData);

foreach ( $data['Listings'] as $key => $value ) {
    fputcsv( $csvFile, makeFileRowFormat( $value, $dynamicHeaderFromData, $parentObjects ) );
}

// Close the CSV file
fclose( $csvFile );

echo "CSV file created successfully!";

function makeFileRowFormat($data, $dynamicHeaderFromData, $parentObjects) {
    $fileRow = array();

    foreach($dynamicHeaderFromData as $key => $value) {
        $isPushed = false;
        foreach($parentObjects as $parentObjectKey => $parentObjectValue) {
            if (isset($data[$parentObjectValue][$value])) {
                array_push($fileRow, $data[$parentObjectValue][$value]);
                $isPushed = true;
            }
        }

        if( isset($data[$value]) && $value != "Images" && $value != "Videos") {
            array_push($fileRow, str_replace(["\r\n", "\n"], '</br>', $data[$value]) );
        } elseif( $value == "Images" ) {
            $images = "";
            if(isset($data['Images']['Images'])) {
                foreach( $data['Images']['Images'] as $image ) {
                    $images = $images . ( ($images != "" ) ? "," . $image['Url'] : $image['Url'] );
                }
            }
            array_push($fileRow, $images);
         
        } elseif( $value == "Videos" ) {
            $videos = "";
            if(isset($data['Videos']['Videos'])) {
                foreach( $data['Videos']['Videos'] as $video ) {
                    $videos = $videos . ( ($videos != "" ) ? "," . $video['Url'] : $video['Url'] );
                }
            }
            array_push($fileRow, $videos);
        } elseif( $isPushed == false ) {
            array_push($fileRow, "");
        }
    }

    return $fileRow;
}
