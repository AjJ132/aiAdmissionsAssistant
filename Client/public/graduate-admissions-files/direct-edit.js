/*Button Code in OU <a id="de" href="^0">&copy;</a>*/
function directedit() {
	if(document.getElementById("de") != null && document.getElementById("directedit")) {
		var link = document.getElementById("de").parentNode.innerHTML;
		document.getElementById("de").parentNode.innerHTML = "";
		document.getElementById("directedit").innerHTML = link;	
	}
}


/*window.onload = function() {
	directedit()
};*/

//replaced above script with the below to fix window.onload conflicts with other embeds
window.addEventListener('DOMContentLoaded', (event) => {
	directedit();
});

//jQuery option, if available..
/*$(document).ready(function () {
    $("#directedit").html(jQuery("#de"));
});*/




//THIS IS TEMPORARY
function skinCheck(skin){
	let title = '';
	if(document.querySelector('.site_title a')){
		title = document.querySelector('.site_title a').textContent;
	}
	
	const header = '<div class="inner_rim"> <div class="logo_container medium"> <a href="https://www.kennesaw.edu"> <img src="https://webstatic.kennesaw.edu/_omni/images/global/logo_mobile.png?v=1" alt="Kennesaw State University" class="mobile_logo"> <img src="https://webstatic.kennesaw.edu/_omni/images/global/logo_black.png?v=1" alt="Kennesaw State University" class="print_logo"> </a> <div class="top"><a href="https://www.kennesaw.edu">Kennesaw State University <div class="logo"></div></a><p class="site_title"><a href="">'+title+'</a></p> </div> <div class="bottom"></div> </div> <div id="header_nav"> <!--<ul class="utility"> <li><a href="https://www.kennesaw.edu/myksu/">MyKSU</a></li> <li><a href="https://www.kennesaw.edu/azindex/">A-Z Index</a></li> <li><a href="https://www.kennesaw.edu/directories.php">Directories</a></li> <li><a href="https://www.kennesaw.edu/maps/">Campus Maps</a></li> </ul>--> <ul class="active"> <li><a href="https://www.kennesaw.edu/apply.php">Apply</a></li> <li><a href="https://www.kennesaw.edu/visit.php">Visit</a></li> <li><a href="https://www.kennesaw.edu/give.php">Give</a></li> <li><a href="https://calendar.kennesaw.edu">Calendar</a></li> </ul> <ul class="info_for_wrapper"> <li class="info_for" tabindex="0" role="button" aria-label="Toggle Information Navigation" aria-expanded="false"> <p>Resources For<img class="info_for_icon" src="https://webstatic.kennesaw.edu/_resources/images/template/chevron-down.svg" alt="Chevron Down Icon" height="15px" width="13px"></p> <ul> <li><a href="#">Current Students</a></li> <li><a href="#">Online Only Students</a></li> <li><a href="#">Faculty &amp; Staff</a></li> <li><a href="#">Parents &amp; Family</a></li> <li><a href="#">Alumni &amp; Friends</a></li> <li><a href="#">Community &amp; Business</a></li> </ul>				</li> </ul> </div>            </div>';
	const goldbar = '<div id="new_header"> <div id="ksu_logo"> <a href="https://www.kennesaw.edu/"> <img src="https://webstatic.kennesaw.edu/_resources/images/template/ksu_horizontal.svg" alt="Kennesaw State University" height="50px"> </a> </div> <div id="main_search"> <a tabindex="0" class="search_button" role="button" aria-label="Toggle Search" aria-controls="header_search" aria-expanded="false"> <img src="https://webstatic.kennesaw.edu/_resources/images/template/search.svg" alt="Magnifying Glass Icon" height="20px" width="20px"> </a> <form id="header_search" class="search" role="search" aria-label="Sitewide" action="https://ksusearch.kennesaw.edu/s/search.html?collection=kennesaw-search"> <input type="hidden" name="collection" value="kennesaw-search"> <input type="search" name="query" id="header_search_box" placeholder="KSU Search" aria-label="KSU Search" tabindex="-1"> <input type="submit" value="SEARCH"> </form>	</div> <div class="main_nav"> <a tabindex="0" class="hamburger_button" role="button" aria-label="Toggle Navigation" aria-controls="header_navigation" aria-expanded="true"> <img class="open" src="https://webstatic.kennesaw.edu/_resources/images/template/bars.svg" alt="Open Menu Icon" width="20px"> <img class="close" src="https://webstatic.kennesaw.edu/_resources/images/template/times.svg" alt="Close Menu Icon" width="20px"> <span>MENU</span></a> </div> </div> <ul id="throne_room"> <li id="search"> <img src="Kennesaw%20State%20University%20in%20Georgia_files/search.png" alt="Search"> <span>Search</span> </li> <li id="menu"> <img src="Kennesaw%20State%20University%20in%20Georgia_files/menu.png" alt="Menu"> <span>Menu</span> </li> </ul> <div class="nav_wrapper"> <ul id="high_council_chamber"> <li><a href="https://www.kennesaw.edu/about">About KSU</a></li> <li><a href="https://www.kennesaw.edu/academics.php">Academics</a></li> <li><a href="https://www.kennesaw.edu/admissions.php">Admissions</a></li> <li><a href="https://www.kennesaw.edu/athletics.php">Athletics</a></li> <li><a href="https://www.kennesaw.edu/campuslife.php">Campus Life</a></li> <li><a href="https://www.kennesaw.edu/research.php">Research</a></li> <li><a href="https://www.kennesaw.edu/global.php">Global</a></li> </ul> </div><ul id="mobile_high_council_chamber"><li><a href="/_dev/kb/test/stratcomm/index.php">Home</a></li><li><a href="http://styleguide.kennesaw.edu/">Brand Management</a></li><li><a href="/_dev/kb/test/stratcomm/creative-services/index.php">Creative Services</a><div class="plus_wrapper icon open-icon"><span class="vertical"></span><span class="horizontal"></span></div><ul class="second_tier"><li><a href="/_dev/kb/test/stratcomm/creative-services/index.php">Overview</a></li><li><a href="/_dev/kb/test/stratcomm/creative-services/design-services.php">Design Services</a></li><li><a href="/_dev/kb/test/stratcomm/creative-services/photography-services.php">Photography Services</a></li><li><a href="/_dev/kb/test/stratcomm/creative-services/video-services.php">Video Services</a></li></ul></li><li><a href="/_dev/kb/test/stratcomm/marketing/index.php">Marketing</a><div class="plus_wrapper icon open-icon"><span class="vertical"></span><span class="horizontal"></span></div><ul class="second_tier"><li><a href="/_dev/kb/test/stratcomm/marketing/index.php">Overview</a></li><li><a href="/_dev/kb/test/stratcomm/marketing/timing-workflow.php">Timing and Workflow</a></li><li><a href="/_dev/kb/test/stratcomm/marketing/digital-signage.php">KSU Digital Signage</a></li><li><a href="/_dev/kb/test/stratcomm/marketing/vendor-selection.php">Vendor Selection</a></li><li><a href="/_dev/kb/test/stratcomm/marketing/definitions.php">Definitions</a></li></ul></li><li><a href="/_dev/kb/test/stratcomm/social-media/index.php">Social Media</a><div class="plus_wrapper icon open-icon"><span class="vertical"></span><span class="horizontal"></span></div><ul class="second_tier"><li><a href="/_dev/kb/test/stratcomm/social-media/index.php">Overview</a></li><li><a href="/_dev/kb/test/stratcomm/social-media/social-media-guidelines.php">Social Media Guidelines</a></li><li><a href="/_dev/kb/test/stratcomm/social-media/getting-started.php">Getting Started on Social Media</a></li><li><a href="/_dev/kb/test/stratcomm/social-media/best-practices.php">Best Practices on Social Media</a></li><li><a href="/_dev/kb/test/stratcomm/social-media/channels.php">Channels</a></li><li><a href="/_dev/kb/test/stratcomm/social-media/safety-guidelines.php">Faculty and Staff Safety Guidelines</a></li><li><a href="/_dev/kb/test/stratcomm/social-media/community-guidelines.php">Community Guidelines</a></li></ul></li><li><a href="/_dev/kb/test/stratcomm/strategic-communications/index.php">Strategic Communications</a><div class="plus_wrapper icon open-icon"><span class="vertical"></span><span class="horizontal"></span></div><ul class="second_tier"><li><a href="/_dev/kb/test/stratcomm/strategic-communications/index.php">Overview</a></li><li><a href="/_dev/kb/test/stratcomm/strategic-communications/media-logo-use.php">Media Logo Use</a></li></ul></li><li><a href="/_dev/kb/test/stratcomm/project-request.php">Project Request</a></li><li><a href="/_dev/kb/test/stratcomm/publications/index.php">Publications</a><div class="plus_wrapper icon open-icon"><span class="vertical"></span><span class="horizontal"></span></div><ul class="second_tier"><li><a href="/_dev/kb/test/stratcomm/publications/magazine.php">Kennesaw State University Magazines</a></li></ul></li><li><a href="/_dev/kb/test/stratcomm/contact/index.php">Contact Us</a><div class="plus_wrapper icon open-icon"><span class="vertical"></span><span class="horizontal"></span></div><ul class="second_tier"><li><a href="/_dev/kb/test/stratcomm/contact/emails.php">Emails</a></li></ul></li></ul>';
	const footer = '<div class="section is_black is_hidden_mobile is_constrained"> <div class="section_content"> <div class="three_col has_gap"> <div class="is_flex_40"> <div class="section_heading"> <p class="heading is_bottom is_left is_text_4 is_gold" aria-level="4">Contact Info</p> </div> <div class="two_col has_gap"> <div> <p><strong>Kennesaw Campus</strong><br>1000 Chastain Road<br>Kennesaw, GA 30144</p> <p><strong>Marietta Campus</strong><br>1100 South Marietta Pkwy<br>Marietta, GA 30060</p> <p><strong><a href="https://maps.kennesaw.edu/">Campus Maps</a></strong></p> </div> <div> <p><strong>Phone</strong><br>470-KSU-INFO<br>(470-578-4636)</p> <p><strong><a href="https://www.kennesaw.edu/info/">kennesaw.edu/info</a></strong></p> <p><strong><a href="https://www.kennesaw.edu/news/media-contacts.php">Media Contacts</a></strong></p> </div> </div> </div> <div class="is_flex_20"> <div class="section_heading"> <p class="heading is_bottom is_left is_text_4 is_gold" aria-level="4">Resources For</p> </div> <ul class="link_list"> <li><a href="https://www.kennesaw.edu/current-students/">Current Students</a></li> <li><a href="https://www.kennesaw.edu/online-students/">Online Only Students</a></li> <li><a href="https://www.kennesaw.edu/faculty-staff/">Faculty &amp; Staff</a></li> <li><a href="https://www.kennesaw.edu/parents-family/">Parents &amp; Family</a></li> <li><a href="https://www.kennesaw.edu/alumni-friends/">Alumni &amp; Friends</a></li> <li><a href="https://www.kennesaw.edu/community-business/">Community &amp; Business</a></li> </ul> </div> <div class="is_flex_40"> <div class="section_heading"> <p class="heading is_bottom is_left is_text_4 is_gold" aria-level="4">Related Links</p> </div> <div class="two_col has_gap"> <div> <ul class="link_list"> <li><a href="https://www.kennesaw.edu/library/">Libraries</a></li> <li><a href="https://ksuhousing.kennesaw.edu/">Housing</a></li> <li><a href="https://financialaid.kennesaw.edu/">Financial Aid</a></li> <li><a href="https://www.kennesaw.edu/degrees-programs/">Degrees, Majors &amp; Programs</a></li> <li><a href="https://registrar.kennesaw.edu/">Registrar</a></li> <li><a href="https://hr.kennesaw.edu/careers.php">Job Opportunities</a></li> </ul> </div> <div> <ul class="link_list"> <li><a href="https://police.kennesaw.edu/">Campus Security</a></li> <li><a href="https://dga.kennesaw.edu/">Global Affairs</a></li> <li><a href="https://diversity.kennesaw.edu/">Diverse &amp; Inclusive Excellence</a></li> <li><a href="https://sustainability.kennesaw.edu/">Sustainability</a></li> <li><a href="https://www.kennesaw.edu/accessibility.php">Accessibility</a></li> </ul> </div> </div> </div> </div> </div> </div> <div class="boilerplate"> <div class="footer_logo"><img src="https://webstatic.kennesaw.edu/_resources/images/template/ksu_horizontal.svg" alt="Kennesaw State University Logo" height="70px"></div> <div class="footer_resources"> <div class="footer_socials"> <div class="section_heading"> <p class="heading is_text_4 is_gold is_hidden_desktop" aria-level="4">Follow KSU</p> </div> <ul class="channels"> <li class="is_gold"> <a href="https://www.facebook.com/KennesawStateUniversity" aria-label="Facebook"> <div> <img src="https://webstatic.kennesaw.edu/_resources/images/template/facebook-f.svg" alt="Facebook Icon" height="30px"> </div> </a> </li> <li class="is_gold"> <a href="https://twitter.com/kennesawstate" aria-label="Twitter"> <div> <img src="https://webstatic.kennesaw.edu/_resources/images/template/twitter.svg" alt="Twitter Icon" height="30px"> </div> </a> </li> <li class="is_gold"> <a href="https://www.linkedin.com/company/kennesaw-state-university" aria-label="LinkedIn"> <div> <img src="https://webstatic.kennesaw.edu/_resources/images/template/linkedin-in.svg" alt="LinkedIn Icon" height="30px"> </div> </a> </li> <li class="is_gold"> <a href="https://instagram.com/kennesawstateuniversity" aria-label="Instagram"> <div> <img src="https://webstatic.kennesaw.edu/_resources/images/template/instagram.svg" alt="Instagram Icon" height="30px"> </div> </a> </li> <li class="is_gold"> <a href="https://www.youtube.com/user/KennesawStatenow" aria-label="YouTube"> <div> <img src="https://webstatic.kennesaw.edu/_resources/images/template/youtube.svg" alt="YouTube Icon" height="30px"> </div> </a> </li> </ul> </div> <p class="ksu_info_mobile"><strong>470-KSU-INFO</strong> (470-578-4636)</p> <p class="copyright"><span id="directedit"> <a id="de" href="https://a.cms.omniupdate.com/11/?skin=kennesaw&amp;account=kennesaw&amp;site=OMNI&amp;action=de&amp;path=/_dev/kb/test/stratcomm/index.pcf">©</a> </span> 2022 Kennesaw State University. All Rights Reserved.</p> <ul class="link_list is_horizontal resources_links"> <li><a href="https://www.kennesaw.edu/privacy-statement.php">Privacy Statement</a></li> <li><a href="https://www.kennesaw.edu/accreditation.php">Accreditation</a></li> <li><a href="https://advisories.kennesaw.edu/">Advisories</a></li> <li><a href="https://www.kennesaw.edu/reporting-hotline.php">Reporting Hotline</a></li> <li><a href="https://www.kennesaw.edu/feedback.php">Feedback</a></li> <li><a href="https://legal.kennesaw.edu/open_records_requests.php">Open Records</a></li> <li><a href="https://gbi.georgia.gov/human-trafficking-notice">Human Trafficking Notice</a></li> <li><a href="https://assistive.usablenet.com/tt/omni.kennesaw.edu/_dev/kb/test/stratcomm/">Text Only</a></li> </ul> </div> </div>';

	
	if(skin == "def"){
		document.querySelector('#header').innerHTML = header;
		document.querySelector('#gold_bar').innerHTML = goldbar;
		document.querySelector('#footer').innerHTML = footer;
		document.querySelector('link[href*="default.css"]').setAttribute('href', 'https://www.kennesaw.edu/_resources/xsl/_dev/kevdev/new.css');
		document.querySelector('head').innerHTML += '<link rel="stylesheet" type="text/css" href="https://webstatic.kennesaw.edu/_resources/css/legacy_snippets.css">';
		document.querySelector('head').innerHTML += '<script src="https://www.kennesaw.edu/_resources/xsl/_dev/kevdev/new.js"></script>';
		document.querySelector('head').innerHTML += '<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700;800&amp;display=swap">';
		$('.secondary_nav').prepend('<div class="secondary_nav_header">'+$('.site_title a').text()+'</div>');
		skinClickEvents();
	}else if(skin == "es"){
		console.log('es skin');
		const esnav = document.querySelector('#high_council_chamber').innerHTML;
		document.querySelector('#header').innerHTML = header;
		document.querySelector('#gold_bar').innerHTML = goldbar;
		document.querySelector('#high_council_chamber').innerHTML = esnav;
		document.querySelector('#footer').innerHTML = footer;
		document.querySelector('link[href*="default.css"]').setAttribute('href', 'https://www.kennesaw.edu/_resources/xsl/_dev/kevdev/new.css');
		document.querySelector('head').innerHTML += '<link rel="stylesheet" type="text/css" href="https://webstatic.kennesaw.edu/_resources/css/legacy_snippets.css">';
		document.querySelector('head').innerHTML += '<script src="https://www.kennesaw.edu/_resources/xsl/_dev/kevdev/new.js"></script>';
		document.querySelector('head').innerHTML += '<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700;800&amp;display=swap">';
		$('.secondary_nav').prepend('<div class="secondary_nav_header">'+$('.site_title a').text()+'</div>');
		skinClickEvents();
	}
}
function skinClickEvents(){
	$('.hamburger_button').click(function(){
        if(window.innerWidth >= 900) {
            if($(this).hasClass('active')){
                if(!$(this).hasClass('active')) 
                    return;
                $(this).removeClass('active');
                $('.nav_wrapper').slideUp();
            }else{
                $(this).addClass('active');
                $('.nav_wrapper').slideDown();     
            }
        }else {
            if($(this).hasClass('active')){
                if(!$(this).hasClass('active')) 
                    return;
                $(this).removeClass('active');
                $('#mobile_high_council_chamber').slideUp();
            }else{
                $(this).addClass('active');
                $('#mobile_high_council_chamber').slideDown();     
            }
        }

    });



    $('.info_for').click(function(){
        if($(this).hasClass('active')){
            if(!$(this).hasClass('active')) 
                return;
            $(this).removeClass('active');
        }else{
            $(this).addClass('active');    
        }
    });



    $('.search_button').click(function(){
        if($(this).siblings('.search').hasClass('active')){
            if(!$(this).siblings('.search').hasClass('active')) 
                return;
                $(this).siblings('.search').removeClass('active');
        }else{
            $(this).siblings('.search').addClass('active');    
        }
    });
}

window.addEventListener('DOMContentLoaded', (event) => {
	const urlParams = new URLSearchParams(window.location.search);
	const skin = urlParams.get('skin');
	if(skin){
		skinCheck(skin);
	}
});