const API = {
  plantSummary: '/api/plants/latest',
  plantHistory: '/api/plants/{plantId}/history?hours=24',
};

const REFRESH_INTERVAL_MS = 30 * 60 * 1000;

const plantsMeta = [
  {
    id: 'plant-1',
    name: 'Aloe Vera',
    species: 'Aloe barbadensis miller',
    image: 'pic/微信图片_20260410151833_480_1.jpg',
    description: 'A resilient succulent known for water-storing leaves and low-maintenance growth habits.',
    idealMin: 30,
    idealMax: 55,
  },
  {
    id: 'plant-2',
    name: 'Peace Lily',
    species: 'Spathiphyllum wallisii',
    image: 'pic/微信图片_20260410151834_481_1.jpg',
    description: 'An elegant indoor plant with glossy leaves and white blooms, preferring stable moisture.',
    idealMin: 45,
    idealMax: 65,
  },
  {
    id: 'plant-3',
    name: 'Pothos',
    species: 'Epipremnum aureum',
    image: 'pic/微信图片_20260410151834_482_1.jpg',
    description: 'A fast-growing trailing vine that adapts well indoors and thrives with moderate humidity.',
    idealMin: 40,
    idealMax: 60,
  },
  {
    id: 'plant-4',
    name: 'Snake Plant',
    species: 'Dracaena trifasciata',
    image: 'pic/微信图片_20260410151835_483_1.jpg',
    description: 'A highly tolerant plant with upright leaves, suitable for low-water and low-light conditions.',
    idealMin: 25,
    idealMax: 45,
  },
  {
    id: 'plant-5',
    name: 'Monstera',
    species: 'Monstera deliciosa',
    image: 'pic/微信图片_20260410151836_484_1.jpg',
    description: 'A tropical favorite with split leaves, requiring balanced humidity and a stable environment.',
    idealMin: 50,
    idealMax: 70,
  },
];

let currentData = [];
let humidityChart = null;

const elements = {
  grid: document.getElementById('plantGrid'),
  totalPlants: document.getElementById('totalPlants'),
  avgHumidity: document.getElementById('avgHumidity'),
  healthyCount: document.getElementById('healthyCount'),
  lastUpdated: document.getElementById('lastUpdated'),
  refreshBtn: document.getElementById('refreshBtn'),
  dataModeBadge: document.getElementById('dataModeBadge'),
  modal: document.getElementById('detailModal'),
  modalBackdrop: document.getElementById('modalBackdrop'),
  closeModal: document.getElementById('closeModal'),
  modalImage: document.getElementById('modalImage'),
  modalName: document.getElementById('modalName'),
  modalDesc: document.getElementById('modalDesc'),
  modalSpecies: document.getElementById('modalSpecies'),
  modalIdealHumidity: document.getElementById('modalIdealHumidity'),
  modalCurrentHumidity: document.getElementById('modalCurrentHumidity'),
  chartCanvas: document.getElementById('humidityChart'),
};

function getStatus(humidity, min, max) {
  if (humidity < min - 5 || humidity > max + 5) return 'bad';
  if (humidity < min || humidity > max) return 'warn';
  return 'good';
}

function statusLabel(status) {
  if (status === 'good') return 'Healthy';
  if (status === 'warn') return 'Watch';
  return 'Alert';
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function createMockHistory(current) {
  const points = 24;
  const labels = [];
  const values = [];

  for (let i = points - 1; i >= 0; i--) {
    const time = new Date(Date.now() - i * 60 * 60 * 1000);
    labels.push(`${String(time.getHours()).padStart(2, '0')}:00`);
  }

  let val = current;
  for (let i = 0; i < points; i++) {
    val += Math.random() * 6 - 3;
    val = clamp(val, 18, 88);
    values.push(Number(val.toFixed(1)));
  }

  values[values.length - 1] = current;
  return { labels, values };
}

function createMockLatestData() {
  return plantsMeta.map((plant) => {
    const humidity = Math.round(plant.idealMin + Math.random() * (plant.idealMax - plant.idealMin + 12));
    return {
      ...plant,
      humidity,
      updatedAt: new Date().toISOString(),
      history: createMockHistory(humidity),
    };
  });
}

async function fetchPlantSummary() {
  try {
    const res = await fetch(API.plantSummary);
    if (!res.ok) throw new Error('API unavailable');
    const payload = await res.json();

    const merged = plantsMeta.map((plant) => {
      const dbItem = payload?.plants?.find((item) => item.id === plant.id || item.device === plant.id);
      const humidity = Number(dbItem?.humidity ?? dbItem?.temperature ?? plant.idealMin + 5);
      return {
        ...plant,
        humidity,
        updatedAt: dbItem?.timestamp || new Date().toISOString(),
        history: createMockHistory(humidity),
      };
    });

    elements.dataModeBadge.textContent = 'Live API';
    return merged;
  } catch {
    elements.dataModeBadge.textContent = 'Mock Data';
    return createMockLatestData();
  }
}

function renderStats(data) {
  const total = data.length;
  const avg = total ? data.reduce((sum, item) => sum + item.humidity, 0) / total : 0;
  const healthy = data.filter((item) => getStatus(item.humidity, item.idealMin, item.idealMax) === 'good').length;

  elements.totalPlants.textContent = String(total);
  elements.avgHumidity.textContent = `${avg.toFixed(1)}%`;
  elements.healthyCount.textContent = `${healthy}/${total}`;
  elements.lastUpdated.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function renderCards(data) {
  elements.grid.innerHTML = data
    .map((item) => {
      const status = getStatus(item.humidity, item.idealMin, item.idealMax);
      const progress = clamp(item.humidity, 0, 100);
      return `
      <article class="plant-card" data-plant-id="${item.id}">
        <div class="card-image-wrap">
          <img src="${item.image}" alt="${item.name}" loading="lazy" />
        </div>
        <div class="card-content">
          <div class="card-top">
            <h4 class="card-name">${item.name}</h4>
            <span class="badge ${status}">${statusLabel(status)}</span>
          </div>
          <div class="humidity-line">
            <span>Humidity</span>
            <strong>${item.humidity}%</strong>
          </div>
          <div class="progress"><div style="width:${progress}%"></div></div>
        </div>
      </article>
    `;
    })
    .join('');

  const cards = elements.grid.querySelectorAll('.plant-card');
  cards.forEach((card) => {
    card.addEventListener('click', () => {
      const plantId = card.getAttribute('data-plant-id');
      const selected = currentData.find((item) => item.id === plantId);
      if (selected) openModal(selected);
    });
  });
}

async function loadPlantData() {
  currentData = await fetchPlantSummary();
  renderStats(currentData);
  renderCards(currentData);
}

function openModal(plant) {
  elements.modalImage.src = plant.image;
  elements.modalImage.alt = plant.name;
  elements.modalName.textContent = plant.name;
  elements.modalDesc.textContent = plant.description;
  elements.modalSpecies.textContent = plant.species;
  elements.modalIdealHumidity.textContent = `Ideal: ${plant.idealMin}% - ${plant.idealMax}%`;
  elements.modalCurrentHumidity.textContent = `Current: ${plant.humidity}%`;

  if (humidityChart) {
    humidityChart.destroy();
  }

  humidityChart = new Chart(elements.chartCanvas, {
    type: 'line',
    data: {
      labels: plant.history.labels,
      datasets: [
        {
          label: 'Humidity %',
          data: plant.history.values,
          tension: 0.35,
          borderWidth: 2.5,
          borderColor: '#6be4ff',
          pointRadius: 2,
          pointHoverRadius: 4,
          pointBackgroundColor: '#6be4ff',
          fill: true,
          backgroundColor: 'rgba(107, 228, 255, 0.12)',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: '#d8e5ff',
          },
        },
      },
      scales: {
        x: {
          ticks: { color: '#9fb1d9' },
          grid: { color: 'rgba(255,255,255,0.08)' },
        },
        y: {
          suggestedMin: 0,
          suggestedMax: 100,
          ticks: { color: '#9fb1d9' },
          grid: { color: 'rgba(255,255,255,0.08)' },
        },
      },
    },
  });

  elements.modal.classList.remove('hidden');
  elements.modal.setAttribute('aria-hidden', 'false');
}

function closeModal() {
  if (humidityChart) {
    humidityChart.destroy();
    humidityChart = null;
  }
  elements.modal.classList.add('hidden');
  elements.modal.setAttribute('aria-hidden', 'true');
}

elements.refreshBtn.addEventListener('click', loadPlantData);
elements.closeModal.addEventListener('click', closeModal);
elements.modalBackdrop.addEventListener('click', closeModal);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});

loadPlantData();
setInterval(loadPlantData, REFRESH_INTERVAL_MS);
