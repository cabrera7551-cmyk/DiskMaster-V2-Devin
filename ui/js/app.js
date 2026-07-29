// Navegacion SPA + animaciones visuales. Solo datos de demostracion.
(function () {
  'use strict';

  const navItems = Array.from(document.querySelectorAll('.nav__item'));
  const sections = Array.from(document.querySelectorAll('.section'));

  function activate(target) {
    sections.forEach((section) => {
      section.classList.toggle('is-active', section.id === target);
    });
    navItems.forEach((item) => {
      item.classList.toggle('is-active', item.dataset.target === target);
    });
    document.querySelector('.main').scrollTop = 0;
  }

  navItems.forEach((item) => {
    item.addEventListener('click', () => activate(item.dataset.target));
  });

  // Escaneo simulado: solo texto estatico animado.
  const scanButton = document.getElementById('btn-escanear');
  const scanState = document.getElementById('scan-state');
  const scanLog = document.getElementById('scan-log');

  const demoLines = [
    { tag: '[ok]', cls: 'term__tag--ok', text: 'particion verificada', meta: 'C: NTFS 480 GB' },
    { tag: '[--]', cls: '', text: '318 archivos indexados', meta: '12 carpetas recorridas' },
    { tag: '[!!]', cls: 'term__tag--warn', text: '3 archivos duplicados detectados', meta: '6.2 GB recuperables' }
  ];

  function renderLine(line) {
    const row = document.createElement('div');
    row.className = 'term__line';
    const tag = document.createElement('span');
    tag.className = 'term__tag ' + line.cls;
    tag.textContent = line.tag;
    const label = document.createElement('strong');
    label.textContent = line.text;
    row.appendChild(tag);
    row.appendChild(label);
    row.appendChild(document.createTextNode(' — ' + line.meta));
    scanLog.appendChild(row);
  }

  if (scanButton) {
    scanButton.addEventListener('click', () => {
      if (scanButton.disabled) return;
      scanButton.disabled = true;
      scanLog.textContent = '';
      scanState.textContent = 'escaneando...';
      scanState.className = 'tag tag--warn';

      demoLines.forEach((line, index) => {
        setTimeout(() => renderLine(line), 450 * (index + 1));
      });

      setTimeout(() => {
        scanState.textContent = 'completado';
        scanState.className = 'tag tag--ok';
        scanButton.disabled = false;
      }, 450 * (demoLines.length + 1));
    });
  }

  activate('dashboard');
})();
