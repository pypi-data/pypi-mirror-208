{% load static %}

importScripts(
  'https://storage.googleapis.com/workbox-cdn/releases/6.4.1/workbox-sw.js'
);

self.addEventListener("install", event => {
  console.log("installing service worker")
});

self.addEventListener('activate', event => {
  console.log("activating service worker")
});


function buildNotification(comment, ...comments) {
  let allComments = [comment];
  for (let i = 0; i < comments.length; i++) {
    let subComments = comments[i];
    for (let j = 0; j < subComments.length; j++) {
      let subComment = subComments[j];
      if (subComment.data.data.id == comment.data.data.id) {
        allComments.push(comment);
        allComments = allComments.slice(1);
      } else {
        allComments.push(subComment);
      }
    }
  }
  if (allComments.length == 1) {
    return allComments[0]
  }
  let currentUser = "";
  let response_urls = [];
  let groupedComments = [];
  for (let i = allComments.length - 1; i >= 0; i--) {
    let currentComment = allComments[i];
    if (currentUser != currentComment.data.data.user) {
      currentUser = currentComment.data.data.user;
      groupedComments.push({user: currentUser, comments: []})
      let dateCreated = new Date(currentComment.data.data.date_created);
    }
    groupedComments[groupedComments.length-1].comments.push(currentComment)
    if (currentComment.data.response_url) {
      response_urls.push(currentComment.data.response_url);
    }
  }

  body = 'Latest comments:'
  for (let i = groupedComments.length - 1; i >= 0; i--) {
    let userComments = groupedComments[i].comments
    let dateCreated = new Date(userComments[userComments.length-1].data.data.date_created);
    body += `\n${groupedComments[i].user} at ${dateCreated.toLocaleTimeString()}`;
    for (let j = 0; j < userComments.length; j++) {
      body += `\n    ${userComments[j].body}`;
    }
  }

  let notificationData = {
    body: body,
    icon: comment.icon ? comment.icon : "{{ root_url }}{% static 'images/logo_160x160.png' %}",
    tag: comment.tag,
    requireInteraction: true,
    renotify: true,
    actions: comment.actions,
    data: {
      url: comment.data.url,
      comments: allComments,
      response_urls: response_urls,
      subject: `${allComments.length} new comments in #${comment.data.data.channel.channel_id}: ${comment.data.data.channel.display_name}`
    }
  }
  return notificationData;
}

function runningInAndroidChrome() {
  // check if we are running in android chrome
  return navigator.userAgent.match(/(chrome)/ig) && navigator.userAgent.match(/(android)/ig)
}

function runningInChrome() {
  // check if we are running in android chrome
  return navigator.userAgent.match(/(chrome)/ig)
}

self.addEventListener('push', function(event) {

  var payload = event.data.text();

  let data = JSON.parse(payload);

  let tag = data.channel ? "channel-" + data.channel.channel_id : data.id;
  let icon = data.icon ? data.icon : "{{ root_url }}{% static 'images/logo_160x160.png' %}";

  if ((!data.unread) || (data.action == "delete")) {

    event.waitUntil(
      self.registration.getNotifications().then(
        function(allNotifications){
          return self.registration.getNotifications({tag: tag}).then(
            function(notifications){
              if (allNotifications.length > notifications.length) {
                notifications.forEach(n => n.close());
                let notification = allNotifications.filter(n => n.tag != tag)[0]
                notification.data.notificationData.renotify = false;
                return self.registration.showNotification(
                  notification.data.subject, notification.data.notificationData
                )
              } else if (notifications.length > 0) {
                if (runningInAndroidChrome()) {
                  // keep the notification to avoid unwanted popups
                  let notification = notifications[0];
                  notifications.forEach(n => n.close());
                  notification.data.notificationData.tag = "dismiss";
                  notification.data.notificationData.renotify = false;
                  notification.data.notificationData.silent = true;
                  return self.registration.showNotification(
                    notification.data.subject, notification.data.notificationData
                  )
                } else {
                  notifications.forEach(n => n.close());
                }
              } else {
                if (runningInAndroidChrome()) {
                  return self.registration.showNotification(
                    "", {tag: "dismiss", icon: icon, silent: true}
                  )
                }
              }
            }
          )
        }
      )
    )
  } else if (data.unread) {
    // Retrieve a list of the clients of this service worker.
    event.waitUntil(
      self.clients.matchAll().then(function(clientList) {
        // Check if there's at least one focused client.

        var notificationData = {
          body: data.body,
          icon: icon,
          tag: tag,
          requireInteraction: true,
          actions: [],
          renotify: true,
          data: {
            url: data.url ? data.url: self.location.origin,
            subject: data.subject,
            data: data
          }
        }
        notificationData.data.notificationData = notificationData;
        if (data.response_url) {
          notificationData.actions.push({
            action: "markAsRead",
            title: "Mark as read"
          });
          notificationData.actions.push({
            action: "delete",
            title: "Delete notification"
          });
          notificationData.data.response_url = data.response_url;
        }

        var focused = clientList.some(function(client) {
          return client.focused;
        });

        if (!focused) {
          if ((data.action == "create") || (data.action == "update")) {
            return self.registration.getNotifications({tag: notificationData.tag}).then(
              (notifications) => {
                notificationData = buildNotification(
                  notificationData, ...notifications.map(n => n.data.comments ? n.data.comments.map(c => c.data.notificationData) : [n.data.notificationData])
                )
                if ((!runningInAndroidChrome()) && (runningInChrome())) {
                  // close the notifications because the actions in desktop
                  // chrome will not appear again otherwise
                  notifications.forEach(n => n.close());
                }
                return self.registration.showNotification(
                  notificationData.data.subject, notificationData
                ).then(
                  () => self.registration.getNotifications({tag: "dismiss"})
                ).then(
                  notifications => notifications.forEach(n => n.close())
                )
              }
            )
          }
        }
      })
    )
  }
});

// Register event listener for the 'notificationclick' event.
self.addEventListener('notificationclick', function(event) {
  if (event.action) {
    var body = {};
    var method = "PATCH";
    if (event.action == "markAsRead") {
      body.unread = false;
    } else if (event.action == "delete") {
      method = "DELETE";
    }
    if (event.notification.data.response_urls) {
      event.waitUntil(
        Promise.all(
          event.notification.data.response_urls.map(
            uri => fetch(uri, {
              method: method,
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(body)
            })
          )
        ).then((response) => {
          event.notification.close();
        }).catch(error => {
          console.error(error);
        })
      )
    } else {
      event.waitUntil(
        fetch(event.notification.data.response_url, {
          method: method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(body)
        }).then((response) => {
          event.notification.close();
        }).catch(error => {
          console.error(error);
        })
      )
    }
  } else {
    event.waitUntil(
      // Retrieve a list of the clients of this service worker.
      self.clients.matchAll({type: "window"}).then(function(clientList) {
        // If there is at least one client, focus it.
        if (clientList.length > 0) {
          event.notification.close();
          clientList[0].navigate(event.notification.data.url);
          return clientList[0].focus();
        }

        // Otherwise, open a new page.
        return self.clients.openWindow(event.notification.data.url);
      })
    );
  }
});

{% include "e2ee/serviceworker_routes.js" %}
