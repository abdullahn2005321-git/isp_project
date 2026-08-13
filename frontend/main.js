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
let addStaffModal;
let logFilterModal;
let selectedSubscriberId = null;
let selectedSubscriberData = null;
let allSubscribers = [];
let allLogs = [];
let allAreas = [];
let currentSubscriberDebt = 0;
let currentSubscriberPage = 1;
let totalSubscriberPages = 1;
let currentLogsPage = 1;
let totalLogsPages = 1;
let currentLogFilter = 'الكل';
let logFilterStartDate = '';
let logFilterEndDate = '';
const subscribersPerPage = 50;
const logsPerPage = 100;

const dom = {
    loginPage: document.getElementById('loginPage'),
    appContainer: document.getElementById('appContainer'),
    loginForm: document.getElementById('loginForm'),
    loginUsername: document.getElementById('loginUsername'),
    loginPassword: document.getElementById('loginPassword'),
    loginMessage: document.getElementById('loginMessage'),
    btnLogout: document.getElementById('btnLogout'),
    btnProfileInfo: document.getElementById('btnProfileInfo'),
    profileInfoCard: document.getElementById('profileInfoCard'),
    profileUsername: document.getElementById('profileUsername'),
    profileRole: document.getElementById('profileRole'),
    profileAreasCount: document.getElementById('profileAreasCount'),
    btnProfileAreas: document.getElementById('btnProfileAreas'),
    btnMyTeam: document.getElementById('btnMyTeam'),
    btnAddStaffProfile: document.getElementById('btnAddStaffProfile'),
    teamAddStaffWrapper: document.getElementById('teamAddStaffWrapper'),
    totalSubscribers: document.getElementById('total-subscribers'),
    todayIncome: document.getElementById('today-income'),
    totalDebt: document.getElementById('total-debt'),
    searchInput: document.getElementById('searchInput'),
    subscribersTableBody: document.getElementById('subscribers-table-body'),
    logsTableBody: document.getElementById('logs-table-body'),
    tabDashboard: document.getElementById('tab-dashboard'),
    tabSubscribers: document.getElementById('tab-subscribers'),
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
    todayPayments: document.getElementById('today-payments'),
    todayRenewals: document.getElementById('today-renewals'),
    reportStatusBadge: document.getElementById('report-status-badge'),
    reportStatusMessage: document.getElementById('report-status-msg'),
    btnOpenLogFilter: document.getElementById('btn-open-log-filter'),
    btnApplyLogFilter: document.getElementById('btnApplyLogFilter'),
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
    areasTableBody: document.getElementById('areas-table-body'),
    subscriberPageInfo: document.getElementById('subscriberPageInfo'),
    btnPrevPage: document.getElementById('btn-prev-page'),
    btnNextPage: document.getElementById('btn-next-page'),
    logsPageInfo: document.getElementById('logsPageInfo'),
    btnPrevLogsPage: document.getElementById('btn-prev-logs-page'),
    btnNextLogsPage: document.getElementById('btn-next-logs-page')
};

function buildUrl(endpoint) {
    const trimmed = endpoint.trim();
    const normalized = trimmed.startsWith('/api') ? trimmed.slice(4) : trimmed;
    return normalized.startsWith('/') ? `${API_URL}${normalized}` : `${API_URL}/${normalized}`;
}

function normalizeSubscriber(sub) {
    if (!sub || typeof sub !== 'object') return sub;

    return {
        ...sub,
        phone_number: sub.phone_number ?? sub.phone ?? '',
        phone: sub.phone ?? sub.phone_number ?? '',
        area_name: sub.area_name ?? sub.area ?? '',
        area: sub.area ?? sub.area_name ?? '',
        promise_date: sub.promise_date ?? '',
        notes: sub.notes ?? ''
    };
}

function normalizeLog(log) {
    if (!log || typeof log !== 'object') return null;

    const rawType = String(log.type ?? log.transaction_type ?? '').toLowerCase();
    const normalizedType = rawType === 'payment' || rawType === 'تسديد'
        ? 'تسديد'
        : rawType === 'renewal' || rawType === 'تجديد'
            ? 'تجديد'
            : (log.type || 'غير معروف');

    const amountValue = Number(log.amount ?? log.value ?? 0);

    return {
        type: normalizedType,
        subscriber_name: log.subscriber_name ?? log.subscriber ?? log.name ?? 'غير معروف',
        amount: Number.isFinite(amountValue) ? amountValue : 0,
        date: log.date ?? log.transaction_date ?? ''
    };
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
            showAlert('لا تملك صلاحية للوصول! يرجى تسجيل الدخول أولاً.');
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error('Network Error:', error);
        return null;
    }
}

function ensureToastContainer() {
    let container = document.getElementById('appToastContainer');
    if (container) return container;

    container = document.createElement('div');
    container.id = 'appToastContainer';
    container.className = 'toast-container position-fixed top-0 start-50 translate-middle-x p-3';
    container.style.zIndex = '2000';
    document.body.appendChild(container);
    return container;
}

function restoreModalFocus() {
    const activeModal = document.querySelector('.modal.show');
    if (!activeModal) return;

    const firstInput = activeModal.querySelector('input, select, textarea, button');
    if (firstInput && typeof firstInput.focus === 'function') {
        firstInput.focus({ preventScroll: true });
    }
}

function showAlert(message, type = 'danger') {
    const container = ensureToastContainer();
    const tone = ['success', 'warning', 'info', 'danger'].includes(type) ? type : 'danger';
    const toastEl = document.createElement('div');

    toastEl.className = `toast align-items-center text-bg-${tone} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    container.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay: 3500 });

    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    }, { once: true });

    toast.show();
    setTimeout(restoreModalFocus, 30);
}

function normalizeRole(role) {
    return typeof role === 'string' ? role.trim().toLowerCase() : '';
}

function decodeJwtRole(token) {
    if (!token) return '';
    try {
        const payload = token.split('.')[1];
        if (!payload) return '';
        const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
        const padded = normalized + '='.repeat((4 - (normalized.length % 4)) % 4);
        return JSON.parse(atob(padded))?.role || '';
    } catch (error) {
        console.warn('Unable to decode JWT role:', error);
        return '';
    }
}

function getCurrentRole() {
    const storedRole = localStorage.getItem('userRole');
    const token = localStorage.getItem('token');
    const decodedRole = decodeJwtRole(token);
    return normalizeRole(decodedRole || storedRole || 'staff');
}

function redirectForRole(role) {
    const normalizedRole = normalizeRole(role);
    if (normalizedRole === 'super_admin') {
        window.location.href = './super_dashboard.html';
        return true;
    }
    return false;
}

function showLogin() {
    dom.loginPage.classList.remove('d-none');
    dom.appContainer.classList.add('d-none');
    dom.btnProfileInfo.classList.add('d-none');
    dom.profileInfoCard.classList.add('d-none');
    dom.btnLogout.classList.add('d-none');
    dom.loginMessage.innerText = '';
    dom.loginForm.reset();
}

function showApp() {
    dom.loginPage.classList.add('d-none');
    dom.appContainer.classList.remove('d-none');
    dom.btnProfileInfo.classList.remove('d-none');
    dom.btnLogout.classList.remove('d-none');

    const userRole = getCurrentRole();
    localStorage.setItem('userRole', userRole);
    const username = localStorage.getItem('username') || 'غير معروف';
    dom.profileUsername.innerText = username;
    dom.profileRole.innerText = userRole === 'super_admin' ? 'مدير عام' : userRole === 'admin' ? 'مدير' : 'موظف';
    dom.profileAreasCount.innerText = Array.isArray(allAreas) ? allAreas.length : 0;

    const canManageStaff = userRole === 'admin' || userRole === 'super_admin';

    if (dom.btnAddStaff) {
        if (canManageStaff) {
            dom.btnAddStaff.classList.remove('d-none');
        } else {
            dom.btnAddStaff.classList.add('d-none');
        }
    }

    if (dom.teamAddStaffWrapper) {
        if (canManageStaff) {
            dom.teamAddStaffWrapper.classList.remove('d-none');
        } else {
            dom.teamAddStaffWrapper.classList.add('d-none');
        }
    }
}

function initPage() {
    actionModal = new bootstrap.Modal(document.getElementById('actionModal'));
    addSubModal = new bootstrap.Modal(document.getElementById('addSubscriberModal'));
    editSubModal = new bootstrap.Modal(document.getElementById('editSubscriberModal'));
    addAreaModal = new bootstrap.Modal(document.getElementById('addAreaModal'));
    addStaffModal = new bootstrap.Modal(document.getElementById('addStaffModal'));
    logFilterModal = new bootstrap.Modal(document.getElementById('logFilterModal'));
    registerEventListeners();
    loadInitialState();
}

function registerEventListeners() {
    dom.loginForm.addEventListener('submit', handleLogin);
    dom.btnProfileInfo.addEventListener('click', (event) => {
        event.stopPropagation();
        dom.profileInfoCard.classList.toggle('d-none');
    });
    document.addEventListener('click', (event) => {
        const clickedInsideProfile = dom.profileInfoCard.contains(event.target) || dom.btnProfileInfo.contains(event.target);
        if (!clickedInsideProfile) {
            dom.profileInfoCard.classList.add('d-none');
        }
    });
    dom.btnProfileAreas.addEventListener('click', () => {
        dom.profileInfoCard.classList.add('d-none');
        switchSection('areas');
        if (addAreaModal) addAreaModal.show();
    });
    if (dom.btnMyTeam) {
        dom.btnMyTeam.addEventListener('click', (event) => {
            event.stopPropagation();
            openTeamModal();
        });
    }
    dom.btnLogout.addEventListener('click', logoutUser);
    dom.tabDashboard.addEventListener('click', () => switchSection('dashboard'));
    dom.tabSubscribers.addEventListener('click', () => switchSection('subscribers'));
    dom.tabLogs.addEventListener('click', () => switchSection('logs'));
    dom.searchInput.addEventListener('input', filterSubscribers);
    dom.btnTodayPromises.addEventListener('click', loadPromisesToday);
    dom.btnAddSubscriber.addEventListener('click', openAddSubscriberModal);
    dom.btnAddArea.addEventListener('click', () => addAreaModal.show());
    dom.btnSaveArea.addEventListener('click', submitNewArea);
    if (dom.btnOpenLogFilter) {
        dom.btnOpenLogFilter.addEventListener('click', () => logFilterModal.show());
    }
    if (dom.btnApplyLogFilter) {
        dom.btnApplyLogFilter.addEventListener('click', () => {
            const startDate = document.getElementById('logFilterStartDate').value;
            const endDate = document.getElementById('logFilterEndDate').value;
            logFilterStartDate = startDate;
            logFilterEndDate = endDate;
            filterLogs(currentLogFilter);
            logFilterModal.hide();
        });
    }
    document.querySelectorAll('[data-log-filter]').forEach((button) => {
        button.addEventListener('click', () => {
            const filterType = button.dataset.logFilter;
            const startDate = document.getElementById('logFilterStartDate').value;
            const endDate = document.getElementById('logFilterEndDate').value;
            logFilterStartDate = startDate;
            logFilterEndDate = endDate;
            filterLogs(filterType);
            logFilterModal.hide();
        });
    });
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
    dom.btnPrevPage.addEventListener('click', () => {
        if (currentSubscriberPage > 1) loadSubscribers(currentSubscriberPage - 1, dom.searchInput.value.trim());
    });
    dom.btnNextPage.addEventListener('click', () => {
        if (currentSubscriberPage < totalSubscriberPages) loadSubscribers(currentSubscriberPage + 1, dom.searchInput.value.trim());
    });
    if (dom.btnPrevLogsPage) {
        dom.btnPrevLogsPage.addEventListener('click', () => {
            if (currentLogsPage > 1) loadLogs(currentLogsPage - 1);
        });
    }
    if (dom.btnNextLogsPage) {
        dom.btnNextLogsPage.addEventListener('click', () => {
            if (currentLogsPage < totalLogsPages) loadLogs(currentLogsPage + 1);
        });
    }
    document.querySelectorAll('[data-quick-amount]').forEach((button) => {
        button.addEventListener('click', () => setQuickAmount(parseInt(button.dataset.quickAmount, 10)));
    });
}

function loadInitialState() {
    const token = localStorage.getItem('token');
    if (token) {
        const role = getCurrentRole();
        if (redirectForRole(role)) {
            return;
        }
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
        const resolvedRole = normalizeRole(response.role || decodeJwtRole(response.token) || 'staff');
        localStorage.setItem('token', response.token);
        localStorage.setItem('userRole', resolvedRole);
        localStorage.setItem('username', response.username || username);
        dom.loginMessage.innerText = '';
        if (redirectForRole(resolvedRole)) {
            return;
        }
        showApp();
        loadPageData();
    } else {
        dom.loginMessage.innerText = response?.message || 'فشل تسجيل الدخول. حاول مرة أخرى.';
    }
}

function logoutUser() {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('username');
    dom.profileInfoCard.classList.add('d-none');
    showLogin();
}

function loadPageData() {
    loadSubscribers();
    loadAreas();
    loadLogs();
}

async function loadAreas() {
    try {
        const data = await apiCall('/areas');
        if (!data || data.status !== 'success') return;
        allAreas = data.areas;
        renderAreaOptions(allAreas);
        renderAreasTable(allAreas);
        if (dom.profileAreasCount) {
            dom.profileAreasCount.innerText = Array.isArray(allAreas) ? allAreas.length : 0;
        }
        updateDashboardSummary();
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

async function loadSubscribers(page = 1, searchQuery = '') {
    try {
        const params = new URLSearchParams({
            page: String(page),
            per_page: String(subscribersPerPage)
        });

        const trimmedQuery = (searchQuery || '').trim();
        if (trimmedQuery) {
            params.set('search', trimmedQuery);
        }

        const data = await apiCall(`/subscribers?${params.toString()}`);
        if (!data || data.status !== 'success') return;
        const subscribersList = (data.subscribers || []).map(normalizeSubscriber);
        allSubscribers = subscribersList;
        currentSubscriberPage = page;
        totalSubscriberPages = data.pagination?.total_pages || 1;
        dom.totalSubscribers.innerText = data.pagination?.total_subscribers || subscribersList.length;
        dom.totalSubscribers.dataset.total = data.pagination?.total_subscribers || subscribersList.length;
        dom.subscriberPageInfo.innerText = `صفحة ${currentSubscriberPage} من ${totalSubscriberPages}`;
        dom.btnPrevPage.disabled = currentSubscriberPage <= 1;
        dom.btnNextPage.disabled = currentSubscriberPage >= totalSubscriberPages;
        renderTable(allSubscribers);
        updateDashboardSummary();
    } catch (error) {
        console.error('خطأ:', error);
    }
}

function filterSubscribers() {
    const query = dom.searchInput.value.trim();
    loadSubscribers(1, query);
}

function createSubscriberRow(sub) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td class="sub-id"></td>
        <td class="fw-bold">
            <span class="text-primary text-decoration-underline subscriber-name" style="cursor: pointer;"></span><br>
            <small class="text-muted subscriber-phone" style="font-size:11px;"></small>
        </td>
        <td><span class="text-secondary area-name"></span></td>
        <td dir="ltr">
            <span class="badge balance-badge fs-6 d-inline-block mb-1"></span><br>
            <small class="text-muted promise-date" style="font-size:11px;"></small>
        </td>
        <td>
            <button type="button" class="btn btn-sm btn-outline-success me-1 fw-bold renew-btn">تجديد</button>
            <button type="button" class="btn btn-sm btn-outline-primary fw-bold payment-btn">تسديد</button>
        </td>
    `;

    tr.querySelector('.sub-id').textContent = sub.id;

    const nameEl = tr.querySelector('.subscriber-name');
    nameEl.textContent = sub.name || '-';
    nameEl.addEventListener('click', () => showSubscriberDetails(sub.id));

    const phoneEl = tr.querySelector('.subscriber-phone');
    const phone = sub.phone_number || sub.phone || 'لا يوجد رقم';
    phoneEl.textContent = `📞 ${phone}`;

    tr.querySelector('.area-name').textContent = sub.area_name || sub.area_id || '-';

    const balanceBadge = tr.querySelector('.balance-badge');
    const balanceValue = Number(sub.balance || 0);
    const balanceLabel = balanceValue < 0 ? 'دين' : 'رصيد';
    balanceBadge.textContent = `${balanceLabel}: ${balanceValue.toLocaleString()}`;
    balanceBadge.classList.add(balanceValue < 0 ? 'bg-danger' : 'bg-success');

    const promiseDateEl = tr.querySelector('.promise-date');
    promiseDateEl.textContent = sub.promise_date && sub.promise_date !== 'None' ? `🗓️ وعد: ${sub.promise_date}` : '🗓️ لا يوجد وعد';

    tr.querySelector('.renew-btn').addEventListener('click', () => openModal(sub.id, sub.name, 'renewal', sub.balance));
    tr.querySelector('.payment-btn').addEventListener('click', () => openModal(sub.id, sub.name, 'payment', sub.balance));
    return tr;
}

function renderTable(list) {
    dom.subscribersTableBody.innerHTML = '';
    if (!list.length) {
        dom.subscribersTableBody.innerHTML = '<tr><td colspan="5" class="text-muted p-4">لا توجد بيانات للعرض</td></tr>';
        return;
    }
    list.forEach((sub) => {
        dom.subscribersTableBody.appendChild(createSubscriberRow(sub));
    });
}

function openAddSubscriberModal() {
    dom.addSubscriberForm.reset();
    addSubModal.show();
}

async function openTeamModal() {
    dom.profileInfoCard.classList.add('d-none');
    const teamModalEl = document.getElementById('teamModal');
    const teamModalBody = document.getElementById('teamModalBody');
    if (!teamModalEl || !teamModalBody) return;

    teamModalBody.innerHTML = '<div class="text-center text-muted">جاري التحميل...</div>';
    const modal = bootstrap.Modal.getOrCreateInstance(teamModalEl);
    modal.show();

    try {
        const data = await apiCall('/my-team');
        if (!data || data.status !== 'success') {
            teamModalBody.innerHTML = '<div class="text-danger">تعذر جلب بيانات الفريق.</div>';
            return;
        }

        const manager = data.manager || {};
        const members = Array.isArray(data.members) ? data.members : [];
        const roleLabel = (role) => role === 'admin' ? 'مدير' : 'موظف';
        const userRole = localStorage.getItem('userRole');
        if (dom.teamAddStaffWrapper) {
            dom.teamAddStaffWrapper.classList.toggle('d-none', userRole !== 'admin');
        }

        teamModalBody.innerHTML = `
            <div class="mb-3">
                <div class="fw-bold text-primary mb-2"><i class="fa-solid fa-user-shield"></i> المدير</div>
                <div class="border rounded p-2 bg-light">
                    <div class="fw-semibold">${manager.username || '—'}</div>
                    <div class="small text-muted">${roleLabel(manager.role || 'admin')}</div>
                </div>
            </div>
            <div>
                <div class="fw-bold text-secondary mb-2"><i class="fa-solid fa-users"></i> الموظفون</div>
                ${members.length ? members.map((member) => `
                    <div class="border rounded p-2 mb-2">
                        <div class="fw-semibold">${member.username || '—'}</div>
                        <div class="small text-muted">${roleLabel(member.role || 'staff')}</div>
                    </div>
                `).join('') : '<div class="text-muted">لا يوجد موظفون مسجلون حتى الآن.</div>'}
            </div>
        `;
    } catch (error) {
        console.error('خطأ في تحميل فريق العمل:', error);
        teamModalBody.innerHTML = '<div class="text-danger">حدث خطأ أثناء تحميل بيانات الفريق.</div>';
    }
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
        promise_date: promiseDate || null,
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
        const sub = normalizeSubscriber(data.subscriber);
        selectedSubscriberData = sub;
        dom.detailName.innerText = sub.name;
        dom.detailArea.innerText = sub.area_name || sub.area || '-';
        dom.detailParentCompany.innerText = '—';
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
    const normalizedSub = normalizeSubscriber(sub);
    document.getElementById('editSubId').value = normalizedSub.id;
    document.getElementById('editName').value = normalizedSub.name;
    document.getElementById('editPhone').value = normalizedSub.phone === 'لا يوجد رقم مسجل' ? '' : normalizedSub.phone || '';
    dom.editAreaId.value = normalizedSub.area_id;
    document.getElementById('editNotes').value = normalizedSub.notes || '';
    document.getElementById('editPromiseDate').value = sub.promise_date && sub.promise_date !== 'None' && sub.promise_date !== 'لا يوجد وعد مسجل' ? sub.promise_date : '';
    editSubModal.show();
}

async function submitEditSubscriber() {
    const subId = document.getElementById('editSubId').value;
    const updatedData = {
        name: document.getElementById('editName').value.trim(),
        phone_number: document.getElementById('editPhone').value.trim(),
        area_id: parseInt(dom.editAreaId.value, 10),
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

async function loadLogs(page = 1) {
    try {
        const data = await apiCall(`/logs?page=${page}&per_page=${logsPerPage}`);
        if (!data) return;
        if (data.status === 'success') {
            const rawLogs = Array.isArray(data.logs)
                ? data.logs
                : (Array.isArray(data.items) ? data.items : []);

            allLogs = rawLogs
                .map(normalizeLog)
                .filter((log) => log !== null);

            currentLogsPage = data.pagination?.current_page || page;
            totalLogsPages = data.pagination?.total_pages || 1;
            if (dom.logsPageInfo) {
                dom.logsPageInfo.innerText = `صفحة ${currentLogsPage} من ${totalLogsPages}`;
            }
            if (dom.btnPrevLogsPage) {
                dom.btnPrevLogsPage.disabled = currentLogsPage <= 1;
            }
            if (dom.btnNextLogsPage) {
                dom.btnNextLogsPage.disabled = currentLogsPage >= totalLogsPages;
            }

            currentLogFilter = 'الكل';
            updateLogFilterButtonLabel();
            renderLogsTable(allLogs);
            updateDashboardSummary();
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
        const badgeClass = log.type === 'تسديد' ? 'bg-primary' : (log.type === 'تجديد' ? 'bg-success' : 'bg-secondary');
        const icon = log.type === 'تسديد' ? 'fa-hand-holding-dollar' : (log.type === 'تجديد' ? 'fa-wifi' : 'fa-circle-info');
        const displayDate = String(log.date || '').replace('T', ' ').slice(0, 19);
        dom.logsTableBody.innerHTML += `
            <tr>
                <td dir="ltr" class="text-muted small">${displayDate}</td>
                <td class="fw-bold text-dark">${log.subscriber_name}</td>
                <td><span class="badge ${badgeClass} fs-6"><i class="fa-solid ${icon}"></i> ${log.type}</span></td>
                <td class="fw-bold fs-6">${Number(log.amount || 0).toLocaleString()} د.ع</td>
            </tr>
        `;
    });
}

function updateLogFilterButtonLabel() {
    if (dom.btnOpenLogFilter) {
        dom.btnOpenLogFilter.innerText = currentLogFilter === 'الكل' ? 'تصفية' : `تصفية: ${currentLogFilter}`;
    }
}

function filterLogs(filterType) {
    currentLogFilter = filterType;
    updateLogFilterButtonLabel();

    const filteredLogs = allLogs.filter((log) => {
        const dateText = String(log.date || '');
        const logDate = dateText.includes('T') ? dateText.split('T')[0] : dateText.split(' ')[0];
        const matchesType = filterType === 'الكل' || log.type === filterType;
        const matchesStart = !logFilterStartDate || logDate >= logFilterStartDate;
        const matchesEnd = !logFilterEndDate || logDate <= logFilterEndDate;
        return matchesType && matchesStart && matchesEnd;
    });

    renderLogsTable(filteredLogs);
}

function updateDashboardSummary() {
    const totalSubscribersCount = Number(dom.totalSubscribers?.dataset?.total || allSubscribers.length || 0);
    const totalAreasCount = Array.isArray(allAreas) ? allAreas.length : 0;
    const totalDebt = allSubscribers.reduce((sum, sub) => sum + (sub.balance < 0 ? Math.abs(sub.balance) : 0), 0);

    if (dom.totalSubscribers) {
        dom.totalSubscribers.innerText = totalSubscribersCount.toLocaleString();
    }
    if (dom.profileAreasCount) {
        dom.profileAreasCount.innerText = totalAreasCount.toLocaleString();
    }
    if (dom.totalDebt) {
        dom.totalDebt.innerText = `${totalDebt.toLocaleString()} د.ع`;
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
    const endpoint = actionType === 'payment' ? '/transactions/payment' : '/transactions/renewal';
    const requestData = {
        subscriber_id: parseInt(subscriberId, 10),
        amount: parseInt(amount, 10),
        promise_date: promiseDate,
        is_cash: isCash
    };
    try {
        const data = await apiCall(endpoint, 'POST', requestData);
        if (data && data.status === 'success') {
            actionModal.hide();
            loadSubscribers();
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
