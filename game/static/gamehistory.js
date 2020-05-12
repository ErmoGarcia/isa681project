$(document).ready(function() {
    var socket = io('/history', {transport: ['websocket']});

  //Visilibility Environment
  $('#next').css('visibility', 'visible');
  $('#prev').css('visibility', 'visible');


  $('#next').click(function(){
    $('#messages').text('');
    socket.emit('next', {});
  });

  $('#prev').click(function(){
      $('#messages').text('');
      socket.emit('prev', {});
  });

    socket.on('move', function(data){
      $('#blueTeam').text('Blue Team Points: ' + data.scoreBlue);
      $('#redTeam').text('Red Team Points: ' + data.scoreRed);

      $('#player1').text(data.players[0]);
      $('#player2').text(data.players[1]);
      $('#player3').text(data.players[2]);
      $('#player4').text(data.players[3]);

      $('#player1').css('color', 'blue');
      $('#player2').css('color', 'red');
      $('#player3').css('color', 'blue');
      $('#player4').css('color', 'red');

      $('#myHeader').text('');

      $('#messages').append('<br>'+data.message);

      $('#phase').text("Phase: "+data.phase);

      data.cards[0].forEach(function(value, index){
        var src = "/static/cards/" + value;

        if(index ==0){
          $('#card1').attr('src', src);
        }
        else if(index ==1){
          $('#card2').attr('src', src);
        }
        else if(index ==2){
          $('#card3').attr('src', src);
        }
        else{
          $('#card4').attr('src', src);
        }
      })

      data.cards[1].forEach(function(value, index){
        var src = "/static/cards/" + value;

        if(index ==0){
          $('#card5').attr('src', src);
        }
        else if(index ==1){
          $('#card6').attr('src', src);
        }
        else if(index ==2){
          $('#card7').attr('src', src);
        }
        else{
          $('#card8').attr('src', src);
        }
      })

      data.cards[2].forEach(function(value, index){
        var src = "/static/cards/" + value;

        if(index ==0){
          $('#card9').attr('src', src);
        }
        else if(index ==1){
          $('#card10').attr('src', src);
        }
        else if(index ==2){
          $('#card11').attr('src', src);
        }
        else{
          $('#card12').attr('src', src);
        }
      })

      data.cards[3].forEach(function(value, index){
        var src = "/static/cards/" + value;

        if(index ==0){
          $('#card13').attr('src', src);
        }
        else if(index ==1){
          $('#card14').attr('src', src);
        }
        else if(index ==2){
          $('#card15').attr('src', src);
        }
        else{
          $('#card16').attr('src', src);
        }
      })
    });
});
