/* global  Materialize, Clipboard */
"use strict";

var host = window.location.hostname; // edit this if needed
var messages = [];
var addressLoaded = false;

function checkSupport() {
  var support = "MozWebSocket" in window ? 'MozWebSocket' : ("WebSocket" in window ? 'WebSocket' : null);
  if (support === null) {
    Materialize.toast('Your browser doesn\'t support Websockets! You won\'t be able to use this service...', 1000000, 'warning-toast');
    return false;
  }

  return true;
}

function processDisconnect(event) {
  Materialize.toast('Server connection lost - please refresh', 1000000, 'warning-toast');
}

function processMessage(event) {
  if(!addressLoaded){
    // first payload is always our config data, a JSON array of [address, port]
    var config = JSON.parse(event.data);
    $('#serverAddess').html(host);
    $('#mailAddress').html(config[0]);
    $('#serverPort').html(config[1]);

    $('#copyLink').attr('data-clipboard-text', config[0]);
    addressLoaded = true;
    return;
  }

  var mailObj = JSON.parse(event.data);
  messages.push(mailObj);

  $('#noMessages').hide();

  var message = '<li class="collection-item avatar">' +
    '<i class="material-icons circle">mail</i>' +
    '<span class="title"><strong>' + mailObj.subject + '</strong></span>' +
    '<p>' + mailObj.from + '(at ' + mailObj.fromIP[0] + ')<br>' + new Date().toLocaleString() + '</p>' +
    '<a href="#!" class="secondary-content" title="View Raw Message"><i class="material-icons">code</i></a>' +
    '</li>';

  $('#messageCollection').prepend(message);
}

if (checkSupport()) {
  var mailSocket = new WebSocket('ws://' + host + ':9000');
  mailSocket.onmessage = processMessage;
  mailSocket.onclose = processDisconnect;
}

// fire up our copy button (has to be selected to work)
var clipboard = new Clipboard('#copyLink');
