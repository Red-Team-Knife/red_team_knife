
// Open and close sidebar
function index_open() {

    document.getElementById("mySidebar").style.display = "block";
    document.getElementById("myOverlay").style.display = "block";
}

function index_close() {

    document.getElementById("mySidebar").style.display = "none";
    document.getElementById("myOverlay").style.display = "none";
}

// Show subelements with transition
function showItem(element) {
    var item = element.nextElementSibling;
    if (item.classList.contains("collapsed")) {

        item.classList.remove("collapsed");
        item.classList.add("expanded");
    } else {

        item.classList.remove("expanded");
        item.classList.add("collapsed");
    }
}
