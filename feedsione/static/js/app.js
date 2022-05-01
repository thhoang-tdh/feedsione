window.addEventListener("load", function() {
  console.log("page loaded");
  const nlfeeds = document.getElementsByClassName('nl-feed');
  for (let i = 0; i < nlfeeds.length; i++) {
    if (nlfeeds[i].classList.contains('leftNavList-active')) {
      expand_tree(nlfeeds[i].parentElement.id.replace('child_', ''));
      break;
    }
  }
})

function expand_tree(id) {
  // alert(id);
  const child = document.getElementById('child_' + id);
  const icon = document.getElementById('plus_' + id);

  if (child.className.includes('visually-hidden')) {
    child.classList.remove('visually-hidden');
    icon.classList.add('rotate90');
  } else {
    child.classList.add('visually-hidden');
    icon.classList.remove('rotate90');
  }

}

function expand_nav_list() {
  const leftNavList = document.getElementById('leftNavList');
  const contentContainer = document.getElementById('contentContainer');

  if (leftNavList.className.includes('visually-hidden')) {
    leftNavList.classList.remove('visually-hidden');
    contentContainer.classList.remove('content-w-list-hide');
    contentContainer.classList.add('content-w-list-show');
  } else {
    leftNavList.classList.add('visually-hidden');
    contentContainer.classList.remove('content-w-list-show');
    contentContainer.classList.add('content-w-list-hide');
  }

}



function get_article_detail(url) {

  fetch(url, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
    credentials: 'same-origin',
  })
  .then(response => {
    if (response.status === 403  && response.headers.get("refresh_url")) {
      // Perhaps do something fancier than alert()
      alert("You have to refresh your authentication.")
      // Redirect the user out of this application.
      document.location.href = response.headers.get("refresh_url");
    } else {
      response.json()
      .then(stuff => {
        console.log(stuff);
      })
    }
  });
}




function toggle_article_detail(id) {
  var url = '/article/id/' + id;

  console.log(url);

  // fetch(url, {
  //   headers: {
  //     "X-Requested-With": "XMLHttpRequest",

  //   }
  // })






  // fetch(url, {
  //   headers: {
  //     "X-Requested-With": "XMLHttpRequest",
  //   },
  //   credentials: 'same-origin',
  // })
  // .then(response => {
  //   if (response.status === 403  && response.headers.get("refresh_url")) {
  //     // Perhaps do something fancier than alert()
  //     alert("You have to refresh your authentication.")
  //     // Redirect the user out of this application.
  //     document.location.href = response.headers.get("refresh_url");
  //   } else {
  //     response.json()
  //     .then(stuff => {
  //       console.log(stuff);
  //     })
  //   }
  // });
}


