// Build highlight container once at page load
const highlightContainer = document.createElement("div");
highlightContainer.classList.add("highlight", "text-center");

const highlightImg = document.createElement("img");
highlightImg.alt = "Enlarged image";

const highlightLabel = document.createElement("p");

highlightContainer.appendChild(highlightImg);
highlightContainer.appendChild(highlightLabel);
document.body.appendChild(highlightContainer);

let hideTimeout = null;

function showImage(element, path, title) {
  if (hideTimeout) {
    clearTimeout(hideTimeout);
    hideTimeout = null;
  }
  highlightImg.src = path;
  highlightLabel.textContent = title;
  highlightContainer.classList.add("visible");
}

function hideImage(element) {
  highlightContainer.classList.remove("visible");
  hideTimeout = setTimeout(function () {
    highlightImg.src = "";
  }, 200);
}

// Lazy loading via Intersection Observer
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const lazyImage = entry.target;
      lazyImage.src = lazyImage.dataset.src;
      lazyImage.classList.remove("lazy-load");
      observer.unobserve(lazyImage);
    }
  });
});

const lazyImages = document.querySelectorAll(".lazy-load");
lazyImages.forEach(image => {
  observer.observe(image);
});
