$(document).ready(function() {
  var socket = io();


  $('#phase').hide();
  $('#mus').hide();
  $('#mus').click(function(){
      $('#mus').hide();
      socket.emit('mus');
  });


  // Server event sent for each connection
  socket.on('new_connection', function(data){
    $('#connections').append('<div class="alert alert-success" role="alert">'+data.connection+'</div>');
  });
  // Server event sent for each disconnection
  socket.on('new_disconnection', function(data){
    $('#connections').append('<div class="alert alert-warning" role="alert">'+data.disconnection+'</div>');
  });

  // Server event sent when a player remains disconnected after one minute
  socket.on('game_over', function(data){
    $('#gameboard').append('<div class="alert alert-warning" role="alert">'+data.game_over+'</div>');
  });


  // Old shit
  socket.on('new_round', function(data){
      $('#connections').hide();
      $('#phase').text("Phase: "+data.phase);
      $('#phase').show();
  });
  socket.on('new_turn', function(data){
      $('#mus').show();
  });
});
