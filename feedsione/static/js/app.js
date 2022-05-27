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
    clicked_btn = event.target.parentElement;

    if (clicked_btn.getAttribute('data-article-read-status') === 'None' ||
      clicked_btn.getAttribute('data-article-read-status') === 'False') {
        is_read = true;
    }
    else {
      is_read = false;
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
});


// Add to readlater
const add_read_later_btns = document.getElementsByName('add-read-later');
add_read_later_btns.forEach(btn => {
  btn.addEventListener('click', event => {
    clicked_btn = event.target.parentElement;
    if (clicked_btn.getAttribute('data-article-read-later-status') === 'None' ||
      clicked_btn.getAttribute('data-article-read-later-status') === 'False')
    {
      is_read_later = true;
    }
    else {
      is_read_later = false;
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
        console.log(is_read_later);
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
    clicked_btn = event.target.parentElement;
    if (clicked_btn.getAttribute('data-article-save-status') === 'None' ||
      clicked_btn.getAttribute('data-article-save-status') === 'False')
    {
      is_saved = true;
    }
    else {
      is_saved = false;
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
