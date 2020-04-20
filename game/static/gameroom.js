$(document).ready(function() {
  var socket = io();
  socket.on('new_connection', function(data){
    $('#connections').append('<li>'+data.connection+'</li>');
  });
  socket.on('new_disconnection', function(data){
    $('#connections').append('<li>'+data.disconnection+'</li>');
  });
  socket.on('game_over', function(data){
    $('#connections').append('<li>'+data.game_over+'</li>');
  });
});
