var sidenav_elem = document.querySelector('.sidenav');
var instance = M.Sidenav.init(sidenav_elem, {
  draggable: true,
});
var fab_elem = document.querySelector('.fixed-action-btn');
if (fab_elem) {
  var fab_instance = M.FloatingActionButton.init(fab_elem);
}
var dropdown_menu_elem = document.querySelector('.dropdown-trigger');
if (dropdown_menu_elem) {
  var dropdown_instance = M.Dropdown.init(dropdown_menu_elem);
}

var messages_elem = document.querySelectorAll('.server_messages > li');
if (messages_elem.length > 0) {
  for (var message_elem of messages_elem) {
    M.toast({html: message_elem.textContent.trim()});
  }
}
