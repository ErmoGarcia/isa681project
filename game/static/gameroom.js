$(document).ready(function() {
  var socket = io();

  $('#mus').hide()
  $('#mus').click(function(){
      $('#mus').hide();
      socket.emit('mus');
  });

  socket.on('new_connection', function(data){
    $('#connections').append('<li>'+data.connection+'</li>');
  });
  socket.on('new_disconnection', function(data){
    $('#connections').append('<li>'+data.disconnection+'</li>');
  });
  socket.on('game_over', function(data){
    $('#connections').append('<li>'+data.game_over+'</li>');
  });


  socket.on('new_round', function(data){
      $('#connections').hide();
      $('#phase').text("Phase: "+data.phase)
  });
  socket.on('new_turn', function(data){
      $('#mus').show()
  });
});
