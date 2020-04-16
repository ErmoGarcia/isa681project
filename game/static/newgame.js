$(document).ready(function() {

  var socket = io();

  socket.on('new_connection', function(data) {
    $("#connections").append('<li>'+data.msg+'</li>');
  });

  socket.on('new_disconnection', function(data) {
    $("#connections").append('<li>'+data.msg+'</li>');
  });

});
