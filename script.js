const menuBtn = document.getElementById('menuBtn');
const navLinks = document.getElementById('navLinks');

menuBtn.addEventListener('click', () => navLinks.classList.toggle('open'));
document.querySelectorAll('.nav-links a').forEach(link => {
  link.addEventListener('click', () => navLinks.classList.remove('open'));
});

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

const phrases = ['data pipelines.', 'AWS data systems.', 'ETL workflows.', 'analytics-ready datasets.'];
const typedText = document.getElementById('typedText');
let phraseIndex = 0;
let charIndex = phrases[0].length;
let deleting = true;

function typeEffect() {
  const phrase = phrases[phraseIndex];
  if (deleting) {
    charIndex--;
    typedText.textContent = phrase.slice(0, charIndex);
    if (charIndex === 0) {
      deleting = false;
      phraseIndex = (phraseIndex + 1) % phrases.length;
      setTimeout(typeEffect, 350);
      return;
    }
  } else {
    charIndex++;
    typedText.textContent = phrases[phraseIndex].slice(0, charIndex);
    if (charIndex === phrases[phraseIndex].length) {
      deleting = true;
      setTimeout(typeEffect, 1400);
      return;
    }
  }
  setTimeout(typeEffect, deleting ? 45 : 75);
}
setTimeout(typeEffect, 1200);

const cursorGlow = document.getElementById('cursorGlow');
window.addEventListener('mousemove', (event) => {
  cursorGlow.style.left = `${event.clientX}px`;
  cursorGlow.style.top = `${event.clientY}px`;
});

const sections = document.querySelectorAll('section[id]');
const navItems = document.querySelectorAll('.nav-links a');

window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(section => {
    if (scrollY >= section.offsetTop - 180) current = section.id;
  });
  navItems.forEach(item => {
    item.style.color = item.getAttribute('href') === `#${current}` ? '#6ee7ff' : '';
  });
});
