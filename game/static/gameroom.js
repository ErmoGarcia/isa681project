$(document).ready(function() {
  var socket = io();
  var card1 = [];
  var card2 = [];
  var card3 = [];
  var card4 = [];
  var cardsSet = new Set();
  var arrayMus = [];

  var card1OnClick = false;
  var card2OnClick = false;
  var card3OnClick = false;
  var card4OnClick = false;

  var alreadyMus = false;
  var alreadyNoMus = false;
  var alreadyPass = false;


  function toCard(number, palo){

    card = "/static/cards/" + number.toString() + palo +'.jpg';
    return card;
  }

  function bid(){

  }

  //Visilibility Environment
  $('#mus').css('visibility', 'visible');
  $('#noMus').css('visibility', 'visible');
  $('#pass').css('visibility', 'visible');
  $('#envido').css('visibility', 'visible');
  $('#myForm').css('visibility', 'visible');


  
  //On click reponses
  $('#card1').click(function(){
    if(card1OnClick == false){
      $('#card1').attr('src',"/static/cards/Reverse.jpg");
      cardsSet.add(card1);
      card1OnClick = true;
    }
    else{
      var card = toCard(card1[0],card1[1]);
      $('#card1').attr('src',card);
      cardsSet.delete(card1);
      card1OnClick = false;
    }
  });

  $('#card2').click(function(){
    if(card2OnClick == false){
      $('#card2').attr('src',"/static/cards/Reverse.jpg");
      cardsSet.add(card2);
      card2OnClick = true;
    }
    else{
      var card = toCard(card2[0],card2[1]);
      $('#card2').attr('src',card);
      cardsSet.delete(card2);
      card2OnClick = false;
    }
  });

  $('#card3').click(function(){
    if(card3OnClick == false){
      $('#card3').attr('src',"/static/cards/Reverse.jpg");
      cardsSet.add(card3);
      card3OnClick = true;
    }
    else{
      var card = toCard(card3[0],card3[1]);
      $('#card3').attr('src',card);
      cardsSet.delete(card3);
      card3OnClick = false;
    }
  });

  $('#card4').click(function(){
    if(card4OnClick == false){
      $('#card4').attr('src',"/static/cards/Reverse.jpg");
      cardsSet.add(card4);
      card4OnClick = true;
    }
    else{
      var card = toCard(card4[0],card4[1]);
      $('#card4').attr('src',card);
      cardsSet.delete(card4);
      card4OnClick = false;
    }
  });


  $('#mus').click(function(){
      $('#mus').hide();
      $('#noMus').hide();
      arrayMus = Array.from(cardsSet);
      var myJson = JSON.stringify(arrayMus);
      jsonToSend = '{"cutMus": ' + 'false, "discards": "'+ myJson + '}';
      socket.emit('client_mus_turn', jsonToSend);
  });

  $('#noMus').click(function(){
      $('#noMus').hide();
      $('#mus').hide();
      var myJson = JSON.stringify();
      jsonToSend = '{"cutMus": ' + 'true, "discards": ""';
      socket.emit('client_mus_turn',jsonToSend);
  });

  $('#pass').click(function(){
      arrayMus = Array.from(cardsSet);
      var myJson = JSON.stringify(arrayMus);
      jsonToSend = '{"cutMus": ' + 'false, "discards": "'+ myJson + '}';
      socket.emit(myJson);
  });

    socket.on('start_game', function(data){
      $('#blueTeam').text('Blue Team Points: ' + data.scoreBlue);
      $('#redTeam').text('Red Team Points: ' + data.scoreRed);
      var i = data.player_number;
      $('#player1').append(data.players[i]);
      if(i==3){
        $('#player1').css('color', 'red');        
        $('#player2').text(data.players[0]);
        $('#player2').css('color', 'blue');      
        $('#player3').text(data.players[1]);
        $('#player3').css('color', 'red');      
        $('#player4').text(data.players[2]);
        $('#player4').css('color', 'blue');      

      }
      else if(i==2){
        $('#player1').css('color', 'blue');      
        $('#player2').text(data.players[3]);
        $('#player2').css('color', 'red');      
        $('#player3').text(data.players[0]);
        $('#player3').css('color', 'blue');      
        $('#player4').text(data.players[1]);
        $('#player4').css('color', 'red');      
      }
      else if(i==1){
        $('#player1').css('color', 'red');      
        $('#player2').text(data.players[2]);
        $('#player2').css('color', 'blue');      
        $('#player3').text(data.players[3]);
        $('#player3').css('color', 'red');      
        $('#player4').text(data.players[1]);
        $('#player4').css('color', 'blue');      
      }
      else {
        $('#player1').css('color', 'blue');      
        $('#player2').text(data.players[1]);
        $('#player2').css('color', 'red');      
        $('#player3').text(data.players[2]);
        $('#player3').css('color', 'blue');      
        $('#player4').text(data.players[3]);
        $('#player4').css('color', 'red');      
      }

      $('#myHeader').text('');
    });

  socket.on('message', function(data){
      $('#messages').append(data);
  });

  socket.on('mus_turn', function(data){
      card1OnClick = false;
      card2OnClick = false;
      card3OnClick = false;
      card4OnClick = false;
        $('#mus').css('visibility', 'visible');
        $('#noMus').css('visibility', 'visible');
        $('#pass').css('visibility', 'visible');
        $('#myForm').css('visibility', 'visible');
      data.cards.forEach(function(value,index){
        var number=value[0];
        var palo;
        var card;
        if (value[1].localeCompare("oros")==0){
          palo = 'o';
        }
        else if (value[1].localeCompare("espadas")==0) {
          palo = 'e';
        }
        else if (value[1].localeCompare("bastos")==0) {
          palo = 'b';
        }
        else {
          palo = 'c';
        }
        if(number<10){
          card = '0' + number.toString() + palo +'.jpg';
        }
        else{
          card = number.toString() + palo +'.jpg';
        }

        var src = "/static/cards/" + card;

        if(index ==0){
          $('#card1').attr('src', src);
          card1[0] = number;
          card1[1] = palo;
        }
        else if(index ==1){
          $('#card2').attr('src', src);
          card2[0] = number;
          card2[1] = palo;
        }
        else if(index ==2){
          $('#card3').attr('src', src);
          card3[0] = number;
          card3[1] = palo;
        }
        else{
          $('#card4').attr('src', src);
          card4[0] = number;
          card4[1] = palo;
        }
      });
    });

  socket.on('game_turn', function(data){
      $('#phase').text("Phase: "+data.phase);
      $('#mus').hide();
      $('#noMus').hide();

  });


  socket.on('new_connection', function(data){
    $('#messages').append('<li>'+data.connection+'</li>');
  });
  socket.on('new_disconnection', function(data){
    $('#messages').append('<li>'+data.disconnection+'</li>');
  });
  socket.on('game_over', function(data){
    $('#messages').append('<li>'+data.game_over+'</li>');
  });



  socket.on('new_round', function(data){
      $('#connections').hide();
      $('#phase').text("Phase: "+data.phase)
  });

  socket.on('new_turn', function(data){
      $('#mus').show()

  });

});
