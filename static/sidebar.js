function index_open() {
    document.getElementById("rtk_sidebar").style.display = "block";
    document.getElementById("rtk_overlay").style.display = "block";
}

function index_close() {
    document.getElementById("rtk_sidebar").style.display = "none";
    document.getElementById("rtk_overlay").style.display = "none";
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
    var sidebarWidth = document.querySelector('#rtk_sidebar').offsetWidth;
    var content = document.querySelector('.content');
    content.style.marginLeft = (sidebarWidth + 40) + 'px';
}

window.addEventListener('DOMContentLoaded', editWindow);
window.addEventListener('resize', editWindow);

