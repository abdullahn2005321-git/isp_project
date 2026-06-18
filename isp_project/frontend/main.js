// -------------------------
// Global Variables
// -------------------------
const API_URL = (() => {
    if (window.location.protocol.startsWith('http')) {
        const host = window.location.hostname;
        const port = window.location.port ? `:${window.location.port}` : '';
        return `${window.location.protocol}//${host}${port}/api`;
    }
    return 'http://127.0.0.1:5000/api';
})();

let actionModal;
let addSubModal;
let editSubModal;
let addAreaModal;
let selectedSubscriberId = null;
let selectedSubscriberData = null;
let allSubscribers = [];
let allLogs = [];
let allAreas = [];
let currentSubscriberDebt = 0;

const dom = {
    loginPage: document.getElementById('loginPage'),
    appContainer: document.getElementById('appContainer'),
    loginForm: document.getElementById('loginForm'),
    loginUsername: document.getElementById('loginUsername'),
    loginPassword: document.getElementById('loginPassword'),
    loginMessage: document.getElementById('loginMessage'),
    btnLogout: document.getElementById('btnLogout'),
    totalSubscribers: document.getElementById('total-subscribers'),
    todayIncome: document.getElementById('today-income'),
    totalDebt: document.getElementById('total-debt'),
    searchInput: document.getElementById('searchInput'),
    subscribersTableBody: document.getElementById('subscribers-table-body'),
    logsTableBody: document.getElementById('logs-table-body'),
    tabDashboard: document.getElementById('tab-dashboard'),
    tabSubscribers: document.getElementById('tab-subscribers'),
    tabAreas: document.getElementById('tab-areas'),
    tabLogs: document.getElementById('tab-logs'),
    dashboardSection: document.getElementById('dashboard'),
    subscribersSection: document.getElementById('subscribers'),
    areasSection: document.getElementById('areas'),
    logsSection: document.getElementById('logs'),
    btnTodayPromises: document.getElementById('btn-today-promises'),
    btnAddSubscriber: document.getElementById('btn-add-subscriber'),
    btnAddArea: document.getElementById('btn-add-area'),
    btnSaveArea: document.getElementById('btn-save-area'),
    newAreaName: document.getElementById('newAreaName'),
    btnAll: document.getElementById('btn-all'),
    btnPayments: document.getElementById('btn-payments'),
    btnRenewals: document.getElementById('btn-renewals'),
    btnCopyDetails: document.getElementById('btn-copy-details'),
    btnDeleteSub: document.getElementById('btn-delete-sub'),
    btnEditSub: document.getElementById('btn-edit-sub'),
    btnSaveEdit: document.getElementById('btn-save-edit'),
    btnSaveNew: document.getElementById('btn-save-new'),
    confirmBtn: document.getElementById('confirmBtn'),
    quickPromiseInput: document.getElementById('quick-detail-promise'),
    amountInput: document.getElementById('amountInput'),
    fullDebtBtn: document.getElementById('fullDebtBtn'),
    isCashCheckbox: document.getElementById('isCashCheckbox'),
    cashPaymentDiv: document.getElementById('cashPaymentDiv'),
    promiseDateInput: document.getElementById('promiseDate'),
    addSubscriberForm: document.getElementById('addSubscriberForm'),
    editSubscriberForm: document.getElementById('editSubscriberForm'),
    addAreaId: document.getElementById('addAreaId'),
    editAreaId: document.getElementById('editAreaId'),
    detailName: document.getElementById('detail-name'),
    detailId: document.getElementById('detail-id'),
    detailArea: document.getElementById('detail-area'),
    detailPhone: document.getElementById('detail-phone'),
    detailParentCompany: document.getElementById('detail-parent-company'),
    detailBalance: document.getElementById('detail-balance'),
    detailNotes: document.getElementById('detail-notes'),
    areasTableBody: document.getElementById('areas-table-body')
};

function buildUrl(endpoint) {
    const trimmed = endpoint.trim();
    const normalized = trimmed.startsWith('/api') ? trimmed.slice(4) : trimmed;
    return normalized.startsWith('/') ? `${API_URL}${normalized}` : `${API_URL}/${normalized}`;
}

function requestOptions(method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('token');
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    const options = { method, headers };
    if (body !== null) {
        options.body = JSON.stringify(body);
    }
    return options;
}

async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const response = await fetch(buildUrl(endpoint), requestOptions(method, body));
        if (response.status === 401) {
            localStorage.removeItem('token');
            showLogin();
            alert('لا تملك صلاحية للوصول! يرجى تسجيل الدخول أولاً.');
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error('Network Error:', error);
        return null;
    }
}

function showAlert(message) {
    alert(message);
}

function showLogin() {
    dom.loginPage.classList.remove('d-none');
    dom.appContainer.classList.add('d-none');
    dom.btnLogout.classList.add('d-none');
    dom.loginMessage.innerText = '';
    dom.loginForm.reset();
}

function showApp() {
    dom.loginPage.classList.add('d-none');
    dom.appContainer.classList.remove('d-none');
    dom.btnLogout.classList.remove('d-none');
}

function initPage() {
    actionModal = new bootstrap.Modal(document.getElementById('actionModal'));
    addSubModal = new bootstrap.Modal(document.getElementById('addSubscriberModal'));
    editSubModal = new bootstrap.Modal(document.getElementById('editSubscriberModal'));
    addAreaModal = new bootstrap.Modal(document.getElementById('addAreaModal'));
    registerEventListeners();
    loadInitialState();
}

function registerEventListeners() {
    dom.loginForm.addEventListener('submit', handleLogin);
    dom.btnLogout.addEventListener('click', logoutUser);
    dom.tabDashboard.addEventListener('click', () => switchSection('dashboard'));
    dom.tabSubscribers.addEventListener('click', () => switchSection('subscribers'));
    dom.tabAreas.addEventListener('click', () => switchSection('areas'));
    dom.tabLogs.addEventListener('click', () => switchSection('logs'));
    dom.searchInput.addEventListener('input', filterSubscribers);
    dom.btnTodayPromises.addEventListener('click', loadPromisesToday);
    dom.btnAddSubscriber.addEventListener('click', openAddSubscriberModal);
    dom.btnAddArea.addEventListener('click', () => addAreaModal.show());
    dom.btnSaveArea.addEventListener('click', submitNewArea);
    dom.btnAll.addEventListener('click', () => filterLogs('الكل'));
    dom.btnPayments.addEventListener('click', () => filterLogs('تسديد'));
    dom.btnRenewals.addEventListener('click', () => filterLogs('تجديد'));
    dom.btnCopyDetails.addEventListener('click', copySubscriberDetails);
    dom.btnDeleteSub.addEventListener('click', () => {
        if (selectedSubscriberId !== null) deleteSubscriber(selectedSubscriberId);
    });
    dom.btnEditSub.addEventListener('click', () => {
        if (selectedSubscriberData) openEditModal(selectedSubscriberData);
    });
    dom.btnSaveEdit.addEventListener('click', submitEditSubscriber);
    dom.btnSaveNew.addEventListener('click', submitNewSubscriber);
    dom.confirmBtn.addEventListener('click', submitAction);
    dom.quickPromiseInput.addEventListener('change', quickUpdatePromise);
    dom.fullDebtBtn.addEventListener('click', setFullDebtAmount);
    document.querySelectorAll('[data-quick-amount]').forEach((button) => {
        button.addEventListener('click', () => setQuickAmount(parseInt(button.dataset.quickAmount, 10)));
    });
}

function loadInitialState() {
    const token = localStorage.getItem('token');
    if (token) {
        showApp();
        loadPageData();
    } else {
        showLogin();
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const username = dom.loginUsername.value.trim();
    const password = dom.loginPassword.value.trim();

    if (!username || !password) {
        dom.loginMessage.innerText = 'يرجى إدخال اسم المستخدم وكلمة المرور.';
        return;
    }

    const response = await apiCall('/login', 'POST', { username, password });
    if (response && response.token) {
        localStorage.setItem('token', response.token);
        dom.loginMessage.innerText = '';
        showApp();
        loadPageData();
    } else {
        dom.loginMessage.innerText = response?.message || 'فشل تسجيل الدخول. حاول مرة أخرى.';
    }
}

function logoutUser() {
    localStorage.removeItem('token');
    showLogin();
}

function loadPageData() {
    loadSubscribers();
    loadDailyReport();
    loadLogs();
    loadAreas();
}

async function loadAreas() {
    try {
        const data = await apiCall('/areas');
        if (!data || data.status !== 'success') return;
        allAreas = data.areas;
        renderAreaOptions(allAreas);
        renderAreasTable(allAreas);
    } catch (error) {
        console.error('خطأ في جلب المناطق:', error);
    }
}

function renderAreaOptions(areas) {
    let optionsHTML = '<option value="" disabled selected>اختر المنطقة...</option>';
    areas.forEach((area) => {
        optionsHTML += `<option value="${area.id}">${area.name}</option>`;
    });
    dom.addAreaId.innerHTML = optionsHTML;
    dom.editAreaId.innerHTML = optionsHTML;
}

function renderAreasTable(areas) {
    dom.areasTableBody.innerHTML = '';
    if (!areas.length) {
        dom.areasTableBody.innerHTML = '<tr><td colspan="2" class="text-muted p-4">لا توجد مناطق مسجلة بعد.</td></tr>';
        return;
    }
    areas.forEach((area, index) => {
        dom.areasTableBody.innerHTML += `
            <tr>
                <td>${index + 1}</td>
                <td>${area.name}</td>
            </tr>
        `;
    });
}

async function submitNewArea() {
    const name = dom.newAreaName.value.trim();
    if (!name) {
        showAlert('يرجى إدخال اسم المنطقة.');
        return;
    }
    const data = await apiCall('/areas', 'POST', { name });
    if (data && data.status === 'success') {
        addAreaModal.hide();
        dom.newAreaName.value = '';
        showAlert(data.message);
        loadAreas();
    } else {
        showAlert(data?.message || 'فشل إنشاء المنطقة.');
    }
}

async function loadSubscribers() {
    try {
        const data = await apiCall('/subscribers');
        if (!data || data.status !== 'success') return;
        const subscribersList = data.subscribers || [];
        allSubscribers = subscribersList;
        dom.totalSubscribers.innerText = allSubscribers.length;
        renderTable(allSubscribers);
    } catch (error) {
        console.error('خطأ:', error);
    }
}

function filterSubscribers() {
    const query = dom.searchInput.value.toLowerCase().trim();
    if (!query) {
        renderTable(allSubscribers);
        return;
    }
    const filtered = allSubscribers.filter((sub) => {
        const nameMatch = sub.name && sub.name.toLowerCase().includes(query);
        const phoneMatch = (sub.phone_number || '').includes(query);
        return nameMatch || phoneMatch;
    });
    renderTable(filtered);
}

function createSubscriberRow(sub) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td class="sub-id"></td>
        <td class="fw-bold">
            <span class="text-primary text-decoration-underline subscriber-name" style="cursor: pointer;"></span><br>
            <small class="text-muted promise-date" style="font-size:11px;"></small>
        </td>
        <td><span class="text-secondary area-name"></span></td>
        <td dir="ltr"><span class="badge balance-badge fs-6"></span></td>
        <td>
            <button type="button" class="btn btn-sm btn-outline-success me-1 fw-bold renew-btn">تجديد</button>
            <button type="button" class="btn btn-sm btn-outline-primary fw-bold payment-btn">تسديد</button>
        </td>
    `;
    tr.querySelector('.sub-id').textContent = sub.id;
    const nameEl = tr.querySelector('.subscriber-name');
    nameEl.textContent = sub.name || '-';
    nameEl.addEventListener('click', () => showSubscriberDetails(sub.id));
    tr.querySelector('.promise-date').textContent = sub.promise_date && sub.promise_date !== 'None' ? `🗓️ وعد: ${sub.promise_date}` : '';
    tr.querySelector('.area-name').textContent = sub.area_name || sub.area_id || '-';
    const balanceBadge = tr.querySelector('.balance-badge');
    balanceBadge.textContent = sub.balance.toLocaleString();
    balanceBadge.classList.add(sub.balance < 0 ? 'bg-danger' : 'bg-success');
    tr.querySelector('.renew-btn').addEventListener('click', () => openModal(sub.id, sub.name, 'renewal', sub.balance));
    tr.querySelector('.payment-btn').addEventListener('click', () => openModal(sub.id, sub.name, 'payment', sub.balance));
    return tr;
}

function renderTable(list) {
    dom.subscribersTableBody.innerHTML = '';
    let totalDebt = 0;
    if (!list.length) {
        dom.subscribersTableBody.innerHTML = '<tr><td colspan="5" class="text-muted p-4">لا توجد بيانات للعرض</td></tr>';
        dom.totalDebt.innerText = '0 د.ع';
        return;
    }
    list.forEach((sub) => {
        if (sub.balance < 0) totalDebt += Math.abs(sub.balance);
        dom.subscribersTableBody.appendChild(createSubscriberRow(sub));
    });
    dom.totalDebt.innerText = `${totalDebt.toLocaleString()} د.ع`;
}

function openAddSubscriberModal() {
    dom.addSubscriberForm.reset();
    addSubModal.show();
}

async function submitNewSubscriber() {
    const name = document.getElementById('addName').value.trim();
    const phone = document.getElementById('addPhone').value.trim();
    const areaId = dom.addAreaId.value;
    const balance = document.getElementById('addBalance').value || 0;
    const parentCompany = document.getElementById('addParentCompany').value.trim();
    const promiseDate = document.getElementById('addPromiseDate').value;
    const notes = document.getElementById('addNotes').value.trim();
    if (!name || !phone || !areaId) {
        showAlert('يرجى تعبئة الحقول الإجبارية (الاسم، الهاتف، المنطقة)!');
        return;
    }
    const newSubscriberData = {
        name,
        phone_number: phone,
        area_id: parseInt(areaId, 10),
        balance: parseFloat(balance),
        parent_company_id: parentCompany,
        promise_date: promiseDate,
        notes
    };
    try {
        const data = await apiCall('/subscribers', 'POST', newSubscriberData);
        if (data && data.status === 'success') {
            addSubModal.hide();
            showAlert(data.message);
            loadSubscribers();
            loadDailyReport();
        } else {
            showAlert(`❌ خطأ: ${data ? data.message : 'تعذر حفظ المشترك.'}`);
        }
    } catch (error) {
        showAlert('❌ حدث خطأ في الاتصال بالسيرفر!');
        console.error('Error:', error);
    }
}

async function showSubscriberDetails(subscriberId) {
    selectedSubscriberId = subscriberId;
    selectedSubscriberData = null;
    dom.detailName.innerText = 'جاري التحميل...';
    dom.detailId.innerText = `ID: ${subscriberId}`;
    dom.detailArea.innerText = '-';
    dom.detailPhone.innerText = '-';
    dom.detailParentCompany.innerText = '-';
    dom.detailBalance.innerText = '-';
    dom.quickPromiseInput.value = '';
    dom.detailNotes.innerText = 'جاري جلب الملاحظات...';
    dom.detailNotes.className = 'm-0 text-muted small fst-italic';
    const detailsModal = new bootstrap.Modal(document.getElementById('detailsModal'));
    detailsModal.show();
    try {
        const data = await apiCall(`/subscribers/${subscriberId}`);
        if (!data || data.status !== 'success') {
            dom.detailName.innerText = '❌ حدث خطأ!';
            showAlert(data ? data.message : 'تعذر جلب تفاصيل المشترك.');
            return;
        }
        const sub = data.subscriber;
        selectedSubscriberData = sub;
        dom.detailName.innerText = sub.name;
        dom.detailArea.innerText = sub.area || sub.area_name || '-';
        dom.detailParentCompany.innerText = sub.parent_company_id && sub.parent_company_id !== 'None' ? sub.parent_company_id : '—';
        dom.detailBalance.innerText = `${sub.balance.toLocaleString()} د.ع`;
        dom.detailBalance.className = sub.balance < 0 ? 'fw-bold fs-5 text-danger' : 'fw-bold fs-5 text-success';
        dom.quickPromiseInput.value = sub.promise_date && sub.promise_date !== 'None' ? sub.promise_date.substring(0, 10) : '';
        if (!sub.phone || sub.phone === 'لا يوجد رقم مسجل') {
            dom.detailPhone.innerHTML = '<span class="text-danger small">لا يوجد رقم مسجل</span>';
        } else {
            dom.detailPhone.innerText = sub.phone;
            dom.detailPhone.className = 'fw-bold text-dark';
        }
        if (sub.notes && sub.notes.trim() !== '' && sub.notes !== 'None') {
            dom.detailNotes.innerText = sub.notes;
            dom.detailNotes.className = 'm-0 text-dark small fw-semibold';
        } else {
            dom.detailNotes.innerText = 'لا توجد ملاحظات مسجلة لهذا المشترك.';
            dom.detailNotes.className = 'm-0 text-muted small fst-italic';
        }
    } catch (error) {
        console.error('خطأ:', error);
        dom.detailName.innerText = '❌ خطأ في الاتصال';
    }
}

function openEditModal(sub) {
    const detailsModal = bootstrap.Modal.getInstance(document.getElementById('detailsModal'));
    if (detailsModal) detailsModal.hide();
    document.getElementById('editSubId').value = sub.id;
    document.getElementById('editName').value = sub.name;
    document.getElementById('editPhone').value = sub.phone === 'لا يوجد رقم مسجل' ? '' : sub.phone || '';
    dom.editAreaId.value = sub.area_id;
    document.getElementById('editParentCompany').value = sub.parent_company_id || '';
    document.getElementById('editNotes').value = sub.notes || '';
    document.getElementById('editPromiseDate').value = sub.promise_date && sub.promise_date !== 'None' && sub.promise_date !== 'لا يوجد وعد مسجل' ? sub.promise_date : '';
    editSubModal.show();
}

async function submitEditSubscriber() {
    const subId = document.getElementById('editSubId').value;
    const updatedData = {
        name: document.getElementById('editName').value.trim(),
        phone_number: document.getElementById('editPhone').value.trim(),
        area_id: parseInt(dom.editAreaId.value, 10),
        parent_company_id: document.getElementById('editParentCompany').value.trim(),
        notes: document.getElementById('editNotes').value.trim(),
        promise_date: document.getElementById('editPromiseDate').value || null
    };
    try {
        const data = await apiCall(`/subscribers/${subId}`, 'PUT', updatedData);
        if (data && data.status === 'success') {
            editSubModal.hide();
            showAlert(`✅ ${data.message}`);
            loadSubscribers();
        } else {
            showAlert(`❌ خطأ: ${data ? data.message : 'تعذر حفظ التعديلات.'}`);
        }
    } catch (error) {
        showAlert('❌ حدث خطأ في الاتصال بالسيرفر!');
        console.error('Error:', error);
    }
}

async function deleteSubscriber(subId) {
    if (!confirm('⚠️ تحذير: هل أنت متأكد أنك تريد حذف هذا المشترك نهائياً؟ لا يمكن التراجع عن هذا الإجراء!')) return;
    try {
        const data = await apiCall(`/subscribers/${subId}`, 'DELETE');
        if (data && data.status === 'success') {
            const detailsModal = bootstrap.Modal.getInstance(document.getElementById('detailsModal'));
            if (detailsModal) detailsModal.hide();
            showAlert(`🗑️ ${data.message}`);
            loadSubscribers();
        } else {
            showAlert(`❌ خطأ: ${data ? data.message : 'تعذر حذف المشترك.'}`);
        }
    } catch (error) {
        showAlert('❌ حدث خطأ في الاتصال بالسيرفر!');
        console.error('Error:', error);
    }
}

async function loadPromisesToday() {
    try {
        const data = await apiCall('/promises_today');
        if (!data) return;
        if (data.status === 'success') {
            if (data.count === 0) {
                showAlert('لا توجد وعود مستحقة لهذا اليوم! 🎉');
                loadSubscribers();
            } else {
                renderTable(data.subscribers);
                showAlert(`تم العثور على ${data.count} وعود مستحقة اليوم!`);
            }
        }
    } catch (error) {
        showAlert('❌ حدث خطأ في جلب الوعود من السيرفر!');
        console.error(error);
    }
}

async function loadLogs() {
    try {
        const data = await apiCall('/logs');
        if (!data) return;
        if (data.status === 'success') {
            allLogs = data.logs;
            renderLogsTable(allLogs);
            dom.btnAll.checked = true;
        }
    } catch (error) {
        console.error('Error loading logs:', error);
        dom.logsTableBody.innerHTML = '<tr><td colspan="4" class="text-danger p-4">❌ خطأ في الاتصال وجلب السجل</td></tr>';
    }
}

function renderLogsTable(logsArray) {
    dom.logsTableBody.innerHTML = '';
    if (!logsArray.length) {
        dom.logsTableBody.innerHTML = '<tr><td colspan="4" class="text-muted p-4">لا توجد عمليات مطابقة للعرض.</td></tr>';
        return;
    }
    logsArray.forEach((log) => {
        const badgeClass = log.type === 'تسديد' ? 'bg-primary' : 'bg-success';
        const icon = log.type === 'تسديد' ? 'fa-hand-holding-dollar' : 'fa-wifi';
        dom.logsTableBody.innerHTML += `
            <tr>
                <td dir="ltr" class="text-muted small">${log.date}</td>
                <td class="fw-bold text-dark">${log.subscriber_name}</td>
                <td><span class="badge ${badgeClass} fs-6"><i class="fa-solid ${icon}"></i> ${log.type}</span></td>
                <td class="fw-bold fs-6">${log.amount.toLocaleString()} د.ع</td>
            </tr>
        `;
    });
}

function filterLogs(filterType) {
    if (filterType === 'الكل') {
        renderLogsTable(allLogs);
    } else {
        renderLogsTable(allLogs.filter((log) => log.type === filterType));
    }
}

async function loadDailyReport() {
    try {
        const data = await apiCall('/daily_report');
        if (!data) return;
        const netTotal = data.summary ? data.summary.net_total : 0;
        dom.todayIncome.innerText = `${netTotal.toLocaleString()} د.ع`;
    } catch (error) {
        console.error('خطأ:', error);
    }
}

async function submitAction() {
    const subscriberId = document.getElementById('modal-subscriber-id').value;
    const actionType = document.getElementById('modal-action-type').value;
    const amount = dom.amountInput.value;
    const promiseDate = dom.promiseDateInput.value;
    const isCash = dom.isCashCheckbox.checked;
    if (!amount || Number(amount) <= 0) {
        return showAlert('يرجى إدخال مبلغ صحيح!');
    }
    const endpoint = actionType === 'payment' ? '/payments' : '/renewals';
    const requestData = {
        subscriber_id: parseInt(subscriberId, 10),
        amount: parseFloat(amount),
        promise_date: promiseDate,
        is_cash: isCash
    };
    try {
        const data = await apiCall(endpoint, 'POST', requestData);
        if (data && data.status === 'success') {
            actionModal.hide();
            loadSubscribers();
            loadDailyReport();
            loadLogs();
        } else {
            showAlert(`❌ تنبيه: ${data ? data.message : 'تعذر تنفيذ العملية.'}`);
        }
    } catch (error) {
        showAlert('❌ خطأ في الاتصال بالسيرفر!');
    }
}

function switchSection(sectionName) {
    document.querySelectorAll('.section-content').forEach((el) => el.classList.remove('active'));
    document.querySelectorAll('.nav-tabs .nav-link').forEach((el) => el.classList.remove('active'));
    document.getElementById(sectionName).classList.add('active');
    document.getElementById(`tab-${sectionName}`).classList.add('active');
}

function openModal(subscriberId, subscriberName, actionType, currentBalance) {
    currentSubscriberDebt = currentBalance < 0 ? Math.abs(currentBalance) : 0;
    const titleLabel = document.getElementById('actionModalLabel');
    const confirmBtn = dom.confirmBtn;
    if (actionType === 'payment') {
        titleLabel.innerHTML = '<i class="fa-solid fa-hand-holding-dollar text-primary"></i> تسديد مبلغ';
        confirmBtn.className = 'btn btn-primary w-100 py-2 fw-bold fs-5';
        dom.cashPaymentDiv.style.display = 'none';
    } else {
        titleLabel.innerHTML = '<i class="fa-solid fa-wifi text-success"></i> تجديد اشتراك';
        confirmBtn.className = 'btn btn-success w-100 py-2 fw-bold fs-5';
        dom.cashPaymentDiv.style.display = 'block';
        dom.isCashCheckbox.checked = false;
    }
    document.getElementById('modal-subscriber-name').innerText = subscriberName;
    dom.amountInput.value = '';
    dom.promiseDateInput.value = '';
    document.getElementById('modal-subscriber-id').value = subscriberId;
    document.getElementById('modal-action-type').value = actionType;
    actionModal.show();
}

function setQuickAmount(amount) {
    dom.amountInput.value = amount;
}

function setFullDebtAmount() {
    if (currentSubscriberDebt > 0) {
        dom.amountInput.value = currentSubscriberDebt;
    } else {
        showAlert('هذا المشترك ليس عليه دين ليتم تسديده!');
    }
}

async function quickUpdatePromise() {
    if (!selectedSubscriberId) return;
    const updatedData = { promise_date: dom.quickPromiseInput.value || null };
    try {
        const data = await apiCall(`/subscribers/${selectedSubscriberId}`, 'PUT', updatedData);
        if (data && data.status === 'success') {
            loadSubscribers();
        } else {
            console.error('خطأ في تحديث الوعد:', data ? data.message : 'No response');
        }
    } catch (error) {
        console.error('حدث خطأ في الاتصال أثناء تحديث الوعد:', error);
    }
}

function copySubscriberDetails() {
    const id = dom.detailId.innerText.replace('ID: ', '').trim();
    const name = dom.detailName.innerText;
    const area = dom.detailArea.innerText;
    const phone = dom.detailPhone.innerText;
    const parentCompany = dom.detailParentCompany.innerText;
    const balance = dom.detailBalance.innerText;
    const promiseDate = dom.quickPromiseInput.value || 'لا يوجد';
    const notes = dom.detailNotes.innerText;
    const textToCopy = `ID: ${id}\nالاسم: ${name}\nالمنطقة: ${area}\nرقم الهاتف: ${phone}\nالشركة الأم: ${parentCompany}\nالرصيد الحالي: ${balance}\nوعد التسديد: ${promiseDate}\nملاحظات: ${notes}`;
    navigator.clipboard.writeText(textToCopy)
        .then(() => showAlert('تم نسخ معلومات المشترك إلى الحافظة.'))
        .catch((error) => {
            console.error('خطأ في نسخ المعلومات:', error);
            showAlert('تعذر نسخ المعلومات. الرجاء المحاولة مرة أخرى.');
        });
}

window.addEventListener('DOMContentLoaded', initPage);
