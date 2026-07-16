document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.panel-card');
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 80}ms`;
    card.classList.add('fade-in');
  });
});
