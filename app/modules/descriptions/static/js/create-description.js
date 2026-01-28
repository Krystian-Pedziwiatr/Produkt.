document.addEventListener('DOMContentLoaded', () => {
  const featuresGrid = document.querySelector('.features-grid');
  const items = Array.from(featuresGrid.children);
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');

  let currentIndex = 0;
  let itemWidth = items[0].offsetWidth; // realna szerokość jednego kafelka
  let visibleItems = Math.floor(featuresGrid.parentElement.offsetWidth / itemWidth);
  let totalItems = items.length;

  function updateSizes() {
    itemWidth = items[0].offsetWidth;
    visibleItems = Math.floor(featuresGrid.parentElement.offsetWidth / itemWidth);
    updateCarousel();
  }

  function updateCarousel() {
    const shift = -(itemWidth * currentIndex);
    featuresGrid.style.transform = `translateX(${shift}px)`;

    prevBtn.disabled = currentIndex === 0;
    nextBtn.disabled = currentIndex >= totalItems - visibleItems;
  }

  prevBtn.addEventListener('click', () => {
    if (currentIndex > 0) {
      currentIndex--;
      updateCarousel();
    }
  });

  nextBtn.addEventListener('click', () => {
    if (currentIndex < totalItems - visibleItems) {
      currentIndex++;
      updateCarousel();
    }
  });

  // Reaguj na resize
  window.addEventListener('resize', updateSizes);

  updateSizes();
});
