// --- Slideshow ---
// Uses fullscreenOverlay and fullscreenContent from timeline.js
let slideshowColumns = []; // [{name, photos: [{src, age}]}]
let slideshowStep = 0;
let slideshowTimers = [];
let slideshowPaused = false;
let slideshowActive = false;

function collectColumns() {
  const headers = document.querySelectorAll(".header-row .col");
  const columns = [];
  headers.forEach((header, i) => {
    const name = header.textContent.trim();
    const photos = [];
    document.querySelectorAll(".photo-row").forEach((row) => {
      const galleries = row.querySelectorAll(".image-gallery");
      if (i >= galleries.length) return;
      const gallery = galleries[i];
      const ageLabel = row.querySelector(".age-label");
      const age = ageLabel ? ageLabel.textContent.trim() : "";
      const thumb = gallery.querySelector(".thumbnail-container img");
      if (!thumb) return;
      const src = thumb.dataset.src || thumb.src;
      if (src) photos.push({ src, age });
    });
    if (photos.length > 0) {
      // Shuffle photos (Fisher-Yates)
      for (let j = photos.length - 1; j > 0; j--) {
        const k = Math.floor(Math.random() * (j + 1));
        [photos[j], photos[k]] = [photos[k], photos[j]];
      }
      columns.push({ name, photos });
    }
  });
  return columns;
}

function clearSlideshowTimers() {
  for (const t of slideshowTimers) clearTimeout(t);
  slideshowTimers = [];
}

function slideshowStepInfo(step) {
  const n = slideshowColumns.length;
  return { colIdx: step % n, round: Math.floor(step / n) };
}

function slideshowMaxSteps() {
  const maxPhotos = Math.max(...slideshowColumns.map((c) => c.photos.length));
  return maxPhotos * slideshowColumns.length;
}

function revealStep() {
  clearSlideshowTimers();
  const { colIdx, round } = slideshowStepInfo(slideshowStep);
  const col = slideshowColumns[colIdx];
  const photo = col.photos[round % col.photos.length];

  const items = fullscreenContent.querySelectorAll(".fullscreen-item");
  const wrapper = items[colIdx];
  const img = wrapper.querySelector("img");
  const nameLabel = wrapper.querySelector(".slideshow-name");
  const ageLabel = wrapper.querySelector(".slideshow-age");

  if (round > 0) {
    // Fade out old photo, hide labels
    nameLabel.classList.remove("visible");
    ageLabel.classList.remove("visible");
    wrapper.classList.add("slideshow-hidden");

    slideshowTimers.push(
      setTimeout(() => {
        img.src = photo.src.replace("/thumbnail/", "/original/");
        ageLabel.textContent = photo.age;
        wrapper.classList.remove("slideshow-hidden");
        scheduleLabels(nameLabel, ageLabel);
      }, 800),
    );
  } else {
    // First appearance
    img.src = photo.src.replace("/thumbnail/", "/original/");
    ageLabel.textContent = photo.age;
    wrapper.classList.remove("slideshow-hidden");
    scheduleLabels(nameLabel, ageLabel);
  }
}

function scheduleLabels(nameLabel, ageLabel) {
  slideshowTimers.push(
    setTimeout(() => {
      nameLabel.classList.add("visible");
    }, 5000),
  );
  slideshowTimers.push(
    setTimeout(() => {
      ageLabel.classList.add("visible");
    }, 8000),
  );
  slideshowTimers.push(
    setTimeout(() => {
      if (!slideshowActive || slideshowPaused) return;
      slideshowStep++;
      if (slideshowStep >= slideshowMaxSteps()) slideshowStep = 0;
      revealStep();
    }, 9000),
  );
}

function rebuildState() {
  clearSlideshowTimers();
  const n = slideshowColumns.length;
  const items = fullscreenContent.querySelectorAll(".fullscreen-item");
  const { colIdx: curCol, round: curRound } = slideshowStepInfo(slideshowStep);

  for (let c = 0; c < n; c++) {
    const col = slideshowColumns[c];
    const wrapper = items[c];
    const img = wrapper.querySelector("img");
    const nameLabel = wrapper.querySelector(".slideshow-name");
    const ageLabel = wrapper.querySelector(".slideshow-age");

    // Determine what round this column should show
    const colRound =
      c < curCol ? curRound : c === curCol ? curRound : curRound - 1;

    if (colRound < 0) {
      wrapper.classList.add("slideshow-hidden");
      nameLabel.classList.remove("visible");
      ageLabel.classList.remove("visible");
    } else if (c === curCol) {
      // Will be animated by revealStep
    } else {
      const photo = col.photos[colRound % col.photos.length];
      img.src = photo.src.replace("/thumbnail/", "/original/");
      ageLabel.textContent = photo.age;
      wrapper.classList.remove("slideshow-hidden");
      nameLabel.classList.add("visible");
      ageLabel.classList.add("visible");
    }
  }

  revealStep();
}

function nextSlide() {
  if (!slideshowActive) return;
  slideshowStep++;
  if (slideshowStep >= slideshowMaxSteps()) slideshowStep = 0;
  rebuildState();
}

function prevSlide() {
  if (!slideshowActive) return;
  slideshowStep--;
  if (slideshowStep < 0) slideshowStep = slideshowMaxSteps() - 1;
  rebuildState();
}

// biome-ignore lint/correctness/noUnusedVariables: called from HTML onclick
function startSlideshow() {
  slideshowColumns = collectColumns();
  if (slideshowColumns.length === 0) return;
  slideshowStep = 0;
  slideshowPaused = false;
  slideshowActive = true;

  fullscreenContent.innerHTML = "";
  for (const col of slideshowColumns) {
    const wrapper = document.createElement("div");
    wrapper.className = "fullscreen-item slideshow-hidden";
    const img = document.createElement("img");
    img.alt = col.name;
    const nameLabel = document.createElement("p");
    nameLabel.className = "fullscreen-label slideshow-name";
    nameLabel.textContent = col.name;
    const ageLabel = document.createElement("p");
    ageLabel.className = "fullscreen-label slideshow-age";
    wrapper.appendChild(img);
    wrapper.appendChild(nameLabel);
    wrapper.appendChild(ageLabel);
    fullscreenContent.appendChild(wrapper);
  }

  fullscreenOverlay.classList.remove("slideshow-paused");
  fullscreenOverlay.classList.add("open");
  revealStep();
}

// biome-ignore lint/correctness/noUnusedVariables: called from timeline.js
function stopSlideshow() {
  slideshowActive = false;
  slideshowPaused = false;
  clearSlideshowTimers();
  fullscreenOverlay.classList.remove("open", "slideshow-paused");
}

document.addEventListener("keydown", (e) => {
  if (!slideshowActive) return;
  if (e.key === "ArrowRight") {
    clearSlideshowTimers();
    nextSlide();
  } else if (e.key === "ArrowLeft") {
    clearSlideshowTimers();
    prevSlide();
  } else if (e.key === " ") {
    e.preventDefault();
    if (slideshowPaused) {
      slideshowPaused = false;
      fullscreenOverlay.classList.remove("slideshow-paused");
      revealStep();
    } else {
      slideshowPaused = true;
      clearSlideshowTimers();
      fullscreenOverlay.classList.add("slideshow-paused");
    }
  }
});
