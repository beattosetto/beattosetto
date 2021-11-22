window.onscroll = function() {scrollFunction()};
window.onresize = function() {onResize()};
window.addEventListener('load', function() {scrollFunction()})

let header = document.getElementById("header")
let profilePicture = document.getElementById("profile-picture")
let headerLogo = document.getElementById("header-logo")
let navListing = document.getElementById("nav-listing")
let mobileHeader = document.getElementById("mobile-header")
let mobileLogo = document.getElementById("mobile-logo")
let arrowProfileMenu = document.getElementById("arrow-profile-menu")

let resizeOnOpenMobileMenu = false;

function scrollFunction() {
    if (document.documentElement.clientWidth >= 1010) {
        if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
            profilePicture.style.height = "32px";
            profilePicture.style.width = "32px";
            headerLogo.style.height = "50px";
            header.style.backgroundColor = "rgba(39,45,49,0.8)";
            header.classList.add('blur-bg')
            navListing.style.fontSize = "18px"
        } else {
            profilePicture.style.height = "48px";
            profilePicture.style.width = "48px";
            headerLogo.style.height = "65px";
            header.style.backgroundColor = "rgba(39,45,49,0)"
            header.classList.remove('blur-bg')
            navListing.style.fontSize = "20px"
        }
    } else {
        if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
            mobileHeader.style.height = "7%";
            mobileHeader.style.minHeight = "68px";
            mobileLogo.style.marginTop = "-5px";
            mobileLogo.style.marginLeft = "-5px";
            mobileLogo.style.height = "45px";
            mobileHeader.style.backgroundColor = "rgba(39,45,49,.8)";
            mobileHeader.classList.add('blur-bg');
            document.getElementById("navbarToggleExternalContent").style.marginTop = "68px";
        } else {
            mobileHeader.style.height = "8%";
            mobileHeader.style.minHeight = "75px";
            mobileLogo.style.marginTop = "0";
            mobileLogo.style.marginLeft = "0";
            mobileLogo.style.height = "50px";
            mobileHeader.style.backgroundColor = "rgba(39,45,49,0)";
            mobileHeader.classList.remove('blur-bg');
            document.getElementById("navbarToggleExternalContent").style.marginTop = "77px";
        }
    }
}

function onResize() {
    if (document.documentElement.clientWidth >= 1010) {
        header.classList.add('show')
        header.classList.remove('hidden')
        header.style.zIndex = "2"
        mobileHeader.style.zIndex = "0"
        profilePicture.style.zIndex = "2"
        headerLogo.style.zIndex = "2"
        navListing.classList.remove('disabled')
        headerLogo.classList.remove('disabled')
    } else {
        header.classList.add('hidden')
        header.classList.remove('show')
        header.style.zIndex = "0"
        mobileHeader.style.zIndex = "2"
        profilePicture.style.zIndex = "0"
        headerLogo.style.zIndex = "0"
        navListing.classList.add('disabled')
        profilePicture.classList.add('disabled')
        headerLogo.classList.add('disabled')
    }

    if ((document.documentElement.clientWidth < 1010 && header.style.backgroundColor === "rgba(39,45,49,0.8)") ||
        (document.documentElement.clientWidth < 1010 && header.style.backgroundColor === "rgba(255,255,255,0.8)") ||
        (document.documentElement.clientWidth < 1010 && header.classList.contains('show'))) {
        header.style.backgroundColor = "rgba(39,45,49,0)";
    }

    if (document.documentElement.clientWidth < 1010 && header.classList.contains('show')) {
        header.classList.add('hidden');
    }
    scrollFunction()

    if (document.getElementById("navbarToggleExternalContent").classList.contains('show') && document.documentElement.clientWidth >= 1010) {
        document.getElementById("navbarToggleExternalContent").classList.remove('show');
        resizeOnOpenMobileMenu = true;
    }

    if (document.documentElement.clientWidth < 1010 && resizeOnOpenMobileMenu) {
        document.getElementById("navbarToggleExternalContent").classList.add('show');
        resizeOnOpenMobileMenu = false;
    }
}

function rotateArrowMenu() {
    if (document.getElementById("profile-menu").getAttribute("aria-expanded") === "false" || arrowProfileMenu.classList.contains('fa-chevron-down')) {
        arrowProfileMenu.classList.remove('fa-chevron-down')
        arrowProfileMenu.classList.add('fa-chevron-up')
    } else {
        arrowProfileMenu.classList.remove('fa-chevron-up')
        arrowProfileMenu.classList.add('fa-chevron-down')
    }
}

window.addEventListener("load", function(){onResize()})

var elem = document.body;
var lastClassName = elem.className;
window.setInterval( function() {
    var className = elem.className;
    if (className !== lastClassName) {
        scrollFunction()
        lastClassName = className;
    }
},10);

// Initialize AOS animation
AOS.init();
// Initialize bootstrap tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
});
// Initialize bootstrap toast
var toastElList = [].slice.call(document.querySelectorAll('.toast'))
var toastList = toastElList.map(function (toastEl) {
    return new bootstrap.Toast(toastEl)
})