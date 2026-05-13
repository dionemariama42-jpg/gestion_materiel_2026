// ============================================
// UFR SI — JavaScript principal
// ============================================

// ---- Sidebar toggle mobile ----
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('open');
}

function openMobileSidebar() {
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('overlay').classList.add('open');
}

function closeMobileSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('open');
}

// ---- Sidebar collapsible (desktop) ----
function initSidebarCollapse() {
  var sidebar = document.getElementById('sidebar');
  var topbar = document.getElementById('topbar');
  var mainContent = document.getElementById('mainContent');
  var toggleBtn = document.getElementById('toggleSidebarBtn');
  var toggleIcon = document.getElementById('toggleIcon');

  if (!sidebar || !toggleBtn) return;

  var isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';

  function applyCollapsed() {
    if (isCollapsed) {
      sidebar.classList.add('collapsed');
      if (topbar) topbar.classList.add('collapsed');
      if (mainContent) mainContent.classList.add('collapsed');
      if (toggleIcon) toggleIcon.className = 'bi bi-chevron-right';
      toggleBtn.title = 'Ouvrir le menu';
    } else {
      sidebar.classList.remove('collapsed');
      if (topbar) topbar.classList.remove('collapsed');
      if (mainContent) mainContent.classList.remove('collapsed');
      if (toggleIcon) toggleIcon.className = 'bi bi-chevron-left';
      toggleBtn.title = 'Réduire le menu';
    }
  }

  applyCollapsed();

  toggleBtn.addEventListener('click', function () {
    isCollapsed = !isCollapsed;
    localStorage.setItem('sidebarCollapsed', isCollapsed);
    applyCollapsed();
  });
}

// ---- Marquer lien actif ----
function marquerLienActif() {
  var links = document.querySelectorAll('.sidebar-link');
  var path = window.location.pathname;
  links.forEach(function(link) {
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });
}

// ============================================
// MODE SOMBRE — appliqué globalement via classe CSS
// ============================================

function setTheme(theme) {
  localStorage.setItem('theme', theme);
  appliquerTheme(theme);

  // Mettre à jour visuellement les boutons de choix (page paramètres)
  document.querySelectorAll('[id^="theme-"]').forEach(function(el) {
    el.style.borderColor = '#e0e7ff';
  });
  var btn = document.getElementById('theme-' + theme);
  if (btn) btn.style.borderColor = 'var(--primary)';
}

function appliquerTheme(theme) {
  if (theme === 'sombre') {
    document.body.classList.add('dark');
  } else if (theme === 'auto') {
    // Suit le système
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDark) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
  } else {
    // Clair
    document.body.classList.remove('dark');
  }
}

// ============================================
// COULEUR PRINCIPALE — appliquée globalement via CSS vars
// ============================================

function setCouleur(couleur) {
  localStorage.setItem('couleur', couleur);
  appliquerCouleur(couleur);

  // Mettre à jour visuellement les cercles de couleur (page paramètres)
  document.querySelectorAll('.couleur-option').forEach(function(el) {
    el.style.outline = 'none';
  });
  var cercle = document.querySelector('[data-couleur="' + couleur + '"]');
  if (cercle) cercle.style.outline = '3px solid ' + couleur;
}

function appliquerCouleur(couleur) {
  var root = document.documentElement;
  root.style.setProperty('--primary', couleur);
  root.style.setProperty('--primary-dark', shadeColor(couleur, -20));
  root.style.setProperty('--primary-light', shadeColor(couleur, 20));
  root.style.setProperty('--primary-lighter', shadeColor(couleur, 35));
  root.style.setProperty('--primary-glow', hexToRgba(couleur, 0.2));
  root.style.setProperty('--border', hexToRgba(couleur, 0.15));
  root.style.setProperty('--border-strong', hexToRgba(couleur, 0.3));
  root.style.setProperty('--surface-hover', hexToRgba(couleur, 0.06));
}

function shadeColor(color, percent) {
  var R = parseInt(color.substring(1, 3), 16);
  var G = parseInt(color.substring(3, 5), 16);
  var B = parseInt(color.substring(5, 7), 16);
  R = Math.min(255, Math.max(0, parseInt(R * (100 + percent) / 100)));
  G = Math.min(255, Math.max(0, parseInt(G * (100 + percent) / 100)));
  B = Math.min(255, Math.max(0, parseInt(B * (100 + percent) / 100)));
  return '#' + R.toString(16).padStart(2, '0') +
               G.toString(16).padStart(2, '0') +
               B.toString(16).padStart(2, '0');
}

function hexToRgba(hex, alpha) {
  var R = parseInt(hex.substring(1, 3), 16);
  var G = parseInt(hex.substring(3, 5), 16);
  var B = parseInt(hex.substring(5, 7), 16);
  return 'rgba(' + R + ',' + G + ',' + B + ',' + alpha + ')';
}

// ---- Appliquer les préférences sauvegardées (toutes pages) ----
function appliquerPreferences() {
  var theme = localStorage.getItem('theme') || 'clair';
  var couleur = localStorage.getItem('couleur');
  appliquerTheme(theme);
  if (couleur) appliquerCouleur(couleur);
}

// ============================================
// HERO SLIDER
// ============================================

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
  slides.forEach(function(s) { s.classList.remove('active'); });
  dots.forEach(function(d) { d.classList.remove('active'); });
  slideIndex = (n + slides.length) % slides.length;
  slides[slideIndex].classList.add('active');
  if (dots[slideIndex]) dots[slideIndex].classList.add('active');
}

function nextSlide() { showSlide(slideIndex + 1); }
function prevSlide() { showSlide(slideIndex - 1); }

// ============================================
// COMPTEURS ANIMÉS
// ============================================

function animerCompteurs() {
  var compteurs = document.querySelectorAll('.compteur');
  compteurs.forEach(function(compteur) {
    var cible = parseInt(compteur.getAttribute('data-cible'));
    var duree = 2000;
    var increment = cible / (duree / 16);
    var valeur = 0;
    var timer = setInterval(function() {
      valeur += increment;
      if (valeur >= cible) { valeur = cible; clearInterval(timer); }
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
      var badge = document.getElementById('notif-badge');
      if (badge) {
        if (data.count > 0) {
          badge.textContent = data.count > 99 ? '99+' : data.count;
          badge.style.display = 'flex';
        } else {
          badge.style.display = 'none';
        }
      }
      if (data.derniere && data.derniere.id !== derniereNotifId) {
        if (!window.location.href.includes('notifications')) {
          afficherPopupNotification(data.derniere.message, data.derniere.lien);
        }
        derniereNotifId = data.derniere.id;
        localStorage.setItem('derniereNotifId', derniereNotifId);
      }
    })
    .catch(function() {});
}

function afficherPopupNotification(message, lien) {
  var ancienPopup = document.querySelector('.notif-popup');
  if (ancienPopup) ancienPopup.remove();

  var popup = document.createElement('div');
  popup.className = 'notif-popup';
  popup.innerHTML =
    '<div class="notif-popup-header">' +
    '<i class="bi bi-bell-fill me-2" style="color:var(--primary);font-size:16px;"></i>' +
    '<strong style="font-size:13px;">Nouvelle notification</strong>' +
    '<button onclick="this.closest(\'.notif-popup\').remove()" ' +
    'style="background:none;border:none;font-size:20px;cursor:pointer;color:#94a3b8;margin-left:auto;line-height:1;">×</button>' +
    '</div>' +
    '<div class="notif-popup-body">' + message + '</div>' +
    (lien ? '<a href="' + lien + '" class="notif-popup-link">Voir les détails →</a>' : '');

  document.body.appendChild(popup);
  setTimeout(function() { popup.classList.add('show'); }, 50);

  try {
    var ctx = new (window.AudioContext || window.webkitAudioContext)();
    [880, 1100, 880].forEach(function(freq, i) {
      var osc = ctx.createOscillator();
      var gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.1, ctx.currentTime + i * 0.15);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.15 + 0.1);
      osc.start(ctx.currentTime + i * 0.15);
      osc.stop(ctx.currentTime + i * 0.15 + 0.1);
    });
  } catch(e) {}

  setTimeout(function() {
    popup.classList.remove('show');
    setTimeout(function() { if (popup.parentNode) popup.remove(); }, 400);
  }, 7000);
}

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  // 1. Appliquer thème et couleur EN PREMIER (avant tout le reste)
  appliquerPreferences();

  // 2. Sidebar
  marquerLienActif();
  initSidebarCollapse();

  // 3. Slider hero
  initSlider();

  // 4. Notifications
  verifierNouvellesNotifications();
  setInterval(verifierNouvellesNotifications, 30000);

  if (window.location.href.includes('notifications')) {
    var badge = document.getElementById('notif-badge');
    if (badge) badge.style.display = 'none';
    derniereNotifId = 0;
    localStorage.removeItem('derniereNotifId');
  }

  // 5. Compteurs animés
  var statsSection = document.querySelector('.stats-section');
  if (statsSection) {
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) { animerCompteurs(); observer.disconnect(); }
      });
    });
    observer.observe(statsSection);
  }
});