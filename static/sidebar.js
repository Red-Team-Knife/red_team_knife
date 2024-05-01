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


function editWindow(){
    var sidebarWidth = document.querySelector('#mySidebar').offsetWidth;
    var content = document.querySelector('.content');
    content.style.marginLeft = (sidebarWidth + 40) + 'px';
}

window.addEventListener('DOMContentLoaded', editWindow);
window.addEventListener('resize', editWindow);

