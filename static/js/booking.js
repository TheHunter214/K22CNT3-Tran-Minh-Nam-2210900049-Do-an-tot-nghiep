let selectedSeats = [];
let selectedCombos = {}; // { comboId: qty }
let comboData = [];
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

    const roomInfo = document.getElementById('room-info');
    roomInfo.style.display = 'block';
    roomInfo.innerText = "📍 Phòng chiếu: " + btn.dataset.room;

    fetchSeats(currentShowtimeId);
}

/* =========================
   GHẾ NGỒI
========================= */
async function fetchSeats(id) {
    const grid = document.getElementById('seats-grid');
    grid.innerHTML = `<p style="grid-column:1/-1;text-align:center">Đang tải ghế...</p>`;

    try {
        const res = await fetch('/api/get_seats/' + id);
        const data = await res.json();
        renderSeats(data.all_seats, data.occupied_seats);
    } catch {
        grid.innerHTML = `<p style="grid-column:1/-1;color:red">Lỗi tải ghế</p>`;
    }
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

function toggleSeat(el, id) {
    el.classList.toggle('selected');

    if (el.classList.contains('selected')) {
        selectedSeats.push(id);
    } else {
        selectedSeats = selectedSeats.filter(s => s !== id);
    }

    updateBill();
}

/* =========================
   COMBO
========================= */
document.addEventListener('DOMContentLoaded', loadCombos);

async function loadCombos() {
    try {
        const res = await fetch('/api/combos');
        comboData = await res.json();
        renderCombos();
    } catch (e) {
        console.error('Lỗi load combo', e);
    }
}

function renderCombos() {
    const container = document.getElementById('combo-list');
    if (!container) return;

    container.innerHTML = '';

    comboData.forEach(c => {
        if (!selectedCombos[c.id]) selectedCombos[c.id] = 0;

        container.innerHTML += `
            <div class="combo-item">
                <div class="combo-info">
                    <h4>${c.name}</h4>
                    <p>${c.description}</p>
                    <strong>${c.price.toLocaleString()}₫</strong>
                </div>
                <div class="combo-actions">
                    <button onclick="changeCombo(${c.id}, -1)">−</button>
                    <span id="combo-qty-${c.id}">${selectedCombos[c.id]}</span>
                    <button onclick="changeCombo(${c.id}, 1)">+</button>
                </div>
            </div>
        `;
    });
}

function changeCombo(id, delta) {
    selectedCombos[id] += delta;
    if (selectedCombos[id] < 0) selectedCombos[id] = 0;

    document.getElementById(`combo-qty-${id}`).innerText = selectedCombos[id];
    updateBill();
}

/* =========================
   TÍNH TIỀN
========================= */
function updateBill() {
    const ticketTotal = selectedSeats.length * ticketPrice;

    let comboTotal = 0;
    for (let id in selectedCombos) {
        const qty = selectedCombos[id];
        const combo = comboData.find(c => c.id == id);
        if (combo && qty > 0) {
            comboTotal += combo.price * qty;
        }
    }

    document.getElementById('bill-seat-text').innerText =
        `Vé (${selectedSeats.length} ghế)`;

    document.getElementById('bill-seat-price').innerText =
        ticketTotal.toLocaleString() + '₫';

    document.getElementById('bill-combo-price').innerText =
        comboTotal.toLocaleString() + '₫';

    document.getElementById('total-amount').innerText =
        (ticketTotal + comboTotal).toLocaleString() + '₫';
}

/* =========================
   THANH TOÁN
========================= */
async function checkout() {
    if (!currentShowtimeId) return alert('Chọn suất chiếu');
    if (selectedSeats.length === 0) return alert('Chọn ghế');

    const combos = {};
    for (let id in selectedCombos) {
        if (selectedCombos[id] > 0) combos[id] = selectedCombos[id];
    }

    const res = await fetch('/api/create_booking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            showtime_id: currentShowtimeId,
            seats: selectedSeats,
            combos: combos
        })
    });

    const data = await res.json();
    if (data.success) {
        alert('🎉 Đặt vé thành công!');
        location.href = '/';
    } else {
        alert(data.error || 'Có lỗi xảy ra');
    }
}
