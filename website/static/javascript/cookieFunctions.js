// these functions come from w3schools
function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  let expires = "expires="+d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  let name = cname + "=";
  let ca = document.cookie.split(';');
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function checkCookie() {
  let user = getCookie("username");
  if (user != "") {
  } else {
    user = prompt("Please create a username:", "");
    if (user != "" && user != null) {
      socket.emit('create_player_request',{
		'username':user,
	        'game_id':game_id
      })
    }
  }
}

socket.on('create_player_response', function(msg) {
	// wait for response before setting username cookie in order to avoid creating duplicate usernames.
	setCookie("username", msg['username'], 1);
	console.log("Recieved create_player_response",msg);
	username = getCookie("username")
});
