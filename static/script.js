document.body.classList.add('is-loading');

const revealItems = document.querySelectorAll('.reveal');
const pageLoader = document.querySelector('.page-loader');
const slideshowItems = document.querySelectorAll('.gallery-slideshow');

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      }
    });
  },
  {
    threshold: 0.15,
    rootMargin: '0px 0px -40px 0px',
  }
);

revealItems.forEach((item) => revealObserver.observe(item));

slideshowItems.forEach((item) => {
  const images = JSON.parse(item.dataset.galleryImages || '[]');
  if (images.length < 2) {
    return;
  }

  let currentIndex = 0;

  window.setInterval(() => {
    currentIndex = (currentIndex + 1) % images.length;
    item.style.opacity = '0.2';

    window.setTimeout(() => {
      item.src = images[currentIndex];
      item.style.opacity = '1';
    }, 220);
  }, 3000);
});

window.addEventListener('load', () => {
  window.setTimeout(() => {
    pageLoader?.classList.add('is-hidden');
    document.body.classList.remove('is-loading');
  }, 650);
});
