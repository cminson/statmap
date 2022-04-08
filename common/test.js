/*
 * Author: Christopher Minson
 * www.christopherminson.com
 *
 */


function init() {


   $.extend(jsSocials.shares, {
    reddit: {
            label: "Reddit",
            logo: "fa fa-reddit",
            shareUrl: "https://www.reddit.com/submit?url={url}",
            countUrl: ""
        }
    });

    $("#ID_SHARE").jsSocials({
            url : "fsdf",
            text : "COVID-19 Top 20 States Ranked by Per Capita Deaths: 01/21/2020 - ",
            shares: ["email", "twitter", "facebook", "reddit"],
                smallScreenWidth: 140,
                largeScreenWidth: 324
    });


}

