/*
 * Author: Christopher Minson
 * www.christopherminson.com
 *
 */

const STATE_DICT = {"Alaska": "AK", "Alabama": "AL", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"};
STATE_LIST = Object.keys(STATE_DICT);

const URL_SHARE = "https://www.statmap.org/";
const URL_HEATMAP = "https://www.statmap.org/data/maps/heatmap.png";
const URL_HOTZONE_MAP = "https://www.statmap.org/data/maps/hotzone.png";
const URL_HOTZONEHISTORY = "https://www.statmap.org/data/movies/hotzones.mp4";
const URL_HEATMAPHISTORY = "https://www.statmap.org/data/movies/movie.mp4";
const URL_RANKED20HISTORY = "https://www.statmap.org/data/movies/ranked20movie.mp4";
const URL_RANKED50HISTORY = "https://www.statmap.org/data/movies/ranked50movie.mp4";
const URL_CHART_CASES = "https://www.statmap.org/data/charts/chart1.png";
const URL_CHART_DEATHS = "https://www.statmap.org/data/charts/chart2.png";
const URL_CHART_DEATH_RATES = "https://www.statmap.org/data/charts/chart3.png";
const URL_CHART_7DAY= "https://www.statmap.org/data/charts/chart7.png";
const URL_CHART_7DAY_CASES= "https://www.statmap.org/data/charts/chart9.png";
const URL_CHART_USWORLD = "https://www.statmap.org/data/charts/chart4.png";
const URL_CHART_DAILYDEATHS = "https://www.statmap.org/data/charts/chart5.png";
const URL_CHART_DAILYCASES = "https://www.statmap.org/data/charts/chart8.png";
const URL_CHART_POLITICAL_RATES = "https://www.statmap.org/data/charts/chart6.png";
const URL_CHART_7DAYPOLITICAL_RATES = "https://www.statmap.org/data/charts/chart10.png";
const URL_LOCAL_CHART_ROOT = "https://www.statmap.org/data/localcharts/";
const URL_TRUMP = "https://youtu.be/wHqr9nS-JHw";



const PATH_LOCAL_DATA = "./data/active/API.ACTIVE.USDATA.json";
const PATH_PREVLOCAL_DATA = "./data/active/API.PREVACTIVE.USDATA.json";
const PATH_TOP_DATA = "./data/active/API.TOPRANKED.json";
const PATH_LOCAL_CHART_ROOT = './data/localcharts/';


var CountyData = [];
var PrevCountyData = [];
var StateData = [];
var PrevStateData = [];
var AllCounties = [];

var NoCache;

var LocaleCases = 0;
var LocaleDeaths = 0;
var LocalePrevCases = 0;
var LocalePrevDeaths = 0;
var initLoadCount = 0;


var StateToPerCapitaDeaths = {};
var CountyToPerCapitaDeaths = {};

function getSearchParameters() {
      var prmstr = window.location.search.substr(1);
      return prmstr != null && prmstr != "" ? transformToAssocArray(prmstr) : {};
}

function transformToAssocArray( prmstr ) {
    var params = {};
    var prmarr = prmstr.split("&");
    for ( var i = 0; i < prmarr.length; i++) {
        var tmparr = prmarr[i].split("=");
        params[tmparr[0]] = tmparr[1];
    }
    return params;
}

function getFormattedDate() {
    var date = new Date();
    var str =  (date.getMonth() + 1) + "/" + date.getDate() + "/" + date.getFullYear();
    return str;
}

function init() {

    var params;
    var selectedLocale = "";

    params = getSearchParameters();
    if (params.LOCALE != null) {
        selectedLocale = params.LOCALE.replace(/_/g,' ');
    }

    NoCache = new Date().getHours();
    //NoCache = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

    // START NEW
    var path_local_data = PATH_TOP_DATA+"?v="+NoCache;
    console.log("pathLocal", path_local_data);
    $.getJSON(path_local_data, function(data) {

        TopStateData = data.top_state_deaths;;
        TopCountyData = data.top_county_deaths;;
        for (i = 0; i < TopStateData.length; i++)
        {
            code = TopStateData[i].code.trim();
            state_name = TopStateData[i].state_name.trim();
            perCapita = TopStateData[i].ratio;

            key = code;
            StateToPerCapitaDeaths[key] = {rank: i + 1, perCapita: perCapita};
        }
        for (i = 0; i < TopCountyData.length; i++)
        {
            code = TopCountyData[i].code.trim();
            state_name = TopCountyData[i].state_name.trim();
            county_name = TopCountyData[i].name.trim();
            county_name = county_name.replace(/ /g,'_');
            perCapita = TopCountyData[i].ratio;

            key = county_name + ':' + code;
            CountyToPerCapitaDeaths[key] = {rank: i + 1, perCapita: perCapita};
        }

        displayLocaleRankings(selectedLocale);

    });
    // END NEW

    var path_local_data = PATH_LOCAL_DATA+"?v="+NoCache;
    $.getJSON(path_local_data, function(data) {

        CountyData = data.counties;;
        var selectedDate = data.usdate;
        for (i = 0; i < data.counties.length; i++)
        {
            var county = data.counties[i];
            var code = county.code.trim();
            var name = county.name.trim();
            var state = county.state.trim();
            var cases = county.cases;
            var deaths = county.deaths;

            if (county.name != 'New York') {
                AllCounties.push(county.name + ", " + county.state);
            }
        }

        StateData = data.states;

        //autocomplete(document.getElementById("ID_LOCAL_NAME"), AllCounties.concat(STATE_LIST));
        //
        // states go first in the completion list, followed by counties
        autocomplete(document.getElementById("ID_LOCAL_NAME"), STATE_LIST.concat(AllCounties));

        document.getElementById("ID_LOCAL_DISPLAY").style="display: block";
        $("#ID_BUSY").hide();

        if (selectedLocale.length > 1) {

            var displayLocale = selectedLocale.replace(/:/g,', ');
            $("#ID_LOCAL_NAME").val(displayLocale);

            displayLocaleData(selectedLocale);
            displayPrevLocaleData(selectedLocale);
            initLoadCount += 1;
            if (initLoadCount == 2) {
                displayDeltaLocaleData();
            }

        }

        $("#ID_LOCAL_DATE").html(selectedDate.replace("2020", "20"));
    });


    var path_local_data = PATH_PREVLOCAL_DATA+"?v="+NoCache;
    $.getJSON(path_local_data, function(data) {

        PrevCountyData = data.counties;;
        PrevStateData = data.states;
        var prevSelectedDate = data.usdate;
        for (i = 0; i < data.counties.length; i++)
        {
            var county = data.counties[i];
            var code = county.code.trim();
            var name = county.name.trim();
            var state = county.state.trim();
            var cases = county.cases;
            var deaths = county.deaths;

        }

        if (selectedLocale.length > 1) {
            displayPrevLocaleData(selectedLocale);
        }

        $("#ID_PREVLOCAL_DATE").html(prevSelectedDate.replace("2020", "20"));
        initLoadCount += 1;
        if (initLoadCount == 2) {
            displayDeltaLocaleData();
        }
    });



   $.extend(jsSocials.shares, {
    reddit: {
            label: "Reddit",
            logo: "fa fa-reddit",
            shareUrl: "https://www.reddit.com/submit?url={url}",
            countUrl: ""
        }
    });

    $("#SHARE_ID_TOP20STATES_MOVIE").jsSocials({
            url : URL_RANKED20HISTORY,
            text : "COVID-19 Top 20 States Ranked by Per Capita Deaths: 01/21/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });


    $("#SHARE_ID_HEATMAP").jsSocials({
            url : URL_HEATMAP,
            text : "COVID-19 US Per Capita Deaths Heat Map:  " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });

    $("#SHARE_ID_HOTZONE_MAP").jsSocials({
            url : URL_HOTZONE_MAP,
            text : "COVID-19 US Hot Zones:  " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });

    $("#SHARE_ID_HOTZONEHISTORY").jsSocials({
            url : URL_HOTZONEHISTORY,
            text : "COVID-19 Animated US Map Coronavirus Hot Zones  03/01/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });


    $("#SHARE_ID_HEATMAPHISTORY").jsSocials({
            url : URL_HEATMAPHISTORY,
            text : "COVID-19 Animated US Map Per Capita Coronavirus Deaths  01/21/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });

    $("#SHARE_ID_DAILY_DEATHS").jsSocials({
            url : URL_CHART_DAILYDEATHS,
            text : "COVID-19 Daily Incremental Deaths: 01/21/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });


    $("#SHARE_ID_DAILY_CASES").jsSocials({
            url : URL_CHART_DAILYCASES,
            text : "COVID-19 Daily New Cases: 01/21/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });


    $("#SHARE_ID_CUMULATIVE_DEATHS").jsSocials({
            url : URL_CHART_DEATHS,
            text : "COVID-19 US Cumulative Deaths: 01/21/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });

    $("#SHARE_ID_CUMULATIVE_DEATH_RATES").jsSocials({
            url : URL_CHART_DEATH_RATES,
            text : "COVID-19 US Cumulative Death Rates: 03/01/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });

    $("#SHARE_ID_CUMULATIVE_CASES").jsSocials({
            url : URL_CHART_CASES,
            text : "COVID-19 US Cumulative Cases:  01/21/2020 - "  + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });

    $("#SHARE_ID_USWORLD_RATES").jsSocials({
            url : URL_CHART_USWORLD,
            text : "US as Percent World's COVID-19 Cases & Deaths: 01/21/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });


    $("#SHARE_ID_POLITICAL_RATES").jsSocials({
            url : URL_CHART_POLITICAL_RATES,
            text : "COVID-19 Total Deaths Per 100,000 (Red/Blue Counties): 03/01/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });

    $("#SHARE_ID_AVG7_RATES").jsSocials({
            url : URL_CHART_7DAYPOLITICAL_RATES,
            text : "COVID-19 Weekly Deaths Per 100,000 (Red/Blue Counties): 03/01/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });


    $("#SHARE_ID_HOME").jsSocials({
            url : URL_SHARE,
            text : "COVID-19 US Dashboard:  " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });


    $("#SHARE_ID_7DAY").jsSocials({
            url : URL_CHART_7DAY,
            text : "US 7-Day Running Average COVID-19 Deaths: 01/21/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });


    $("#SHARE_ID_7DAY_CASES").jsSocials({
            url : URL_CHART_7DAY_CASES,
            text : "US 7-Day Running Average COVID-19 Cases: 01/21/2020 - " + getFormattedDate(),
            shares: ["twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });


}


function formatNumber(num) {
  return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}


function displayLocaleRankings(selectedLocale) {

    $("#ID_LOCAL_PERCAPITA").html('');
    $("#ID_LOCAL_RANK").html('');
    $("#ID_US_PERCAPITA").html('');

    if (selectedLocale == null) return;
    if (selectedLocale == undefined) return;
    if (selectedLocale.length < 2) return;

    var USPerCapita = CountyToPerCapitaDeaths['Average:USA'].perCapita;

    if (STATE_LIST.includes(selectedLocale)) {

        stateCode = STATE_DICT[selectedLocale];
        var rankStats = StateToPerCapitaDeaths[stateCode];
        var rank = rankStats.rank;
        var perCapita = rankStats.perCapita;

        perCapita = perCapita.toFixed(2);

        if (perCapita > 0.0) {
            $("#ID_LOCAL_PERCAPITA").html('Deaths Per 100,000: ' + perCapita );
            $("#ID_LOCAL_RANK").html('<a target=\"blank\" href="http://www.statmap.org/rankedstates.html">State Rank: #'+rank+'</a>');
            $("#ID_US_PERCAPITA").html('US Average: ' + USPerCapita + ' per 100,000 population');
        }
    }
    else {

        var key = selectedLocale.replace(/, /g,',');
        key = key.replace(/,/g,'.');
        key = key.replace(/ /g,'_');
        var rankStats = CountyToPerCapitaDeaths[key];
        var rank = rankStats.rank;
        var perCapita = rankStats.perCapita;

        perCapita = perCapita.toFixed(2);

        if (perCapita > 0.0) {
            $("#ID_LOCAL_PERCAPITA").html('Deaths Per 100,000: ' + perCapita );
            $("#ID_LOCAL_RANK").html('<a target=\"blank\" href="http://www.statmap.org/rankedcounties.html">County Rank: #'+rank+'</a>');
            $("#ID_US_PERCAPITA").html('US Average: ' + USPerCapita + ' per 100,000 population');
        }
    }
}

function displayDeltaLocaleData() {

    var deltaCases = LocaleCases - LocalePrevCases;
    var deltaDeaths = LocaleDeaths - LocalePrevDeaths;

    var rate = 0.0
    if (deltaCases > 0) {
        rate = ((deltaDeaths / deltaCases) * 100).toFixed(2);
    }

    $('#ID_DELTA_LOCAL_CASES').html("+"+formatNumber(deltaCases));
    $('#ID_DELTA_LOCAL_DEATHS').html("+"+formatNumber(deltaDeaths));
    $('#ID_DELTA_LOCAL_DEATH_RATE').html(rate+"%");

}

function displayLocaleData(selectedLocale) {

    var url = "";
    var selectedCounty = "";
    var selectedStateCode = "";

    if (selectedLocale == null) return;
    if (selectedLocale == undefined) return;
    if (selectedLocale.length < 2) return;

    if (STATE_LIST.includes(selectedLocale)) {

        stateCode = STATE_DICT[selectedLocale];

        var cases = 0;
        var deaths = 0;
        var rate = 0.0;
        for (i = 0; i < StateData.length; i++) {
            
            cases = StateData[i].cases;
            deaths = StateData[i].deaths;
            if (selectedLocale == StateData[i].name) break;
        }
        if (cases > 0) {
            rate = ((deaths / cases) * 100).toFixed(2);
        }
        $('#ID_LOCAL_CASES').html(formatNumber(cases));
        $('#ID_LOCAL_DEATHS').html(formatNumber(deaths));
        $('#ID_LOCAL_DEATH_RATE').html(rate+"%");
        LocaleCases = cases;
        LocaleDeaths = deaths;

        path_img = PATH_LOCAL_CHART_ROOT + stateCode + '.png' + '?' + NoCache;

        var param = selectedLocale.replace(/ /g,'_');
        param = param.replace(', ',':');
        url = URL_SHARE + "?LOCALE=" + param + "#data";
        //url = URL_SHARE + "?LOCALE=" + param;
        share_title = selectedLocale

        $("#ID_LOCAL_MAP").attr("src", path_img);

    }
    else
    {
        var county_state = selectedLocale.split(':');
        var match_name = county_state[0].trim();
        var match_state = county_state[1].trim();

        for (i = 0; i < CountyData.length; i++)
        {
            var rate = 0.00;
            var county = CountyData[i];
            var name = county.name.trim();
            var state = county.state.trim();
            if ((name == match_name) && (state == match_state)) {

                if (county.cases > 0) {
                    rate = ((county.deaths / county.cases) * 100).toFixed(2);
                }

                $('#ID_LOCAL_CASES').html(formatNumber(county.cases));
                $('#ID_LOCAL_DEATHS').html(formatNumber(county.deaths));
                $('#ID_LOCAL_DEATH_RATE').html(rate+"%");

                LocaleCases = county.cases;
                LocaleDeaths = county.deaths;
                selectedCounty = match_name;
                selectedStateCode = match_state;
                break;
            }
        }

        county = selectedCounty.replace(/\s/g, '');
        county = county.toUpperCase();
        path_img = PATH_LOCAL_CHART_ROOT + selectedStateCode + '.' +  county  + '.png' + '?' + NoCache;

        var param = selectedLocale.replace(/ /g,'_');

        param = param.replace(',',':');
        url = URL_SHARE + "?LOCALE=" + param + '#data';
        //url = URL_SHARE + "?LOCALE=" + param;
        share_title = selectedCounty + ' County'

        $("#ID_LOCAL_MAP").attr("src", path_img);
    }


    $("#ID_LOCAL_SHARE").jsSocials({
            url : url,
            text : share_title + " COVID-19 Cumulative Cases and Deaths",
            shares: ["email", "twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });
}



function displayPrevLocaleData(selectedLocale) {

    if (PrevCountyData.length < 2) return;

    var selectedCounty = "";
    var selectedStateCode = "";

    if (selectedLocale == null) return;
    if (selectedLocale == undefined) return;
    if (selectedLocale.length < 2) return;

    if (STATE_LIST.includes(selectedLocale)) {

        stateCode = STATE_DICT[selectedLocale];

        var cases = 0;
        var deaths = 0;
        var rate = 0.0;
        for (i = 0; i < PrevStateData.length; i++) {
            
            cases = PrevStateData[i].cases;
            deaths = PrevStateData[i].deaths;
            if (selectedLocale == PrevStateData[i].name) break;
        }
        if (cases > 0) {
            rate = ((deaths / cases) * 100).toFixed(2);
        }

        $('#ID_PREVLOCAL_CASES').html(formatNumber(cases));
        $('#ID_PREVLOCAL_DEATHS').html(formatNumber(deaths));
        $('#ID_PREVLOCAL_DEATH_RATE').html(rate+"%");
        LocalePrevCases = cases;
        LocalePrevDeaths = deaths;
    }
    else
    {
        var county_state = selectedLocale.split(':');
        var match_name = county_state[0].trim();
        var match_state = county_state[1].trim();

        for (i = 0; i < PrevCountyData.length; i++)
        {
            var rate = 0.00;
            var county = PrevCountyData[i];
            var name = county.name.trim();
            var state = county.state.trim();
            if ((name == match_name) && (state == match_state)) {

                if (county.cases > 0) {
                    rate = ((county.deaths / county.cases) * 100).toFixed(2);
                }

                $('#ID_PREVLOCAL_CASES').html(formatNumber(county.cases));
                $('#ID_PREVLOCAL_DEATHS').html(formatNumber(county.deaths));
                $('#ID_PREVLOCAL_DEATH_RATE').html(rate+"%");

                LocalePrevCases = county.cases;
                LocalePrevDeaths = county.deaths;

                break;
            }
        }

    }

}


function setCookie(cname, cvalue, exdays) {

    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}



function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}


function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!val) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/
      for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
          /*create a DIV element for each matching element:*/
          b = document.createElement("DIV");
          /*make the matching letters bold:*/
          b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
          b.innerHTML += arr[i].substr(val.length);
          /*insert a input field that will hold the current array item's value:*/
          b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
          /*execute a function when someone clicks on the item value (DIV element):*/
              b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field:*/
              inp.value = this.getElementsByTagName("input")[0].value;
              /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
              closeAllLists();
          });
          a.appendChild(b);
        }
      }
  });


  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });


  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }


  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    if (elmnt != null) {

        var selectedLocale = "";
        var displayLocale = $("#ID_LOCAL_NAME").val();

        if (displayLocale.length > 1) {
            var selectedLocale = displayLocale.replace(', ',':');
 
            displayLocaleData(selectedLocale);
            displayPrevLocaleData(selectedLocale);
            displayDeltaLocaleData();
            displayLocaleRankings(selectedLocale);
        }
    }

    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
      x[i].parentNode.removeChild(x[i]);
    }
  }
}


/*execute a function when someone clicks in the document:*/
document.addEventListener("click", function (e) {
    closeAllLists(e.target);
});
}
