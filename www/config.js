//
// Overwrite these with your own settings in config.local.js!
//

// OpenHAB URL (without the "http://" part; note that you can't use "localhost" or "127.0.0.1" or OpenHAB will send "Connection Refused")
var openhabURL = "192.168.1.107:8080/rest/items/";	// TODO: change this to your Pi's IP address
// Log URL
var logURL = "http://192.168.1.107/data.php?item=";	// TODO: change this to your Pi's IP address

// Wunderground API
// TODO: insert your API key and location code (example location code: pws:KNYNEWYO118)
var weatherURL = "http://api.wunderground.com/api/f1267833f6b90414/conditions/q/46060.json";
var forecastURL = "http://api.wunderground.com/api/f1267833f6b90414/forecast/q/46060.json";

// Logging level (0 = off, 1 = ajax errors only, 2 = some logging, 3 = full logging)
// This logs to the developer console: in Google Chrome, press F12 and make sure the "Console" tab is selected
var loggingLevel = 3;
// How often to check weather (in milliseconds)
var weatherFrequency = 600000;	// every 600 seconds (= 10 minutes)
var forecastFrequency = 3600000;	// every 3600 seconds (= 1 hour)

var reloadHour = 4;	// time at which to reload the entire page. Helps keep things fresh (Chrome tends to time out the websockets). 24 hour format (0 = midnight, 23 = 11 PM)

var weatherUnit = "fc"; //c for celsius, f for farenheit, cf for celsius (farenheit), fc for farenheit (celsius)
var tempRound = true;	//rounds all temperatures to whole numbers (so today and forecast match)

var twelveHour = true;	//if true, time is displayed as 12-hour rather than 24-hour
var twelveHourAMPM = true;	//if true, 'am' or 'pm' is appended to the time. Probably doesn't make sense unless twelveHour is also true.