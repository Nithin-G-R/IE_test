function scrollPage() {
  if (window.scrollY === 0) {
    // User is at the top, scroll down
    window.scrollTo({
      top: document.body.offsetHeight,
      behavior: 'smooth'
    });
  } else {
    // User is at the bottom, scroll to top
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
}

window.addEventListener('scroll', function() {
  var scrollButton = document.getElementById('goTop-btn');
  if (window.scrollY > 0) {
      scrollButton.style.display = 'block';
    if ((window.innerHeight + window.scrollY) === document.body.offsetHeight) {
        scrollButton.textContent = 'Go Top';
    }

  } else {
    scrollButton.style.display = 'none';
  }
});