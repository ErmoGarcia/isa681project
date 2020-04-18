$(document).ready(function() {

  var socket = io();

  $('#create').click(function() {

    socket.emit('new game');

    $('button').hide();
    $('#msg').html('New game created by {{ current_user.username }}');

  });

  $('#join').click(function() {

    socket.emit('get players');

    $('button').hide();

  });

  socket.on('player', function(data) {
  });

});
