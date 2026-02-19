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

// --- Photo selection ---
const selectedPhotos = new Map(); // column index -> { src, container }
const enlargeBtn = document.getElementById("enlarge-btn");
const enlargeCount = document.getElementById("enlarge-count");

function toggleSelect(container) {
  const col = container.getAttribute("data-column");
  const img = container.querySelector("img");
  const src = img.dataset.src || img.src;

  if (container.classList.contains("selected")) {
    container.classList.remove("selected");
    selectedPhotos.delete(col + ":" + src);
  } else {
    // Deselect any other photo in the same column
    const prev = document.querySelector(
      `.thumbnail-container.selected[data-column="${col}"]`
    );
    if (prev && prev !== container) {
      prev.classList.remove("selected");
      const prevImg = prev.querySelector("img");
      const prevSrc = prevImg.dataset.src || prevImg.src;
      selectedPhotos.delete(col + ":" + prevSrc);
    }
    container.classList.add("selected");
    selectedPhotos.set(col + ":" + src, src);
  }

  updateEnlargeBtn();
}

function updateEnlargeBtn() {
  const count = selectedPhotos.size;
  enlargeCount.textContent = count;
  enlargeBtn.classList.toggle("visible", count > 0);
}

// --- Fullscreen ---
const fullscreenOverlay = document.getElementById("fullscreen-overlay");
const fullscreenContent = document.getElementById("fullscreen-content");

function openFullscreen() {
  fullscreenContent.innerHTML = "";
  for (const src of selectedPhotos.values()) {
    const img = document.createElement("img");
    img.src = src.replace("/thumbnail/", "/original/");
    img.alt = "Selected photo";
    fullscreenContent.appendChild(img);
  }
  fullscreenOverlay.classList.add("open");
}

function closeFullscreen(event) {
  if (event.target === fullscreenOverlay) {
    fullscreenOverlay.classList.remove("open");
  }
}

document.addEventListener("keydown", function (e) {
  if (e.key === "Escape" && fullscreenOverlay.classList.contains("open")) {
    fullscreenOverlay.classList.remove("open");
  }
});

// --- Lazy loading via Intersection Observer ---
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
