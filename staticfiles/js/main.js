// ============================================
// UFR SI — JavaScript principal
// ============================================

// Sidebar toggle mobile
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('open');
}

// Marquer lien actif dans sidebar
function marquerLienActif() {
  const links = document.querySelectorAll('.sidebar-link');
  links.forEach(link => {
    if (link.href === window.location.href) {
      link.classList.add('active');
    }
  });
}

// Mode sombre
function setTheme(theme) {
  localStorage.setItem('theme', theme);
  if (theme === 'sombre') {
    document.body.classList.add('dark');
  } else {
    document.body.classList.remove('dark');
  }
}

// Couleur principale
function setCouleur(couleur) {
  document.documentElement.style.setProperty('--primary', couleur);
  document.documentElement.style.setProperty('--primary-dark',
    shadeColor(couleur, -20));
  document.documentElement.style.setProperty('--primary-light',
    shadeColor(couleur, 20));
  localStorage.setItem('couleur', couleur);
}

function shadeColor(color, percent) {
  var R = parseInt(color.substring(1,3), 16);
  var G = parseInt(color.substring(3,5), 16);
  var B = parseInt(color.substring(5,7), 16);
  R = parseInt(R * (100 + percent) / 100);
  G = parseInt(G * (100 + percent) / 100);
  B = parseInt(B * (100 + percent) / 100);
  R = (R<255)?R:255; G = (G<255)?G:255; B = (B<255)?B:255;
  R = Math.max(0, R); G = Math.max(0, G); B = Math.max(0, B);
  var RR = R.toString(16).padStart(2, '0');
  var GG = G.toString(16).padStart(2, '0');
  var BB = B.toString(16).padStart(2, '0');
  return "#" + RR + GG + BB;
}

// Appliquer préférences sauvegardées
function appliquerPreferences() {
  var theme = localStorage.getItem('theme');
  var couleur = localStorage.getItem('couleur');
  if (theme === 'sombre') document.body.classList.add('dark');
  if (couleur) setCouleur(couleur);
}

// Hero slider
var slideIndex = 0;
var slides, dots;

function initSlider() {
  slides = document.querySelectorAll('.hero-slide');
  dots = document.querySelectorAll('.hero-dot');
  if (slides.length === 0) return;
  showSlide(0);
  setInterval(nextSlide, 5000);
}

function showSlide(n) {
  slides.forEach(s => s.classList.remove('active'));
  dots.forEach(d => d.classList.remove('active'));
  slideIndex = (n + slides.length) % slides.length;
  slides[slideIndex].classList.add('active');
  if (dots[slideIndex]) dots[slideIndex].classList.add('active');
}

function nextSlide() { showSlide(slideIndex + 1); }
function prevSlide() { showSlide(slideIndex - 1); }

// Compteur animé
function animerCompteurs() {
  const compteurs = document.querySelectorAll('.compteur');
  compteurs.forEach(compteur => {
    const cible = parseInt(compteur.getAttribute('data-cible'));
    const duree = 2000;
    const increment = cible / (duree / 16);
    let valeur = 0;
    const timer = setInterval(() => {
      valeur += increment;
      if (valeur >= cible) {
        valeur = cible;
        clearInterval(timer);
      }
      compteur.textContent = Math.floor(valeur);
    }, 16);
  });
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
  marquerLienActif();
  appliquerPreferences();
  initSlider();

  // Observer pour compteurs
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animerCompteurs();
        observer.disconnect();
      }
    });
  });
  const statsSection = document.querySelector('.stats-section');
  if (statsSection) observer.observe(statsSection);
});