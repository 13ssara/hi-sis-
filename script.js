// ICON INTERACTION: Manage hover states for navigation icons
// Home icon stays light by default, others only light up on hover

const home = document.getElementById('home');
const profile = document.getElementById('profile');
const settings = document.getElementById('settings');
const otherIcons = [profile, settings];

// When hovering over profile or settings, remove active from home
otherIcons.forEach(icon => {
    icon.addEventListener('mouseenter', () => {
        home.classList.remove('active');
        icon.classList.add('active');
    });
    
    // When mouse leaves, remove active from that icon and restore home
    icon.addEventListener('mouseleave', () => {
        icon.classList.remove('active');
        home.classList.add('active');
    });
});
