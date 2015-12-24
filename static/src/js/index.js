/* global  Materialize, Clipboard, escapeHtml, Notify*/
"use strict";

var host = window.location.hostname; // edit this if needed
var messages = [];
var addressLoaded = false;
var unreadEmails = 0;

function checkSupport() {
  var support = "MozWebSocket" in window ? 'MozWebSocket' : ("WebSocket" in window ? 'WebSocket' : null);
  if (support === null) {
    Materialize.toast('Your browser doesn\'t support Websockets! You won\'t be able to use this service...', 1000000, 'warning-toast');
    return false;
  }

  return true;
}

function checkNotify() {
  if (window.Notification && Notify.needsPermission) {
    Notify.requestPermission();
  }
}

function notifyEmail(email) {
  if (!document.hasFocus() && $("#sendNotifications").is(':checked')) {
    var myNotification = new Notify(email.from, {
      icon: '/img/ios-desktop.png',
      body: email.body,
      timeout: 4
    });

    myNotification.show();

    unreadEmails += 1;
    document.title = 'Mockbox (' + unreadEmails + ' new)';
  }
}

function showRaw(id) {
  $('#rawArea').text(messages[id].raw);
  $('#rawModal').openModal();
}

function getAttachments(id) {
  if (messages[id].attachments.length === 0) {
    return 'No Attachments';
  } else {
    var lengthString = messages[id].attachments.length + ' attachment';
    if (messages[id].attachments.length > 1) {
      lengthString += 's';
    }
    lengthString += ': ';

    var attachmentLinks = messages[id].attachments.map(function(attachment) {
      var dataURI = 'data:' + attachment.type + ';' + attachment.transferEncoding + ',' + attachment.data;
      return '<a href="' + dataURI + '" target="_blank">' + attachment.name + '</a>';
    }).join(', ');

    var attachmentString = lengthString + attachmentLinks;

    return attachmentString;
  }
}

function processDisconnect(event) {
  Materialize.toast('Server connection lost - please refresh', 1000000, 'warning-toast');
}

function processMessage(event) {
  if (!addressLoaded) {
    // first payload is always our config data, a JSON array of [address, port, maxbytes]
    var config = JSON.parse(event.data);
    $('#serverAddress').html(host);
    $('#mailAddress').html(config[0]);
    $('#serverPort').html(config[1]);
    $('#dropSize').html(config[2] / 1000);

    $('#copyLink').attr('data-clipboard-text', config[0]);
    addressLoaded = true;
    return;
  }

  var mailObj = JSON.parse(event.data);
  messages.push(mailObj);
  var messageID = messages.length - 1;

  // do body sanity checking
  if (mailObj.body === null) {
    mailObj.body = '[no body]';
    messages.pop();
    messages.push(mailObj);
    messageID = messages.length - 1;
  }

  var message = '<li class="collection-item avatar">' +
    '<i class="material-icons circle">mail</i>' +
    '<span class="title"><strong>' + escapeHtml(mailObj.subject) + '</strong></span>' +
    '<p>' + escapeHtml(mailObj.from) + ' (at ' + escapeHtml(mailObj.fromIP[0]) + ')<br>' +
    new Date().toLocaleString() + '<br>' +
    getAttachments(messageID) + '</p>' +
    '<a href="#!" onClick="showRaw(' + messageID + ');" class="secondary-content" title="View Raw Message"><i class="material-icons">code</i></a>' +
    '<div class="inlineCode">' + escapeHtml(mailObj.body).replace(/(?:\r\n|\r|\n)/g, '<br />') + '</div>' +
    '</li>';

  $('#noMessages').hide();
  $('#messageCollection').prepend(message);
  notifyEmail(mailObj);
}

function showDemo() {
  $.ajax({
    url: "demo.txt",
    dataType: "text",
    success: function(data) {
      var fakeEvent = {};
      fakeEvent.data = data;
      processMessage(fakeEvent);
    }
  });
}

function clearEmails() {
  messages = [];
  $('#noMessages').show();
  $('#messageCollection').empty();
}

// when we focus in, remove the unread notification
var removeUnread = function(event) {
    unreadEmails = 0;
    document.title = 'Mockbox';
};

document.body.addEventListener('focus', removeUnread, true); //Non-IE
document.body.onfocusin = removeUnread; //IE

window.onbeforeunload = function(e) {
  if (messages.length > 0) {
    return 'You will lose access to the contents of this Mockbox and be unable to use this address again.';
  }
};

if (checkSupport()) {
  var wsProto = window.location.protocol === 'https:' ? 'wss' : 'ws';
  var mailSocket = new WebSocket(wsProto + '://' + host + ':9000');
  mailSocket.onmessage = processMessage;
  mailSocket.onclose = processDisconnect;

  // fire up our copy button (has to be selected to work)
  var clipboard = new Clipboard('#copyLink');

  checkNotify();
}
