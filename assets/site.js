const search = document.querySelector('#search');
const filterButtons = [...document.querySelectorAll('[data-filter]')];
let selected = new URLSearchParams(location.search).get('category') || 'all';
if (!filterButtons.some(button => button.dataset.filter === selected)) selected = 'all';
function filter() {
  const query = (search?.value || '').trim().toLowerCase();
  let count = 0;
  document.querySelectorAll('.command-group').forEach(group => {
    let visible = 0;
    group.querySelectorAll('.command').forEach(card => {
      card.hidden = !(selected === 'all' || group.id === selected) || !card.textContent.toLowerCase().includes(query);
      if (!card.hidden) visible++;
    });
    group.hidden = visible === 0;
    count += visible;
  });
  filterButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === selected)));
  const empty = document.querySelector('#empty');
  if (empty) empty.hidden = count !== 0;
  const total = document.querySelector('#result-count');
  if (total) total.textContent = `${count} 条指令`;
}
search?.addEventListener('input', filter);
filterButtons.forEach(button => button.addEventListener('click', () => { selected = button.dataset.filter; filter(); }));
if (search) filter();
document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(button.dataset.copy); button.textContent = '已复制'; }
  catch { button.textContent = '请选中指令复制'; }
  setTimeout(() => {button.textContent = '复制';}, 1800);
}));

const mobileMenu = document.querySelector('#mobile-menu');
const menuToggle = document.querySelector('.menu-toggle');
if (mobileMenu && menuToggle) {
  let closing = null;
  const closeMenu = () => {
    if (closing) return closing;
    if (!mobileMenu.open) return Promise.resolve();
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
      mobileMenu.close();
      return Promise.resolve();
    }
    closing = new Promise(resolve => {
      mobileMenu.classList.add('is-closing');
      setTimeout(() => {
        mobileMenu.close();
        mobileMenu.classList.remove('is-closing');
        closing = null;
        resolve();
      }, 240);
    });
    return closing;
  };
  mobileMenu.addEventListener('cancel', event => {
    event.preventDefault();
    closeMenu();
  });
  menuToggle.addEventListener('click', () => {
    if (mobileMenu.open || closing) return;
    mobileMenu.showModal();
    menuToggle.setAttribute('aria-expanded', 'true');
    document.body.classList.add('menu-open');
  });
  mobileMenu.querySelector('.menu-close').addEventListener('click', closeMenu);
  mobileMenu.addEventListener('click', event => {
    const bounds = mobileMenu.getBoundingClientRect();
    if (event.target === mobileMenu && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) closeMenu();
  });
  mobileMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', async event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    await closeMenu();
    location.assign(link.href);
  }));
  mobileMenu.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', async () => {
    await closeMenu();
    document.querySelector('.help-layout')?.scrollIntoView({block: 'start', behavior: 'auto'});
    animateFilteredCommands();
  }));
  mobileMenu.addEventListener('close', () => {
    menuToggle.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('menu-open');
  });
  matchMedia('(max-width: 760px)').addEventListener('change', event => {
    if (!event.matches && mobileMenu.open) closeMenu();
  });
}

const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const revealTargets = [...document.querySelectorAll('.feature, .lower > .panel, .release')];
let revealObserver;
if (!reducedMotion.matches && 'IntersectionObserver' in window) {
  revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.remove('reveal-pending');
      entry.target.classList.add('reveal-visible');
      revealObserver.unobserve(entry.target);
    });
  }, { threshold: 0.08 });
  revealTargets.forEach((element, index) => {
    element.style.setProperty('--reveal-delay', `${(index % 3) * 65}ms`);
    element.classList.add('reveal-pending');
    revealObserver.observe(element);
  });
}
reducedMotion.addEventListener('change', event => {
  if (event.matches) {
    revealObserver?.disconnect();
    revealTargets.forEach(element => element.classList.remove('reveal-pending', 'reveal-visible'));
    document.querySelectorAll('.command').forEach(element => element.getAnimations().forEach(animation => animation.cancel()));
  }
});
function animateFilteredCommands() {
  if (reducedMotion.matches) return;
  // Only animate visible cards near the viewport; long lists remain responsive.
  document.querySelectorAll('.command').forEach(element => {
    element.getAnimations().forEach(animation => animation.cancel());
    if (element.hidden || element.closest('.command-group').hidden) return;
    const bounds = element.getBoundingClientRect();
    if (bounds.top > innerHeight || bounds.bottom < 0) return;
    element.animate([
      {opacity: 0, transform: 'translateY(8px)'},
      {opacity: 1, transform: 'translateY(0)'}
    ], {duration: 240, easing: 'ease-out'});
  });
}
filterButtons.forEach(button => button.addEventListener('click', animateFilteredCommands));
