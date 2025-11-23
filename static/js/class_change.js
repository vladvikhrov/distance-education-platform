const rows = document.querySelectorAll('#tbody tr');
const checks = document.querySelectorAll('.check');
const count = document.getElementById('count');
const classFilter = document.getElementById('classFilter');
const searchInput = document.getElementById('search');
const toggleBtn = document.getElementById('toggleSelect');

function updateCount() {
  count.textContent = document.querySelectorAll('.check:checked').length;
}

// Функция: применить фильтры (класс + поиск)
function applyFilters() {
  const classVal = classFilter.value;
  const searchVal = searchInput.value.toLowerCase();
  
  rows.forEach(row => {
    const matchClass = !classVal || row.dataset.class === classVal;
    const matchSearch = !searchVal || row.dataset.search.includes(searchVal);
    row.style.display = (matchClass && matchSearch) ? '' : 'none';
  });
}

// Кнопка: выбрать/снять всех (toggle)
toggleBtn.addEventListener('click', function() {
  let visibleChecked = 0;
  let visibleTotal = 0;
  
  // Считаем сколько видимых и сколько выбрано
  rows.forEach(row => {
    if (row.style.display !== 'none') {
      visibleTotal++;
      if (row.querySelector('.check').checked) visibleChecked++;
    }
  });
  
  // Решаем: выбрать или снять
  const shouldCheck = visibleChecked < visibleTotal;
  
  // Применяем действие
  rows.forEach(row => {
    if (row.style.display !== 'none') {
      row.querySelector('.check').checked = shouldCheck;
    }
  });
  
  if (shouldCheck) {
    toggleBtn.innerHTML = '<i class="bi bi-x-square me-1"></i>Снять выбор';
    toggleBtn.classList.remove('btn-outline-primary');
    toggleBtn.classList.add('btn-outline-secondary');
  } else {
    toggleBtn.innerHTML = '<i class="bi bi-check-square me-1"></i>Выбрать всех';
    toggleBtn.classList.remove('btn-outline-secondary');
    toggleBtn.classList.add('btn-outline-primary');
  }
  
  updateCount();
});

checks.forEach(check => check.addEventListener('change', updateCount));

classFilter.addEventListener('change', applyFilters);

searchInput.addEventListener('input', applyFilters);

document.getElementById('mainForm').addEventListener('submit', function(e) {
  const selected = document.querySelectorAll('.check:checked').length;
  if (selected === 0) {
    e.preventDefault();
    alert('Выберите хотя бы одного ученика');
  }
});