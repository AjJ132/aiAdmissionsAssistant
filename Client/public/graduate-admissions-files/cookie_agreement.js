//window.addEventListener('DOMContentLoaded', (event) => {
	
	if(document.cookie.indexOf('ksu_privacy=') == -1 && window.location.hostname.indexOf('kennesaw.edu') != -1) {
		let privacyStyles = document.createElement('style');
		privacyStyles.innerHTML = '#cookie-notification{display:flex;justify-content:center;z-index:9999;position:fixed;bottom:0;background:#f7f7f7;padding:1rem 2rem;font-weight:500;width:calc(100% - 4rem)}#cookie-notification .cookie-links{white-space:nowrap;padding-left:2rem}#cookie-notification a{min-height:24px;display:inline-block;}#cookie-notification .button{transform:translateY(-50%);top:50%;position:relative;margin:0;}@media only screen and (max-width:80.5em){#cookie-notification{flex-wrap:wrap}}';
		let privacyPopup = document.createElement('div');
		privacyPopup.id = 'cookie-notification';
		privacyPopup.setAttribute('role', 'region');
		privacyPopup.setAttribute('aria-label','Cookie Agreement Notification');
		privacyPopup.innerHTML = '<div class="cookie-statement"><p>This website uses cookies. Find out more in our Privacy Notice at <a href="https://www.kennesaw.edu/privacy-statement.php" target="_blank">https://www.kennesaw.edu/privacy-statement.php</a>. Questions or Requests, please complete <a target="_blank" href="https://kennesaw.service-now.com/dpr?id=sc_cat_item&sys_id=bd7c11b5db5b91500149c8cb139619b6">this form</a>.</p></div><div class="cookie-links"><button class="privacy-ok button">OK</button></div>';
		document.body.appendChild(privacyStyles); 
		document.body.appendChild(privacyPopup);
		let agreeButton = document.querySelector('.privacy-ok');
		agreeButton.addEventListener('click', function(e) {
			let currentDate = new Date();
			currentDate.setFullYear(currentDate.getFullYear()+1);
			document.cookie = "ksu_privacy=accepted; domain=kennesaw.edu; path=/; secure=true; expires="+currentDate.toUTCString()+"; SameSite=Lax;";
			privacyPopup.parentNode.removeChild(privacyPopup); 
		});
	}
//});