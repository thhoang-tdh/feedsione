window.addEventListener("load", function() {
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




/**************************************************
 *              TOP BAR NAV
**************************************************/
function sort_newest_first() {
  var url = new URL(window.location.href.toString());
  url.searchParams.set('o', '-date_published');
  window.location = url;
  return false;
}

function sort_oldest_first() {
  var url = new URL(window.location.href.toString());
  url.searchParams.set('o', 'date_published');
  window.location = url;
  return false;
}

function handle_onchange_unread() {
  var unread_checkbox = document.getElementById('unread_checkbox').checked;

  var url = new URL(window.location.href.toString());
  if (unread_checkbox === true) {
    url.searchParams.set('unread', 1);
  } else {
    url.searchParams.set('unread', 0);
  }
  window.location = url;
  return false;
}





/**
 *  ARTICLE TITLE
 * TODO: right click to article origin url
 */
// const article_title = document.getElementsByName('article-title');
// article_title.forEach(a => {
//   a.addEventListener('mousedown', event => {

//     if (event.button == 0) {
//       console.log('left')
//       event.preventDefault();

//       const url = event.target.getAttribute('data-article-url');
//       console.log(url);
//       console.log(window.location.href.toString());
//     }

//     // e.preventDefault();
//     // const url = new URL(e.target.getAttribute('data-article-url'));
//     // window.location = url;
//   })
//   return false;
// });


/**************************************************
 *              MARK ARTICLES
**************************************************/
function MarkReadFormSubmit(n) {
  // mark a list of articles
  document.mark_read_form.day.value = n;
  console.log(document.mark_read_form.day.value);
}


// Mark article
const mark_as_read_btns = document.getElementsByName('mark-as-read-article');
mark_as_read_btns.forEach(btn => {
  btn.addEventListener('click', event => {
    clicked_btn = event.target;
    if (clicked_btn.tagName.toLowerCase() === 'i') {
      clicked_btn = clicked_btn.parentElement;
    }

    if (clicked_btn.getAttribute('data-article-read-status') === 'True') {
      is_read = false;
    } else {
      is_read = true;
    }

    const data = {
      'article_slug': clicked_btn.getAttribute('data-article-slug'),
      'is_read': is_read,
    };


    $.ajax({
      type: 'POST',
      url: '/article/mark-as-read/',
      beforeSend: function(xhr) {
        xhr.setRequestHeader('X-CSRFToken', CSRF_TOKEN);
      },
      data: data,
      success: function (data) {
        if (is_read === false) {
          clicked_btn.innerHTML = '<i class="bi bi-circle"></i>';
          clicked_btn.setAttribute('data-article-read-status', 'False');
        } else {
          clicked_btn.innerHTML = '<i class="bi bi-check2-circle"></i>';
          clicked_btn.setAttribute('data-article-read-status', 'True');
        }
      },
      error: function (response) {
        console.log(response);
      }
    });
  })
  return true;
});


// Add to readlater
const add_read_later_btns = document.getElementsByName('add-read-later');
add_read_later_btns.forEach(btn => {
  btn.addEventListener('click', event => {
    clicked_btn = event.target;
    if (clicked_btn.tagName.toLowerCase() === 'i') {
      clicked_btn = clicked_btn.parentElement;
    }

    if (clicked_btn.getAttribute('data-article-read-later-status') === 'True') {
      is_read_later = false;
    } else {
      is_read_later = true;
    }

    const data = {
      'article_slug': clicked_btn.getAttribute('data-article-slug'),
      'is_read_later': is_read_later
    };

    $.ajax({
      type: 'POST',
      url: '/article/read-later/',
      beforeSend: function(xhr) {
        xhr.setRequestHeader('X-CSRFToken', CSRF_TOKEN);
      },
      data: data,
      success: function (data) {
        if (is_read_later === false) {
          clicked_btn.innerHTML = '<i class="bi bi-bookmark"></i>';
          clicked_btn.setAttribute('data-article-read-later-status', 'False');
        } else {
          clicked_btn.innerHTML = '<i class="bi bi-bookmark-fill"></i>';
          clicked_btn.setAttribute('data-article-read-later-status', 'True');
        }
      },
      error: function (response) {
        console.log(response);
      }
    });

  })
});


// Save article
const save_article_btns = document.getElementsByName('save-article');
save_article_btns.forEach(btn => {
  btn.addEventListener('click', event => {
    clicked_btn = event.target;
    if (clicked_btn.tagName.toLowerCase() === 'i') {
      clicked_btn = clicked_btn.parentElement;
    }

    if (clicked_btn.getAttribute('data-article-save-status') === 'True') {
      is_saved = false;
    } else {
      is_saved = true;
    }

    const data = {
      'article_slug': clicked_btn.getAttribute('data-article-slug'),
      'is_saved': is_saved
    };

    $.ajax({
      type: 'POST',
      url: '/article/save/',
      beforeSend: function(xhr) {
        xhr.setRequestHeader('X-CSRFToken', CSRF_TOKEN);
      },
      data: data,
      success: function (data) {
        if (is_saved === false) {
          clicked_btn.innerHTML = '<i class="bi bi-star"></i>';
          clicked_btn.setAttribute('data-article-save-status', 'False');
        } else {
          clicked_btn.innerHTML = '<i class="bi bi-star-fill"></i>';
          clicked_btn.setAttribute('data-article-save-status', 'True');
        }
      },
      error: function (response) {
        console.log(response);
      }
    });

  })
});


/**************************************************
 *           FOLLOW/UNFOLLOW
**************************************************/
const feed_subscription_btn = document.getElementsByName('feed-subscription');
feed_subscription_btn.forEach(btn => {
  btn.addEventListener('click', event => {
    var clicked_btn = event.target;
    if (clicked_btn.tagName.toLowerCase() === 'div') {
      clicked_btn = clicked_btn.parentElement;
    }
    if (clicked_btn.tagName.toLowerCase() === 'span') {
      clicked_btn = clicked_btn.parentElement.parentElement;
    }

    const data = {
      'feed_slug': clicked_btn.getAttribute('data-slug-feed'),
      'folder_slug': clicked_btn.getAttribute('data-slug-folder')
    }

    let url = '/feed/unfollow/';
    let action = 'unfollow';
    if (clicked_btn.getAttribute('data-subscription-action') === 'add') {
      url = '/feed/follow/';
      action = 'follow';
    }

    $.ajax({
      type: 'POST',
      url: url,
      beforeSend: function(xhr) {
        xhr.setRequestHeader('X-CSRFToken', CSRF_TOKEN);
      },
      data: data,
      success: function (res) {
        if (action === 'unfollow') {
          clicked_btn.querySelector('.btn-action').innerHTML = '<span class="badge bg-primary opacity-50 ms-5">ADD</span>';
          clicked_btn.setAttribute('data-subscription-action', 'add');
        } else {
          clicked_btn.querySelector('.btn-action').innerHTML = '<span class="badge bg-warning opacity-50 ms-5">REMOVE</span>';
          clicked_btn.setAttribute('data-subscription-action', 'remove');
        }

        var ul = clicked_btn.parentElement.parentElement;
        var children = ul.children;
        var num_followed = 0;
        for(var i=0; i<children.length - 1; i++){
          var child = children[i].children[0];
          if (child.getAttribute('data-subscription-action') === 'remove') {
            num_followed += 1;
          }
        }

        var toggler = ul.previousElementSibling;
        if (num_followed === 0) {
          toggler.classList.remove('btn-outline-secondary');
          toggler.classList.add('btn-outline-primary');
          toggler.innerHTML = '<span>FOLLOW</span>';
        } else {
          toggler.classList.remove('btn-outline-primary');
          toggler.classList.add('btn-outline-secondary');
          toggler.innerHTML = '<span>EDIT</span>';
        }

      },
      error: function (res) {
        console.log(res);
      }

    });


  });
});