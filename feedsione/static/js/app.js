var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
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
