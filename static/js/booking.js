let selectedSeats = [];
let selectedCombos = {};
let currentShowtimeId = null;
let ticketPrice = 0;

/* =========================
   CHỌN SUẤT CHIẾU
========================= */
function selectShowtime(btn) {
    document.querySelectorAll('.showtime-btn')
        .forEach(b => b.classList.remove('active'));

    btn.classList.add('active');

    currentShowtimeId = btn.dataset.id;
    ticketPrice = parseInt(btn.dataset.price);

    document.getElementById('room-info').style.display = 'block';
    document.getElementById('room-info').innerText =
        "📍 Phòng chiếu: " + btn.dataset.room;

    fetchSeats(currentShowtimeId);
}

/* =========================
   GHẾ NGỒI
========================= */
async function fetchSeats(id) {
    const grid = document.getElementById('seats-grid');
    grid.innerHTML = 'Đang tải ghế...';

    const res = await fetch('/api/get_seats/' + id);
    const data = await res.json();

    renderSeats(data.all_seats, data.occupied_seats);
}

function renderSeats(all, occupied) {
    const grid = document.getElementById('seats-grid');
    grid.innerHTML = '';
    selectedSeats = [];

    all.forEach(s => {
        const seat = document.createElement('div');
        seat.className = 'seat';
        seat.innerText = s.label;

        if (occupied.includes(s.id)) {
            seat.classList.add('occupied');
        } else {
            seat.onclick = () => toggleSeat(seat, s.id);
        }

        grid.appendChild(seat);
    });

    updateBill();
}

function toggleSeat(div, id) {
    div.classList.toggle('selected');

    if (div.classList.contains('selected')) {
        selectedSeats.push(id);
    } else {
        selectedSeats = selectedSeats.filter(s => s !== id);
    }

    updateBill();
}

/* =========================
   COMBO ĐỒ ĂN
========================= */
document.addEventListener('DOMContentLoaded', () => {
    loadCombos();
});

async function loadCombos() {
    const res = await fetch('/api/combos');
    const combos = await res.json();
    renderCombos(combos);
}

function renderCombos(combos) {
    const container = document.getElementById('combo-list');
    container.innerHTML = '';

    combos.forEach(c => {
        selectedCombos[c.id] = 0;

        container.innerHTML += `
            <div class="combo-item">
                <img src="/static/images/${c.image}" class="combo-img">
                <div class="combo-info">
                    <h4>${c.name}</h4>
                    <p>${c.description}</p>
                    <span>${c.price.toLocaleString()}₫</span>
                </div>
                <div class="combo-actions">
                    <button onclick="changeCombo(${c.id}, ${c.price}, -1)">−</button>
                    <span id="combo-${c.id}">0</span>
                    <button onclick="changeCombo(${c.id}, ${c.price}, 1)">+</button>
                </div>
            </div>
        `;
    });
}

function changeCombo(id, price, delta) {
    selectedCombos[id] += delta;
    if (selectedCombos[id] < 0) selectedCombos[id] = 0;

    document.getElementById(`combo-${id}`).innerText =
        selectedCombos[id];

    updateBill();
}

/* =========================
   TÍNH TIỀN
========================= */
function updateBill() {
    let ticketTotal = selectedSeats.length * ticketPrice;
    let comboTotal = 0;

    for (let id in selectedCombos) {
        comboTotal += selectedCombos[id] *
            document.querySelector(`#combo-${id}`)
                ?.parentElement
                ?.previousElementSibling
                ?.querySelector('span')
                ?.innerText
                ?.replace(/\D/g, '') || 0;
    }

    document.getElementById('bill-seat-text').innerText =
        `Vé (${selectedSeats.length} ghế)`;

    document.getElementById('bill-seat-price').innerText =
        ticketTotal.toLocaleString() + '₫';

    document.getElementById('total-amount').innerText =
        (ticketTotal + comboTotal).toLocaleString() + '₫';
}

/* =========================
   THANH TOÁN
========================= */
async function checkout() {
    if (!currentShowtimeId || selectedSeats.length === 0) {
        alert('Vui lòng chọn suất chiếu và ghế!');
        return;
    }

    const res = await fetch('/api/create_booking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            showtime_id: currentShowtimeId,
            seats: selectedSeats,
            combos: selectedCombos
        })
    });

    const data = await res.json();

    if (data.success) {
        alert('🎉 Đặt vé thành công!');
        window.location.href = '/';
    } else {
        alert(data.error);
    }
}

document.getElementById('btn-checkout').onclick = checkout;
