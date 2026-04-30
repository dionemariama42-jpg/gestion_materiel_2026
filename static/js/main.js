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
  document.documentElement.style.setProperty('--primary-dark', shadeColor(couleur, -20));
  document.documentElement.style.setProperty('--primary-light', shadeColor(couleur, 20));
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
  return "#" + R.toString(16).padStart(2,'0') +
               G.toString(16).padStart(2,'0') +
               B.toString(16).padStart(2,'0');
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

// ============================================
// NOTIFICATIONS EN TEMPS RÉEL
// ============================================

var derniereNotifId = localStorage.getItem('derniereNotifId') ?
  parseInt(localStorage.getItem('derniereNotifId')) : 0;

function verifierNouvellesNotifications() {
  fetch('/clubs/notifications/count/')
    .then(function(r) { return r.json(); })
    .then(function(data) {

      // Mettre à jour badge cloche
      var badge = document.getElementById('notif-badge');
      if (badge) {
        if (data.count > 0) {
          badge.textContent = data.count > 99 ? '99+' : data.count;
          badge.style.display = 'flex';
        } else {
          badge.style.display = 'none';
        }
      }

      // Afficher popup si nouvelle notification
      if (data.derniere && data.derniere.id !== derniereNotifId) {
        // Ne pas afficher si on est déjà sur la page notifications
        if (!window.location.href.includes('notifications')) {
          afficherPopupNotification(
            data.derniere.message,
            data.derniere.lien
          );
        }
        derniereNotifId = data.derniere.id;
        localStorage.setItem('derniereNotifId', derniereNotifId);
      }
    })
    .catch(function() {});
}

function afficherPopupNotification(message, lien) {
  // Supprimer ancien popup si existe
  var ancienPopup = document.querySelector('.notif-popup');
  if (ancienPopup) ancienPopup.remove();

  var popup = document.createElement('div');
  popup.className = 'notif-popup';
  popup.innerHTML =
    '<div class="notif-popup-header">' +
    '<i class="bi bi-bell-fill me-2" style="color:#f39c12;font-size:16px;"></i>' +
    '<strong style="font-size:13px;">Nouvelle notification</strong>' +
    '<button onclick="this.closest(\'.notif-popup\').remove()" ' +
    'style="background:none;border:none;font-size:20px;cursor:pointer;' +
    'color:#94a3b8;margin-left:auto;line-height:1;">×</button>' +
    '</div>' +
    '<div class="notif-popup-body">' + message + '</div>' +
    (lien ?
      '<a href="' + lien + '" class="notif-popup-link">Voir les détails →</a>'
      : '');

  document.body.appendChild(popup);

  // Animation entrée
  setTimeout(function() { popup.classList.add('show'); }, 50);

  // Son de notification
  try {
    var ctx = new (window.AudioContext || window.webkitAudioContext)();
    [880, 1100, 880].forEach(function(freq, i) {
      var osc = ctx.createOscillator();
      var gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.1, ctx.currentTime + i * 0.15);
      gain.gain.exponentialRampToValueAtTime(
        0.001, ctx.currentTime + i * 0.15 + 0.1
      );
      osc.start(ctx.currentTime + i * 0.15);
      osc.stop(ctx.currentTime + i * 0.15 + 0.1);
    });
  } catch(e) {}

  // Disparaît après 7 secondes
  setTimeout(function() {
    popup.classList.remove('show');
    setTimeout(function() {
      if (popup.parentNode) popup.remove();
    }, 400);
  }, 7000);
}

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  marquerLienActif();
  appliquerPreferences();
  initSlider();

  // Notifications
  verifierNouvellesNotifications();
  setInterval(verifierNouvellesNotifications, 30000);

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