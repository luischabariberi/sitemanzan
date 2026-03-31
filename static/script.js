document.body.classList.add('is-loading');

const revealItems = document.querySelectorAll('.reveal');
const pageLoader = document.querySelector('.page-loader');

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

window.addEventListener('load', () => {
  window.setTimeout(() => {
    pageLoader?.classList.add('is-hidden');
    document.body.classList.remove('is-loading');
  }, 650);
});
