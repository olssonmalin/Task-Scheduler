function show(e) {
    console.log(e.target.parentNode)
    const showElement = e.target.parentNode.querySelector('.show-element');
    showElement.style.display = "block";
};

function close(e) {
    const closeElement = e.target.parentNode;
    closeElement.style.display = "none";
};

clickShowContainers = document.getElementsByClassName("click-show-container");
for (element of clickShowContainers) {
    const buttonShow = element.querySelector('.click-button-show');
    const buttonClose = element.querySelector('.click-button-close');
    buttonShow.addEventListener("click", show);
    buttonClose.addEventListener("click", close);
};

