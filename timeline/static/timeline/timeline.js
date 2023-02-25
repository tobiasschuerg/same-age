function showImage(element, path) {
  var enlargedImage = document.createElement("img");
  enlargedImage.src = path;
  enlargedImage.alt = "Enlarged image";
  enlargedImage.classList.add("highlight");
  enlargedImage.style.transition = "opacity 0.3s ease-in-out";
  document.body.appendChild(enlargedImage);
  setTimeout(function() {
    enlargedImage.style.opacity = "1";
  }, 100);
}

function hideImage(element) {
  var enlargedImage = document.querySelector("img[alt='Enlarged image']");
  enlargedImage.style.opacity = "0";
  document.body.removeChild(enlargedImage);
}