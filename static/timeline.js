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

function getPhotoLabel(container) {
  const img = container.querySelector("img");
  const title = img.getAttribute("alt") || "";
  const row = container.closest(".photo-row");
  const age = row ? row.querySelector(".age-label").textContent.trim() : "";
  return title + (age ? " — " + age : "");
}

function toggleSelect(container) {
  const col = container.getAttribute("data-column");
  const img = container.querySelector("img");
  const src = img.dataset.src || img.src;
  const key = col + ":" + src;

  if (container.classList.contains("selected")) {
    container.classList.remove("selected");
    selectedPhotos.delete(key);
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
    selectedPhotos.set(key, { src, label: getPhotoLabel(container) });
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
  for (const { src, label } of selectedPhotos.values()) {
    const wrapper = document.createElement("div");
    wrapper.className = "fullscreen-item";
    const img = document.createElement("img");
    img.src = src.replace("/thumbnail/", "/original/");
    img.alt = label;
    const caption = document.createElement("p");
    caption.className = "fullscreen-label";
    caption.textContent = label;
    wrapper.appendChild(img);
    wrapper.appendChild(caption);
    fullscreenContent.appendChild(wrapper);
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
      const container = lazyImage.closest(".thumbnail-container");
      container.classList.add("loading");
      lazyImage.onload = () => container.classList.remove("loading");
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

// --- Collapsible rows ---
document.querySelectorAll(".photo-row").forEach(row => {
  const galleries = row.querySelectorAll(".image-gallery");
  let needsCollapse = false;

  galleries.forEach(gallery => {
    const thumbs = gallery.querySelectorAll(".thumbnail-container");
    if (thumbs.length > 8) {
      needsCollapse = true;
      const overlay = document.createElement("div");
      overlay.className = "expand-overlay";
      overlay.textContent = "+" + (thumbs.length - 7);
      overlay.addEventListener("click", function (e) {
        e.stopPropagation();
        row.classList.remove("collapsed");
        row.querySelectorAll(".expand-overlay").forEach(o => o.remove());
      });
      thumbs[7].appendChild(overlay);
    }
  });

  if (needsCollapse) row.classList.add("collapsed");
});
